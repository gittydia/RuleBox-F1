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
import torch

if not torch.cuda.is_available():
    print("Warning: CUDA is not available. PyTorch will use the CPU backend.")

class RuleBoxF1Processor:
    def __init__(self, mongodb_uri='mongodb://localhost:27017/', openrouter_api_key=''):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client['rulebox_f1_database']
        if openrouter_api_key:
            try:
                self.ai_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_api_key,
                )
            except Exception as e:
                print(f"Error initializing OpenAI client in datacollect: {e}")
                self.ai_client = None
        else:
            self.ai_client = None
            print("Warning: No OpenRouter API key provided. AI features will be disabled.")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')
        self._create_indexes()

    def _create_indexes(self):
        try:
            self.db.rules.create_index([
                ("title", "text"),
                ("content", "text"),
                ("metadata.keywords", "text")
            ])
            self.db.rules.create_index("category")
            self.db.rules.create_index("rule_id")
            self.db.rules.create_index("metadata.effective_date")
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Index creation warning: {e}")

    def download_regulations(self):
        urls = {
            'technical': 'https://www.fia.com/sites/default/files/2025_formula_1_technical_regulations_-_iss_1.pdf',
            'sporting': 'https://www.fia.com/sites/default/files/2025_formula_1_sporting_regulations_-_iss_5.pdf',
            'financial': 'https://www.fia.com/sites/default/files/2025_formula_1_financial_regulations_-_iss_3.pdf'
        }
        downloaded_files = []
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
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_pages = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
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
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,():\-–—/\[\]{}"]', '', text)
        text = text.replace('fi', 'fi').replace('fl', 'fl')
        return text.strip()

    def parse_regulations_structure(self, text_pages, regulation_type):
        rules_data = []
        current_article = None
        current_content = []
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
                article_match = None
                for pattern in article_patterns:
                    article_match = re.match(pattern, line, re.IGNORECASE)
                    if article_match:
                        break
                if article_match:
                    if current_article:
                        rules_data.append(self._create_rule_object(
                            current_article,
                            '\n'.join(current_content),
                            regulation_type,
                            page_info['page_number']
                        ))
                    current_article = {
                        'number': article_match.group(1),
                        'title': article_match.group(2).strip()
                    }
                    current_content = []
                else:
                    if current_article:
                        current_content.append(line)
        if current_article:
            rules_data.append(self._create_rule_object(
                current_article,
                '\n'.join(current_content),
                regulation_type,
                text_pages[-1]['page_number'] if text_pages else 1
            ))
        return rules_data

    def _create_rule_object(self, article_info, content, regulation_type, page_number):
        category_prefixes = {
            'technical': 'TR',
            'sporting': 'SR',
            'financial': 'FR'
        }
        prefix = category_prefixes.get(regulation_type, 'GR')
        rule_id = f"{prefix}-2025-{article_info['number'].replace('.', '-')}"
        clean_content = self.clean_and_structure_text(content)
        embedding_text = f"{article_info['title']} {clean_content}"
        embedding = self.embedding_model.encode(embedding_text).tolist()
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
            'related_articles': [],
            'penalties': self._extract_penalties(clean_content),
            'diagrams': [],
            'examples': self._extract_examples(clean_content)
        }
        return rule

    def _extract_keywords(self, text):
        f1_terms = {
            'aerodynamic', 'downforce', 'drs', 'power unit', 'ers', 'kers',
            'qualifying', 'grid', 'safety car', 'pit stop', 'penalty',
            'championship', 'points', 'constructor', 'driver', 'team',
            'engine', 'gearbox', 'suspension', 'brake', 'tire', 'tyre',
            'fuel', 'weight', 'ballast', 'scrutineering', 'parc ferme'
        }
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}
        for word in words:
            if word in f1_terms or len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:10]]

    def _determine_subcategory(self, title, content, regulation_type):
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
        examples = []
        example_patterns = [
            r'for example[,:]?\s*([^.]+\.)',
            r'such as[,:]?\s*([^.]+\.)',
            r'including[,:]?\s*([^.]+\.)'
        ]
        for pattern in example_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                examples.append(match.group(1).strip())
        return examples[:3]

    def store_in_database(self, rules_data):
        try:
            # Don't clear all rules, just update/insert new ones
            if rules_data:
                # Insert rules one by one to handle duplicates
                inserted_count = 0
                for rule in rules_data:
                    try:
                        # Update if exists, insert if not
                        result = self.db.rules.replace_one(
                            {'rule_id': rule['rule_id']},
                            rule,
                            upsert=True
                        )
                        inserted_count += 1
                    except Exception as e:
                        print(f"Error inserting rule {rule.get('rule_id', 'unknown')}: {e}")
                        continue
                
                print(f"✓ Stored {inserted_count} rules in database")
                self._create_summary_stats(rules_data)
                return inserted_count
            else:
                print("No rules to store")
                return 0
        except Exception as e:
            print(f"Error storing rules in database: {e}")
            return 0

    def _create_summary_stats(self, rules_data):
        stats = {
            'total_rules': len(rules_data),
            'categories': {},
            'subcategories': {},
            'last_updated': datetime.now().isoformat(),
            'regulation_year': 2025
        }
        for rule in rules_data:
            category = rule['category']
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            subcategory = rule['subcategory']
            stats['subcategories'][subcategory] = stats['subcategories'].get(subcategory, 0) + 1
        self.db.summary.replace_one(
            {'type': 'rules_summary'},
            stats,
            upsert=True
        )

    def semantic_search(self, query, limit=10, category_filter=None):
        try:
            query_embedding = self.embedding_model.encode(query)
            query_embedding = np.array(query_embedding).reshape(1, -1)
            
            mongo_filter = {}
            if category_filter:
                mongo_filter['category'] = category_filter
            rules = list(self.db.rules.find(mongo_filter))
            if not rules:
                print("Warning: No rules found in the database.")
                return []
            similarities = []
            for rule in rules:
                if 'metadata' in rule and 'embedding' in rule['metadata']:
                    rule_embedding = np.array(rule['metadata']['embedding']).reshape(1, -1)
                    similarity = cosine_similarity(query_embedding, rule_embedding)[0][0]
                    similarities.append({
                        'rule': rule,
                        'similarity': float(similarity)
                    })
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return [item['rule'] for item in similarities[:limit]]
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    def text_search(self, query, category_filter=None):
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

    def process_documents(self):
        """Process all PDF files from the raw_data folder"""
        raw_data_folder = os.path.join(os.path.dirname(__file__), 'raw_data')
        processed_files = []
        
        print(f"Looking for raw_data folder at: {raw_data_folder}")
        
        if not os.path.exists(raw_data_folder):
            return {"error": f"raw_data folder not found at {raw_data_folder}"}
        
        pdf_files = [f for f in os.listdir(raw_data_folder) if f.endswith('.pdf')]
        
        if not pdf_files:
            return {"error": "No PDF files found in raw_data folder", "folder_contents": os.listdir(raw_data_folder)}
        
        print(f"Found {len(pdf_files)} PDF files: {pdf_files}")
        
        all_rules_data = []  # Collect all rules from all files
        
        for pdf_file in pdf_files:
            try:
                pdf_path = os.path.join(raw_data_folder, pdf_file)
                print(f"Processing {pdf_file}...")
                
                # Determine regulation type from filename
                if 'technical' in pdf_file.lower():
                    regulation_type = 'technical'
                elif 'sporting' in pdf_file.lower():
                    regulation_type = 'sporting'
                elif 'financial' in pdf_file.lower():
                    regulation_type = 'financial'
                else:
                    regulation_type = 'general'
                
                # Extract text from PDF
                text_pages = self.extract_text_from_pdf(pdf_path)
                
                if not text_pages:
                    processed_files.append({
                        'file': pdf_file,
                        'error': 'No text extracted from PDF',
                        'status': 'error'
                    })
                    continue
                
                # Parse and structure the text
                rules_data = self.parse_regulations_structure(text_pages, regulation_type)
                
                if not rules_data:
                    processed_files.append({
                        'file': pdf_file,
                        'error': 'No rules parsed from PDF',
                        'status': 'error'
                    })
                    continue
                
                # Add to all rules data
                all_rules_data.extend(rules_data)
                
                processed_files.append({
                    'file': pdf_file,
                    'regulation_type': regulation_type,
                    'pages_processed': len(text_pages),
                    'rules_processed': len(rules_data),
                    'status': 'success'
                })
                
                print(f"✓ Processed {pdf_file}: {len(rules_data)} rules extracted")
                
            except Exception as e:
                print(f"✗ Error processing {pdf_file}: {str(e)}")
                processed_files.append({
                    'file': pdf_file,
                    'error': str(e),
                    'status': 'error'
                })
        
        # Store all rules at once
        if all_rules_data:
            try:
                stored_count = self.store_in_database(all_rules_data)
                print(f"✓ Stored {stored_count} total rules in database")
            except Exception as e:
                print(f"✗ Error storing rules in database: {str(e)}")
                return {
                    'error': f'Failed to store rules: {str(e)}',
                    'processed_files': processed_files
                }
        
        return {
            'processed_files': processed_files,
            'total_files': len(pdf_files),
            'successful': len([f for f in processed_files if f['status'] == 'success']),
            'total_rules_stored': len(all_rules_data)
        }

    def test_embedding_model(self):
        """Test if the embedding model is working correctly"""
        try:
            test_text = "This is a test sentence for the embedding model."
            embedding = self.embedding_model.encode(test_text)
            print(f"✓ Embedding model working. Embedding shape: {embedding.shape}")
            return True
        except Exception as e:
            print(f"✗ Embedding model error: {e}")
            return False

    # ...existing code...