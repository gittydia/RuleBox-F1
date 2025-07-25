export default async function handler(req, res) {
  if (req.method === "POST") {
    const { query } = req.body;

    try {
      const backendUrl = process.env.NODE_ENV === 'production' 
        ? '' // Use relative URL in production
        : "http://localhost:8000";
      
      const response = await fetch(`${backendUrl}/api/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (response.ok) {
        const data = await response.json();
        res.status(200).json({ results: data });
      } else {
        res.status(response.status).json({ error: "Search failed." });
      }
    } catch {
      res.status(500).json({ error: "Internal server error." });
    }
  } else {
    res.setHeader("Allow", ["POST"]);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
