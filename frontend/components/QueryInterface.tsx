"use client";

import { useState } from "react";

// Define the type for the result objects
interface Result {
  title: string;
  rule_id: string;
  article_number: string;
  category: string;
  subcategory: string;
  page_number: number;
  content: string; // Added content field
  metadata?: {
    effective_date?: string;
    last_modified?: string;
    keywords?: string[];
  };
}

const QueryInterface = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[]>([]); // Use the Result type here
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log("Query sent:", query); // Log the query being sent

      const response = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (response.ok) {
        const data = await response.json();

        // Handle response structure - backend returns {results: [...]}
        if (data.results && Array.isArray(data.results)) {
          setResults(data.results);
        } else {
          console.error("Unexpected response format:", data);
          setResults([]); // Reset results to an empty array if the response is invalid
        }
      } else {
        const errorText = await response.text();
        console.error("Search failed with status:", response.status, errorText);
        setError(`Search failed (${response.status}): ${errorText || 'Unknown error'}`);
        setResults([]);
      }
    } catch (error) {
      console.error("Error fetching search results:", error);
      setError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setResults([]); // Reset results to an empty array in case of an error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gradient">
          Search F1 Regulations
        </h1>
        
        <div className="card mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (error) setError(null); // Clear error when user starts typing
              }}
              placeholder="Search for F1 rules, regulations, or technical specifications..."
              className="form-input flex-1"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              className="racing-button px-8 py-3"
              disabled={!query.trim() || loading}
            >
              {loading ? '� Searching...' : '�🔍 Search'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <div className="flex items-center">
              <span className="text-xl mr-2">⚠️</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        {results.length > 0 && (
          <div className="mb-4">
            <h2 className="text-2xl font-semibold mb-6 text-[#ff1801]">
              Found {results.length} result{results.length !== 1 ? 's' : ''}
            </h2>
          </div>
        )}

        <div className="space-y-6">
          {results.map((result, index) => (
            <div key={index} className="search-result">
              <h3>{result.title}</h3>
              
              <div className="metadata">
                <div className="metadata-item">
                  <strong>Rule ID:</strong> {result.rule_id}
                </div>
                <div className="metadata-item">
                  <strong>Article:</strong> {result.article_number}
                </div>
                <div className="metadata-item">
                  <strong>Category:</strong> {result.category}
                </div>
                <div className="metadata-item">
                  <strong>Subcategory:</strong> {result.subcategory}
                </div>
                <div className="metadata-item">
                  <strong>Page:</strong> {result.page_number}
                </div>
                {result.metadata?.effective_date && (
                  <div className="metadata-item">
                    <strong>Effective:</strong> {result.metadata.effective_date}
                  </div>
                )}
                {result.metadata?.last_modified && (
                  <div className="metadata-item">
                    <strong>Modified:</strong> {result.metadata.last_modified}
                  </div>
                )}
              </div>
              {result.content && result.content.trim() && (
                <div className="content">
                  {result.content}
                </div>
              )}
            </div>
          ))}
        </div>

        {results.length === 0 && query && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-300">No results found</h3>
            <p className="text-gray-400">Try different keywords or check your spelling</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryInterface;
