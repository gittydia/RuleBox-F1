import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    message: 'Frontend is working',
    timestamp: new Date().toISOString(),
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'not set',
    nodeEnv: process.env.NODE_ENV || 'not set'
  });
}
