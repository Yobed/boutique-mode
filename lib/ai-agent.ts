import { Article, ChatMessage } from './types';
import { getArticles, searchArticles } from './supabase';

const GROQ_API_KEY = process.env.GROQ_API_KEY || '';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';

export async function processStylistChat(
  history: ChatMessage[],
  userMessage: string
): Promise<{ text: string; articles?: Article[]; suggestedActions?: string[] }> {
  const articlesCatalog = await getArticles();

  // 1. Recherche d'articles pertinents dans le catalogue
  const relevantArticles = findRelevantArticles(userMessage, articlesCatalog);

  // 2. Si clé Groq disponible -> Utilisation de Llama 3.3 70B (ultra-rapide)
  if (GROQ_API_KEY) {
    try {
      const response = await callGroqAPI(history, userMessage, articlesCatalog, relevantArticles);
      return {
        text: response,
        articles: relevantArticles.slice(0, 3),
        suggestedActions: generateSuggestions(relevantArticles),
      };
    } catch (err) {
      console.warn('Groq API failed, falling back:', err);
    }
  }

  // 3. Si clé Gemini disponible -> Utilisation de Gemini Flash
  if (GEMINI_API_KEY) {
    try {
      const response = await callGeminiAPI(history, userMessage, articlesCatalog, relevantArticles);
      return {
        text: response,
        articles: relevantArticles.slice(0, 3),
        suggestedActions: generateSuggestions(relevantArticles),
      };
    } catch (err) {
      console.warn('Gemini API failed, falling back:', err);
    }
  }

  // 4. Moteur Styliste Local Intégré (0 configuration requise, fonctionne immédiatement)
  return fallbackStylistEngine(userMessage, relevantArticles);
}

function findRelevantArticles(message: string, catalog: Article[]): Article[] {
  const lower = message.toLowerCase();

  // Recherche par catégorie
  if (lower.includes('robe')) return catalog.filter(a => a.categorie === 'robes');
  if (lower.includes('costume') || lower.includes('veston')) return catalog.filter(a => a.categorie === 'costumes');
  if (lower.includes('chemise') || lower.includes('wax')) return catalog.filter(a => a.categorie === 'chemises');
  if (lower.includes('pantalon')) return catalog.filter(a => a.categorie === 'pantalons');
  if (lower.includes('chaussure') || lower.includes('escarpin') || lower.includes('mocassin')) return catalog.filter(a => a.categorie === 'chaussures');
  if (lower.includes('sac')) return catalog.filter(a => a.categorie === 'sacs');
  if (lower.includes('accessoire') || lower.includes('bijou') || lower.includes('collier') || lower.includes('lunette')) return catalog.filter(a => a.categorie === 'accessoires');

  // Recherche par genre
  if (lower.includes('homme') || lower.includes('monsieur')) return catalog.filter(a => a.genre === 'homme');
  if (lower.includes('femme') || lower.includes('dame')) return catalog.filter(a => a.genre === 'femme');

  // Recherche par promotion ou coup de coeur
  if (lower.includes('promo') || lower.includes('solde') || lower.includes('rabais')) {
    return catalog.filter(a => !!a.prix_promo);
  }

  // Si rien de spécifique, renvoyer les articles vedettes
  return catalog.filter(a => a.vedette);
}

async function callGroqAPI(
  history: ChatMessage[],
  userMessage: string,
  catalog: Article[],
  relevantArticles: Article[]
): Promise<string> {
  const catalogContext = catalog.map(a =>
    `- ${a.nom} (${a.categorie}, ${a.genre}) : ${a.prix.toLocaleString('fr-FR')} FCFA${a.prix_promo ? ` (Promo: ${a.prix_promo.toLocaleString('fr-FR')} FCFA)` : ''}. Tailles: ${a.tailles.join(', ')}. Couleurs: ${a.couleurs.join(', ')}.`
  ).join('\n');

  const systemPrompt = `Tu es Sophia, première d'atelier et styliste personnelle de la prestigieuse maison de prêt-à-porter "ELSI" à Abidjan (Côte d'Ivoire).
Ton ton est chaleureux, raffiné, digne des plus grands ateliers de couture tout en restant accessible et attentif. Tu t'exprimes dans un français ivoirien distingué.
Tu conseilles avec expertise les clients sur leurs tenues selon l'occasion (gala au Sofitel Ivoire, mariage, rendez-vous d'affaires au Plateau, cocktail à Cocody ou détente à Assinie).
Tu connais parfaitement le catalogue ci-dessous et ses disponibilités en stock.
Tu réponds de façon concise (2 à 4 phrases maximum) pour garder la conversation fluide.
Si le client veut commander, rassure-le sur le paiement sécurisé à la réception (espèces, Wave, Orange Money ou MTN MoMo), la livraison sous housse sous 24 h et l'échange de taille garanti sous 48 h à domicile. Demande-lui sa taille, sa commune de livraison et son contact WhatsApp.

Catalogue actuel de la maison :
${catalogContext}`;

  const messages = [
    { role: 'system', content: systemPrompt },
    ...history.slice(-6).map(m => ({ role: m.role, content: m.content })),
    { role: 'user', content: userMessage },
  ];

  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${GROQ_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'llama-3.3-70b-versatile',
      messages,
      temperature: 0.7,
      max_tokens: 300,
    }),
  });

  const data = await res.json();
  return data.choices?.[0]?.message?.content || 'Bienvenue ! Comment puis-je sublimer votre style aujourd\'hui ?';
}

