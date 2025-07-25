"use client";

import { useState } from "react";

interface SearchResult {
  title: string;
  content: string;
}

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.results);
      } else {
        console.error("Search failed.");
      }
    } catch (error) {
      console.error("Error during search:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <h1>F1 Regulation Search</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your query..."
        className="search-input"
      />
      <button
        onClick={handleSearch}
        disabled={loading}
        className="search-button"
      >
        {loading ? "Searching..." : "Search"}
      </button>

      <div className="results">
        {results.length > 0 ? (
          <ul>
            {results.map((result, index) => (
              <li key={index}>
                <h3>{result.title}</h3>
                <p>{result.content}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No results found.</p>
        )}
      </div>

      <style jsx>{`
        .search-container {
          max-width: 600px;
          margin: 0 auto;
          text-align: center;
          padding: 20px;
        }
        .search-input {
          width: 100%;
          padding: 10px;
          margin-bottom: 10px;
          border: 1px solid #ccc;
          border-radius: 4px;
        }
        .search-button {
          padding: 10px 20px;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        .search-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        .results {
          margin-top: 20px;
        }
        .results ul {
          list-style: none;
          padding: 0;
        }
        .results li {
          margin-bottom: 20px;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
}
