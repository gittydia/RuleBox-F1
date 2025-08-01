import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    // Your FastAPI backend URL
    const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
        
    const response = await fetch(`${BACKEND_URL}/api/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend search failed:', response.status, errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Search API error:', error);
    
    // Check if it's a connection error
    if (error instanceof Error && 'cause' in error) {
      const cause = error.cause as { code?: string };
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
