import { NextRequest, NextResponse } from 'next/server';
import { processStylistChat } from '@/lib/ai-agent';

// No hard-coded fallbacks: without these env vars the webhook stays disabled.
const WHATSAPP_GATEWAY_URL = process.env.WHATSAPP_GATEWAY_URL;
const WHATSAPP_API_KEY = process.env.WHATSAPP_API_KEY;
const VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN;
const WEBHOOK_SECRET = process.env.WHATSAPP_WEBHOOK_SECRET;

// 1. Webhook Verification (pour Meta Cloud API standard)
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const mode = searchParams.get('hub.mode');
  const token = searchParams.get('hub.verify_token');
  const challenge = searchParams.get('hub.challenge');

  if (VERIFY_TOKEN && mode === 'subscribe' && token === VERIFY_TOKEN) {
    return new Response(challenge, { status: 200 });
  }

  return NextResponse.json({ status: 'ok', service: 'Boutique WhatsApp Webhook' });
}

// 2. Ingestion des messages entrants (WhatsApp Gateway Baileys / Meta)
export async function POST(req: NextRequest) {
  // The gateway must prove it is ours, otherwise anyone could make the shop's number message arbitrary people.
  if (!WEBHOOK_SECRET || !WHATSAPP_API_KEY || !WHATSAPP_GATEWAY_URL) {
    return NextResponse.json({ error: 'Webhook non configuré' }, { status: 503 });
  }
  if (req.headers.get('x-webhook-secret') !== WEBHOOK_SECRET) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 });
  }
  try {
    const payload = await req.json();

    // Extraction du message et du destinataire
    let sender = '';
    let text = '';
    let fromMe = false;

    // Format Baileys Gateway
    if (payload.data?.from || payload.from) {
      sender = (payload.data?.from || payload.from || '').replace(/\D/g, '');
      text = payload.data?.body || payload.text || payload.data?.message?.conversation || '';
      fromMe = !!payload.data?.fromMe;
    }
    // Format Meta Cloud API
    else if (payload.entry?.[0]?.changes?.[0]?.value?.messages?.[0]) {
      const msg = payload.entry[0].changes[0].value.messages[0];
      sender = msg.from;
      text = msg.text?.body || '';
    }

    // Ignore si c'est notre propre message ou vide
    if (fromMe || !sender || !text) {
      return NextResponse.json({ success: true, ignored: true });
    }

    console.log(`💬 Message WhatsApp reçu de +${sender}: "${text}"`);

    // Traitement par notre Styliste IA Sophia
    const aiResponse = await processStylistChat([], text);

    let replyMessage = aiResponse.text;

    // Si des articles sont recommandés, on ajoute un joli récapitulatif
    if (aiResponse.articles && aiResponse.articles.length > 0) {
      replyMessage += '\n\n✨ *Nos Recommandations pour vous :*\n';
      aiResponse.articles.slice(0, 2).forEach((art) => {
        replyMessage += `\n👗 *${art.nom}*\n💰 Prix : *${(art.prix_promo || art.prix).toLocaleString('fr-FR')} FCFA*\n📏 Tailles : ${art.tailles.join(', ')}\n📸 Photo : ${art.photos[0]}\n`;
      });
      replyMessage += '\n👉 Tapez *COMMANDER* avec votre taille et commune pour valider !';
    }

    // Renvoi du message au client via la passerelle WhatsApp
    if (WHATSAPP_GATEWAY_URL) {
      fetch(`${WHATSAPP_GATEWAY_URL}/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${WHATSAPP_API_KEY}`,
        },
        body: JSON.stringify({
          to: sender,
          text: replyMessage,
        }),
      }).catch((e) => console.error('Erreur relai passerelle WhatsApp:', e));
    }

    return NextResponse.json({ success: true, replyGenerated: true });
  } catch (err: any) {
    console.error('Erreur webhook WhatsApp:', err);
    return NextResponse.json({ success: false, error: err.message }, { status: 500 });
  }
}
