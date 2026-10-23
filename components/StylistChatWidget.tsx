'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, X, Send, ShoppingBag, MessageCircle, Bot } from 'lucide-react';
import { Article, ChatMessage } from '@/lib/types';

interface StylistChatWidgetProps {
  isOpen: boolean;
  onToggle: () => void;
  onAddToCart: (article: Article, taille: string, couleur: string) => void;
}

export default function StylistChatWidget({ isOpen, onToggle, onAddToCart }: StylistChatWidgetProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Bonjour et bienvenue chez Boutique en Ligne ! ✨ Je suis Sophia, votre styliste personnelle. Pour quelle occasion recherchez-vous une tenue aujourd\'hui ?',
      suggestedActions: ['Robes de soirée', 'Costumes homme', 'Ensembles lin & wax', 'Promotions du moment'],
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: messages,
        }),
      });

      const data = await res.json();

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.text || 'Je suis à votre entière disposition pour vous conseiller !',
        articles: data.articles || [],
        suggestedActions: data.suggestedActions || [],
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: 'Oups, une petite coupure de réseau est survenue. N\'hésitez pas à nous écrire directement sur WhatsApp !',
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Launcher Button */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-purple-700 via-pink-600 to-amber-500 text-white font-bold text-sm shadow-2xl shadow-purple-600/40 hover:scale-105 transition-all duration-200 ease-premium motion-press group"
          title="Parler à notre styliste IA"
        >
          <div className="relative">
            <Sparkles className="w-5 h-5 text-amber-200 animate-spin" style={{ animationDuration: '4s' }} />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-dark-950 animate-pulse-subtle" />
          </div>
          <span className="tracking-wide">Styliste IA</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-[92vw] sm:w-[420px] h-[580px] max-h-[85vh] bg-dark-950 border border-white/15 rounded-3xl shadow-2xl flex flex-col overflow-hidden text-white backdrop-blur-xl animate-scale-in">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-purple-950 via-dark-900 to-dark-950 border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold animate-pulse-subtle">
                  <Bot className="w-5 h-5" />
                </div>
                <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 rounded-full border-2 border-dark-950" />
              </div>
              <div>
                <h3 className="font-serif font-bold text-sm text-white flex items-center gap-1.5">
                  Sophia • Styliste IA
                  <Sparkles className="w-3.5 h-3.5 text-gold-400" />
                </h3>
                <span className="text-[11px] text-emerald-400 font-medium">
                  En ligne • Vendeuse & Conseillère
                </span>
              </div>
            </div>
            <button
              onClick={onToggle}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 transition-colors duration-150 ease-premium motion-press"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Flow */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.role === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-gold-500 text-dark-950 font-medium rounded-br-none shadow-md'
                      : 'bg-dark-900 border border-white/10 text-zinc-200 rounded-bl-none'
                  }`}
                >
                  {msg.content}
                </div>

                {/* Embedded Recommended Articles */}
                {msg.articles && msg.articles.length > 0 && (
                  <div className="mt-2.5 space-y-2 w-full max-w-[90%]">
                    {msg.articles.map((art) => (
                      <div
                        key={art.id}
                        className="flex gap-2.5 p-2 rounded-xl bg-white/5 border border-white/10 hover:border-gold-500/40 transition-colors"
                      >
                        <img
                          src={art.photos[0]}
                          alt={art.nom}
                          className="w-14 h-18 object-cover rounded-lg bg-zinc-800 flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0 flex flex-col justify-between">
                          <div>
                            <h4 className="font-serif font-bold text-white text-[11px] truncate">
                              {art.nom}
                            </h4>
                            <div className="text-gold-400 font-bold text-xs mt-0.5">
                              {(art.prix_promo || art.prix).toLocaleString('fr-FR')} FCFA
                            </div>
                            <div className="text-[10px] text-zinc-400">
                              Tailles : {art.tailles.join(', ')}
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => onAddToCart(art, art.tailles[0], art.couleurs[0])}
                            className="inline-flex items-center gap-1 self-start px-2.5 py-1 rounded-md bg-gold-500 text-dark-950 text-[10px] font-bold hover:bg-gold-400 transition-colors duration-150 ease-premium motion-press"
                          >
                            <ShoppingBag className="w-3 h-3" />
                            <span>Ajouter</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Suggested Action Chips */}
                {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {msg.suggestedActions.map((sug, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleSend(sug)}
                        className="px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-zinc-300 hover:text-white hover:border-gold-400/50 hover:bg-white/10 text-[11px] transition-all duration-150 ease-premium motion-press"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-zinc-400 text-xs py-2">
                <div className="w-2 h-2 rounded-full bg-gold-400 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-gold-400 animate-bounce" style={{ animationDelay: '0.2s' }} />
                <div className="w-2 h-2 rounded-full bg-gold-400 animate-bounce" style={{ animationDelay: '0.4s' }} />
                <span>Sophia réfléchit...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-dark-900 border-t border-white/10 flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Écrivez votre message à Sophia..."
              className="flex-1 bg-dark-950 border border-white/10 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-gold-500"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2.5 rounded-xl bg-gold-500 hover:bg-gold-400 text-dark-950 disabled:opacity-40 transition-all duration-150 ease-premium motion-press font-bold"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
