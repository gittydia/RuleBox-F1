import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { query, conversation_id } = await request.json();

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    // Your FastAPI backend URL
    const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
    
    console.log(`Forwarding AI query request to: ${BACKEND_URL}/api/ai-query`);
    console.log(`Query: ${query}`);
    console.log(`Conversation ID: ${conversation_id}`);
    
    const response = await fetch(`${BACKEND_URL}/api/ai-query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        query,
        conversation_id 
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend AI query failed:', response.status, errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Backend AI response:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('AI Query API error:', error);
    
    // Check if it's a connection error
    if (error instanceof Error && 'cause' in error) {
      const cause = error.cause as any;
      if (cause?.code === 'ECONNREFUSED') {
        return NextResponse.json(
          { 
            error: 'Backend service is not running. Please start your Python backend server.',
            details: 'Make sure your app.py is running on port 8000.'
          },
          { status: 503 }
        );
      }
    }
    
    return NextResponse.json(
      { error: 'Failed to connect to backend service' },
      { status: 500 }
    );
  }
}
