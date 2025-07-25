export default async function handler(req, res) {
  if (req.method === "POST") {
    const { query, conversationId } = req.body;

    // In production, use relative URL; in development, use localhost
    const apiUrl = process.env.NODE_ENV === 'production' 
      ? '/api/ai-query'  // This will route to your Python backend
      : 'http://localhost:8000/api/ai-query';

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query, conversation_id: conversationId }),
      });

      if (response.ok) {
        const data = await response.json();
        res.status(200).json(data);
      } else {
        const errorData = await response.json();
        res.status(response.status).json(errorData);
      }
    } catch (error) {
      console.error("AI Query API error:", error);
      res.status(500).json({ detail: "Internal server error." });
    }
  } else {
    res.setHeader("Allow", ["POST"]);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
