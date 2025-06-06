import PyPDF2
import re
import requests
import os
from datetime import datetime
from pymongo import MongoClient
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Remove TensorFlow-specific environment variable
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Ensure PyTorch is used as the backend
import torch
if not torch.cuda.is_available():
    print("Warning: CUDA is not available. PyTorch will use the CPU backend.")

class RuleBoxF1Processor:
    def __init__(self, mongodb_uri='mongodb://localhost:27017/', openrouter_api_key='OPENROUTER_API_KEY'):
        # Initialize MongoDB connection
        self.client = MongoClient(mongodb_uri)
        self.db = self.client['rulebox_f1_database']
        
        # Initialize OpenRouter/DeepSeek AI client
        if openrouter_api_key:
            self.ai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_api_key,
            )
        else:
            self.ai_client = None
            print("Warning: No OpenRouter API key provided. AI features will be disabled.")

        # Initialize vector embedding model for semantic search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')
        
        # Create indexes for better search performance
        self._create_indexes()

    def _create_indexes(self):
        """Create MongoDB indexes for better search performance"""
        try:
            # Text indexes for full-text search
            self.db.rules.create_index([
                ("title", "text"),
                ("content", "text"),
                ("metadata.keywords", "text")
            ])
            
            # Regular indexes for filtering
            self.db.rules.create_index("category")
            self.db.rules.create_index("rule_id")
            self.db.rules.create_index("metadata.effective_date")
            
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Index creation warning: {e}")

    def download_regulations(self):
        """Download the latest F1 regulations from FIA website"""
        # Updated URLs for 2025 regulations
        urls = {
            'technical': 'https://www.fia.com/sites/default/files/2025_formula_1_technical_regulations_-_iss_1.pdf',
            'sporting': 'https://www.fia.com/sites/default/files/2025_formula_1_sporting_regulations_-_iss_5.pdf',
            'financial': 'https://www.fia.com/sites/default/files/2025_formula_1_financial_regulations_-_iss_3.pdf'
        }
        
        downloaded_files = []
        
        # Create raw_data directory
        os.makedirs('raw_data', exist_ok=True)
        
        for reg_type, url in urls.items():
            try:
                print(f"Downloading {reg_type} regulations...")
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    filename = f'raw_data/{reg_type}_regulations_2025.pdf'
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    downloaded_files.append((filename, reg_type))
                    print(f"✓ Downloaded {reg_type} regulations")
                else:
                    print(f"✗ Failed to download {reg_type} regulations (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"✗ Error downloading {reg_type} regulations: {e}")
        
        return downloaded_files

    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF files with better error handling"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_pages = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():  # Only add non-empty pages
                            text_pages.append({
                                'page_number': page_num + 1,
                                'text': text
                            })
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                
                return text_pages
                
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return []

    def clean_and_structure_text(self, text):
        """Clean and structure extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-printable characters but keep important symbols
        text = re.sub(r'[^\w\s.,():\-–—/\[\]{}"]', '', text)
        
        # Fix common PDF extraction issues
        text = text.replace('fi', 'fi').replace('fl', 'fl')  # Fix ligatures
        
        return text.strip()

    def parse_regulations_structure(self, text_pages, regulation_type):
        """Parse regulation structure with improved article detection"""
        rules_data = []
        current_article = None
        current_content = []
        
        # Enhanced patterns for different regulation types
        article_patterns = [
            r'\bARTICLE\s+(\d+(?:\.\d+)?)\s*[:\-–—]?\s*(.+?)(?=\n|\r|$)',
            r'^(\d+(?:\.\d+)?)\s+(.+?)(?=\n|\r|$)',
            r'\b(\d+(?:\.\d+)?)\s*\.\s*(.+?)(?=\n|\r|$)'
        ]
        
        for page_info in text_pages:
            lines = page_info['text'].split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this line starts a new article
                article_match = None
                for pattern in article_patterns:
                    article_match = re.match(pattern, line, re.IGNORECASE)
                    if article_match:
                        break
                
                if article_match:
                    # Save previous article if exists
                    if current_article:
                        rules_data.append(self._create_rule_object(
                            current_article, 
                            '\n'.join(current_content), 
                            regulation_type,
                            page_info['page_number']
                        ))
                    
                    # Start new article
                    current_article = {
                        'number': article_match.group(1),
                        'title': article_match.group(2).strip()
                    }
                    current_content = []
                else:
                    # Add content to current article
                    if current_article:
                        current_content.append(line)
        
        # Don't forget the last article
        if current_article:
            rules_data.append(self._create_rule_object(
                current_article, 
                '\n'.join(current_content), 
                regulation_type,
                text_pages[-1]['page_number'] if text_pages else 1
            ))
        
        return rules_data

    def _create_rule_object(self, article_info, content, regulation_type, page_number):
        """Create a structured rule object"""
        # Generate rule ID
        category_prefixes = {
            'technical': 'TR',
            'sporting': 'SR', 
            'financial': 'FR'
        }
        
        prefix = category_prefixes.get(regulation_type, 'GR')
        rule_id = f"{prefix}-2025-{article_info['number'].replace('.', '-')}"
        
        # Clean content
        clean_content = self.clean_and_structure_text(content)
        
        # Generate vector embedding
        embedding_text = f"{article_info['title']} {clean_content}"
        embedding = self.embedding_model.encode(embedding_text).tolist()
        
        # Extract keywords
        keywords = self._extract_keywords(embedding_text)
        
        rule = {
            'rule_id': rule_id,
            'article_number': article_info['number'],
            'title': self.clean_and_structure_text(article_info['title']),
            'content': clean_content,
            'category': regulation_type.title(),
            'subcategory': self._determine_subcategory(article_info['title'], clean_content, regulation_type),
            'page_number': page_number,
            'metadata': {
                'effective_date': '2025-01-01',
                'last_modified': datetime.now().isoformat(),
                'keywords': keywords,
                'regulation_year': 2025,
                'content_length': len(clean_content),
                'embedding': embedding
            },
            'related_articles': [],  # Will be populated later
            'penalties': self._extract_penalties(clean_content),
            'diagrams': [],  # Placeholder for future diagram extraction
            'examples': self._extract_examples(clean_content)
        }
        
        return rule

    def _extract_keywords(self, text):
        """Extract relevant keywords from text"""
        # Common F1 terms to prioritize
        f1_terms = {
            'aerodynamic', 'downforce', 'drs', 'power unit', 'ers', 'kers',
            'qualifying', 'grid', 'safety car', 'pit stop', 'penalty',
            'championship', 'points', 'constructor', 'driver', 'team',
            'engine', 'gearbox', 'suspension', 'brake', 'tire', 'tyre',
            'fuel', 'weight', 'ballast', 'scrutineering', 'parc ferme'
        }
        
        # Extract words and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word in f1_terms or len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:10]]

    def _determine_subcategory(self, title, content, regulation_type):
        """Determine subcategory based on content analysis"""
        subcategories = {
            'technical': {
                'power_unit': ['power unit', 'engine', 'ers', 'fuel'],
                'aerodynamics': ['aerodynamic', 'wing', 'bodywork', 'downforce'],
                'chassis': ['chassis', 'monocoque', 'survival cell'],
                'suspension': ['suspension', 'spring', 'damper'],
                'wheels_tires': ['wheel', 'tire', 'tyre', 'rim'],
                'safety': ['safety', 'crash', 'impact', 'halo']
            },
            'sporting': {
                'championship': ['championship', 'points', 'constructor'],
                'race_procedure': ['race', 'start', 'finish', 'grid'],
                'qualifying': ['qualifying', 'practice', 'session'],
                'penalties': ['penalty', 'infringement', 'breach'],
                'pit_stops': ['pit', 'refuel', 'tire change'],
                'safety': ['safety car', 'red flag', 'yellow flag']
            },
            'financial': {
                'cost_cap': ['cost cap', 'budget', 'expenditure'],
                'reporting': ['report', 'submission', 'declaration'],
                'penalties': ['penalty', 'breach', 'sanction'],
                'excluded_costs': ['excluded', 'exemption']
            }
        }
        
        text_combined = f"{title} {content}".lower()
        
        if regulation_type in subcategories:
            for subcat, keywords in subcategories[regulation_type].items():
                if any(keyword in text_combined for keyword in keywords):
                    return subcat
        
        return 'general'

    def _extract_penalties(self, content):
        """Extract penalty information from content"""
        penalties = []
        penalty_patterns = [
            r'(\d+)\s*second[s]?\s*time\s*penalty',
            r'(\d+)\s*place[s]?\s*grid\s*penalty',
            r'drive.through\s*penalty',
            r'stop.and.go\s*penalty',
            r'disqualification',
            r'reprimand'
        ]
        
        for pattern in penalty_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                penalties.append(match.group(0))
        
        return penalties

    def _extract_examples(self, content):
        """Extract examples or specific cases from content"""
        examples = []
        
        # Look for example patterns
        example_patterns = [
            r'for example[,:]?\s*([^.]+\.)',
            r'such as[,:]?\s*([^.]+\.)',
            r'including[,:]?\s*([^.]+\.)'
        ]
        
        for pattern in example_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                examples.append(match.group(1).strip())
        
        return examples[:3]  # Limit to 3 examples

    def store_in_database(self, rules_data):
        """Store all processed rules in MongoDB"""
        try:
            # Clear existing data for fresh import
            self.db.rules.delete_many({})
            
            # Insert new rules
            if rules_data:
                result = self.db.rules.insert_many(rules_data)
                print(f"✓ Stored {len(result.inserted_ids)} rules in database")
                
                # Create summary statistics
                self._create_summary_stats(rules_data)
                
                return len(result.inserted_ids)
            else:
                print("No rules to store")
                return 0
                
        except Exception as e:
            print(f"Error storing rules in database: {e}")
            return 0

    def _create_summary_stats(self, rules_data):
        """Create summary statistics for the database"""
        stats = {
            'total_rules': len(rules_data),
            'categories': {},
            'subcategories': {},
            'last_updated': datetime.now().isoformat(),
            'regulation_year': 2025
        }
        
        for rule in rules_data:
            # Count by category
            category = rule['category']
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Count by subcategory
            subcategory = rule['subcategory']
            stats['subcategories'][subcategory] = stats['subcategories'].get(subcategory, 0) + 1
        
        # Store summary
        self.db.summary.replace_one(
            {'type': 'rules_summary'}, 
            stats, 
            upsert=True
        )

    def semantic_search(self, query, limit=10, category_filter=None):
        """Perform semantic search using vector embeddings"""
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query)
            
            # Build MongoDB filter
            mongo_filter = {}
            if category_filter:
                mongo_filter['category'] = category_filter
            
            # Get all rules (or filtered rules)
            rules = list(self.db.rules.find(mongo_filter))
            
            if not rules:
                return []
            
            # Calculate similarities
            similarities = []
            for rule in rules:
                if 'metadata' in rule and 'embedding' in rule['metadata']:
                    rule_embedding = np.array(rule['metadata']['embedding'])
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [rule_embedding]
                    )[0][0]
                    
                    similarities.append({
                        'rule': rule,
                        'similarity': float(similarity)
                    })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return [item['rule'] for item in similarities[:limit]]
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    def text_search(self, query, category_filter=None):
        """Perform traditional text search"""
        try:
            mongo_filter = {'$text': {'$search': query}}
            
            if category_filter:
                mongo_filter['category'] = category_filter
            
            results = list(self.db.rules.find(
                mongo_filter,
                {'score': {'$meta': 'textScore'}}
            ).sort([('score', {'$meta': 'textScore'})]).limit(20))
            
            return results
            
        except Exception as e:
            print(f"Error in text search: {e}")
            return []

    def get_rule_by_id(self, rule_id):
        """Get a specific rule by ID"""
        return self.db.rules.find_one({'rule_id': rule_id})

    def get_rules_by_category(self, category, limit=50):
        """Get rules by category"""
        return list(self.db.rules.find({'category': category}).limit(limit))

    def process_all_regulations(self):
        """Main processing pipeline"""
        print("🏎️  Starting RuleBox F1 regulation processing...")

        try:
            # Step 1: Use already downloaded regulations
            print("\n📥 Using existing regulations in raw_data folder...")
            regulation_files = {
                'technical': 'raw_data/technical_regulations.pdf',
                'sporting': 'raw_data/sporting_regulations.pdf',
                'financial': 'raw_data/financial_regulations.pdf'
            }

            all_rules = []

            # Step 2: Process each regulation file
            for reg_type, pdf_path in regulation_files.items():
                if not os.path.exists(pdf_path):
                    print(f"⚠️  File not found: {pdf_path}")
                    continue

                print(f"\n📄 Processing {reg_type} regulations...")

                # Extract text
                text_pages = self.extract_text_from_pdf(pdf_path)

                if not text_pages:
                    print(f"⚠️  No text extracted from {pdf_path}")
                    continue

                # Parse regulations
                rules = self.parse_regulations_structure(text_pages, reg_type)
                print(f"✓ Extracted {len(rules)} rules from {reg_type} regulations")

                all_rules.extend(rules)

            # Step 3: Store in database
            print(f"\n💾 Storing {len(all_rules)} rules in database...")
            stored_count = self.store_in_database(all_rules)

            # Step 4: Generate summary
            summary = self.db.summary.find_one({'type': 'rules_summary'})

            print(f"\n🎉 Processing complete!")
            print(f"   📊 Total rules processed: {len(all_rules)}")
            print(f"   💾 Rules stored in database: {stored_count}")

            if summary:
                print(f"   📈 Categories: {summary.get('categories', {})}")

            return {
                "status": "success", 
                "rules_processed": len(all_rules),
                "rules_stored": stored_count,
                "categories": summary.get('categories', {}) if summary else {}
            }

        except Exception as e:
            print(f"❌ Processing error: {e}")
            return {"status": "error", "message": str(e)}

# Usage example and testing
if __name__ == "__main__":
    # Initialize processor
    processor = RuleBoxF1Processor(
        mongodb_uri='mongodb://localhost:27017/', 
        openrouter_api_key="OPENROUTER_API_KEY"  # Replace with your actual key
    )
    
    # Process all regulations
    result = processor.process_all_regulations()
    print(f"\nFinal result: {result}")
    
    # Example searches after processing
    if result["status"] == "success":
        print("\n🔍 Testing search functionality...")
        
        # Test semantic search
        search_results = processor.semantic_search("power unit regulations", limit=3)
        print(f"Semantic search results: {len(search_results)} rules found")
        
        # Test text search
        text_results = processor.text_search("qualifying procedure")
        print(f"Text search results: {len(text_results)} rules found")
        
        # Test AI query (if API key is provided)
        if processor.ai_client:
            ai_response = processor.ai_query("What are the main power unit regulations?")
            print(f"AI response preview: {ai_response[:200]}...")