async function callGeminiAPI(
  history: ChatMessage[],
  userMessage: string,
  catalog: Article[],
  relevantArticles: Article[]
): Promise<string> {
  const catalogContext = catalog.map(a =>
    `- ${a.nom} : ${a.prix.toLocaleString('fr-FR')} FCFA (Tailles: ${a.tailles.join(', ')})`
  ).join('\n');

  const systemInstruction = `Tu es Sophia, première d'atelier et styliste personnelle chez ELSI à Abidjan. Conseille le client avec raffinement, amabilité et expertise de coupe. Réponds en 2 à 3 phrases claires. Catalogue : ${catalogContext}`;

  const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [
        { role: 'user', parts: [{ text: `${systemInstruction}\n\nClient : ${userMessage}` }] }
      ]
    }),
  });

  const data = await res.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text || 'Avec plaisir ! Quel style ou tenue recherchez-vous ?';
}

function fallbackStylistEngine(
  message: string,
  articles: Article[]
): { text: string; articles: Article[]; suggestedActions: string[] } {
  const lower = message.toLowerCase();

  if (lower.includes('bonjour') || lower.includes('salut') || lower.includes('hello') || lower.includes('bonsoir')) {
    return {
      text: 'Bonjour et bienvenue chez ELSI. Je suis Sophia, votre styliste d\'atelier. Pour quelle occasion recherchez-vous une création aujourd\'hui ? (Gala, mariage, d\'affaires ou cocktail)',
      articles: articles.slice(0, 2),
      suggestedActions: ['Robes de soirée', 'Costumes homme', 'Créations lin & wax', 'Nouveautés'],
    };
  }

  if (lower.includes('robe')) {
    return {
      text: 'Exquis choix ! Nous avons de magnifiques robes comme notre Robe Soirée Émeraude Satinée ou notre Robe Cocktail Cache-Cœur. En quelle taille préférez-vous votre modèle ?',
      articles: articles.slice(0, 3),
      suggestedActions: ['Taille S', 'Taille M', 'Taille L', 'Commander sur WhatsApp'],
    };
  }

  if (lower.includes('costume') || lower.includes('homme')) {
    return {
      text: 'Pour homme, notre Costume Slim Fit Bleu Nuit et nos créations en Lin & Wax rencontrent un immense succès ! Ils allient prestige et confort pour toutes vos cérémonies.',
      articles: articles.slice(0, 2),
      suggestedActions: ['Voir les costumes', 'Guide des tailles', 'Commander'],
    };
  }

  if (lower.includes('prix') || lower.includes('combien') || lower.includes('tarif')) {
    return {
      text: 'Nos prix commencent dès 16 000 FCFA pour nos polos signatures et jusqu\'à 85 000 FCFA pour nos costumes sur mesure. La livraison est rapide sur tout Abidjan et à l\'intérieur !',
      articles: articles.slice(0, 2),
      suggestedActions: ['Voir les promotions', 'Passer commande'],
    };
  }

  if (lower.includes('commander') || lower.includes('acheter') || lower.includes('livraison')) {
    return {
      text: 'Parfait ! Vous pouvez ajouter votre article au panier et valider en 1 clic via WhatsApp, ou me donner directement votre taille et commune de livraison pour enregistrer votre commande.',
      articles: articles.slice(0, 2),
      suggestedActions: ['Ouvrir le panier', 'Payer par Wave / MoMo', 'Discuter sur WhatsApp'],
    };
  }

  return {
    text: `Voici une sélection raffinée de notre collection ! N'hésitez pas à me préciser votre taille ou la couleur souhaitée pour un conseil sur mesure.`,
    articles: articles.slice(0, 3),
    suggestedActions: ['Robes', 'Costumes', 'Chaussures & Sacs', 'Promotions'],
  };
}

function generateSuggestions(articles: Article[]): string[] {
  const suggestions = ['Guide des tailles', 'Commander via WhatsApp'];
  if (articles.some(a => a.categorie === 'robes')) suggestions.unshift('Voir les robes');
  if (articles.some(a => a.categorie === 'costumes')) suggestions.unshift('Costumes sur mesure');
  if (articles.some(a => a.prix_promo)) suggestions.unshift('Offres en promo');
  return suggestions.slice(0, 4);
}
