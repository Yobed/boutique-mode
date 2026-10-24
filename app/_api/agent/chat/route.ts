import { NextRequest, NextResponse } from 'next/server';
import { processStylistChat } from '@/lib/ai-agent';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { message, history } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Le champ message est requis' },
        { status: 400 }
      );
    }

    const result = await processStylistChat(history || [], message);
    return NextResponse.json(result);
  } catch (err: any) {
    console.error('Erreur API /api/agent/chat:', err);
    return NextResponse.json(
      {
        text: 'Bonjour ! Comment puis-je vous aider à choisir la tenue parfaite ?',
        articles: [],
      },
      { status: 200 }
    );
  }
}
