'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMentor } from '@/lib/mentorContext';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

/** Suggested questions shown when no stock context is active */
const DEFAULT_SUGGESTIONS = [
  'Apa itu RSI dan bagaimana cara membacanya?',
  'Jelaskan cara kerja klaster "Buy the Dip"',
  'Bagaimana ATR digunakan untuk menentukan Stop Loss?',
  'Apa perbedaan EMA20 dan EMA50?',
  'Jelaskan strategi Fibonacci Take Profit',
];

/** Cluster-specific suggested questions */
const CLUSTER_SUGGESTIONS = {
  'Beli Saat Turun': [
    'Jelaskan kenapa saham ini masuk klaster Beli Saat Turun?',
    'Kapan waktu terbaik untuk mulai akumulasi saham oversold?',
    'Jelaskan pola reversal yang biasa muncul setelah oversold',
    'Apa itu divergence bullish di RSI?',
  ],
  // Legacy alias
  'Buy the Dip': [
    'Jelaskan kenapa saham ini masuk klaster Beli Saat Turun?',
    'Kapan waktu terbaik untuk mulai akumulasi saham oversold?',
    'Jelaskan pola reversal yang biasa muncul setelah oversold',
    'Apa itu divergence bullish di RSI?',
  ],
  'Momentum': [
    'Bagaimana cara mengikuti tren naik dengan aman?',
    'Jelaskan kenapa EMA20 > EMA50 itu bullish?',
    'Kapan tren naik biasanya berakhir?',
    'Apa itu momentum dan bagaimana mengukurnya?',
  ],
  'Trending / Momentum': [
    'Bagaimana cara mengikuti tren naik dengan aman?',
    'Jelaskan kenapa EMA20 > EMA50 itu bullish?',
    'Kapan tren naik biasanya berakhir?',
    'Apa itu momentum dan bagaimana mengukurnya?',
  ],
  'Konsolidasi': [
    'Apa strategi terbaik untuk saham konsolidasi?',
    'Jelaskan konsep akumulasi bertahap (Dollar Cost Averaging)',
    'Bagaimana Bollinger Bands membantu di pasar sideways?',
    'Apa yang dimaksud dengan support dan resistance?',
  ],
  'Sideways / Accumulation': [
    'Apa strategi terbaik untuk saham sideways?',
    'Jelaskan konsep akumulasi bertahap (Dollar Cost Averaging)',
    'Bagaimana Bollinger Bands membantu di pasar sideways?',
    'Apa yang dimaksud dengan support dan resistance?',
  ],
  'High Risk': [
    'Mengapa saham ini dikategorikan High Risk?',
    'Apa tanda-tanda saham sedang dimanipulasi bandar?',
    'Bagaimana cara mengukur risiko sebelum masuk posisi?',
    'Jelaskan pentingnya manajemen risiko dalam trading',
  ],
  'High Risk / Avoid': [
    'Mengapa saham ini dikategorikan High Risk?',
    'Apa tanda-tanda saham sedang dimanipulasi bandar?',
    'Bagaimana cara mengukur risiko sebelum masuk posisi?',
    'Jelaskan pentingnya manajemen risiko dalam trading',
  ],
};

// ---------------------------------------------------------------------------
// Markdown Renderer (lightweight, no external deps)
// ---------------------------------------------------------------------------

function renderMarkdown(text) {
  const lines = text.split('\n');
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Blockquote (disclaimer)
    if (line.startsWith('> ')) {
      elements.push(
        <blockquote key={i} className="mentor-blockquote">
          {parseInline(line.slice(2))}
        </blockquote>
      );
      i++;
      continue;
    }

    // Unordered list
    if (line.match(/^[-*] /)) {
      const items = [];
      while (i < lines.length && lines[i].match(/^[-*] /)) {
        items.push(<li key={i}>{parseInline(lines[i].slice(2))}</li>);
        i++;
      }
      elements.push(<ul key={`ul-${i}`} className="mentor-list">{items}</ul>);
      continue;
    }

    // Ordered list
    if (line.match(/^\d+\. /)) {
      const items = [];
      while (i < lines.length && lines[i].match(/^\d+\. /)) {
        items.push(<li key={i}>{parseInline(lines[i].replace(/^\d+\. /, ''))}</li>);
        i++;
      }
      elements.push(<ol key={`ol-${i}`} className="mentor-list mentor-list-ordered">{items}</ol>);
      continue;
    }

    // Headings
    if (line.startsWith('### ')) {
      elements.push(<h3 key={i} className="mentor-h3">{parseInline(line.slice(4))}</h3>);
      i++;
      continue;
    }
    if (line.startsWith('## ')) {
      elements.push(<h2 key={i} className="mentor-h2">{parseInline(line.slice(3))}</h2>);
      i++;
      continue;
    }

    // Table (simple 2-3 column)
    if (line.startsWith('|') && lines[i + 1]?.startsWith('|---')) {
      const headers = line.split('|').filter(Boolean).map(h => h.trim());
      i += 2; // skip separator
      const rows = [];
      while (i < lines.length && lines[i].startsWith('|')) {
        rows.push(lines[i].split('|').filter(Boolean).map(c => c.trim()));
        i++;
      }
      elements.push(
        <div key={`tbl-${i}`} className="mentor-table-wrap">
          <table className="mentor-table">
            <thead>
              <tr>{headers.map((h, j) => <th key={j}>{parseInline(h)}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row, ri) => (
                <tr key={ri}>
                  {row.map((cell, ci) => <td key={ci}>{parseInline(cell)}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Empty line
    if (line.trim() === '') {
      i++;
      continue;
    }

    // Paragraph
    if (line.trim()) {
      elements.push(<p key={i} className="mentor-p">{parseInline(line)}</p>);
    }
    i++;
  }

  return elements;
}

function parseInline(text) {
  // Bold (**text**) and inline code (`code`)
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} className="mentor-code">{part.slice(1, -1)}</code>;
    }
    // Emoji preservation
    return part;
  });
}

// ---------------------------------------------------------------------------
// Message Bubble
// ---------------------------------------------------------------------------

function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className={`flex gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {!isUser && (
        <div className="mentor-avatar">
          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>auto_awesome</span>
        </div>
      )}
      <div className={`mentor-bubble ${isUser ? 'mentor-bubble-user' : 'mentor-bubble-ai'}`}>
        {isUser
          ? <p className="mentor-p">{message.content}</p>
          : renderMarkdown(message.content)
        }
        {message.isStreaming && (
          <span className="mentor-cursor" aria-hidden="true" />
        )}
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Suggested Question Chip
// ---------------------------------------------------------------------------

function SuggestionChip({ text, onClick }) {
  return (
    <button
      onClick={() => onClick(text)}
      className="mentor-suggestion-chip"
      type="button"
    >
      <span className="material-symbols-outlined" style={{ fontSize: '12px' }}>lightbulb</span>
      {text}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Rate Limit Toast
// ---------------------------------------------------------------------------

function RateLimitToast({ visible }) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 8 }}
          className="mentor-rate-toast"
        >
          <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>timer</span>
          Terlalu banyak pertanyaan. Tunggu sebentar ya!
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// ---------------------------------------------------------------------------
// Main ChatWidget
// ---------------------------------------------------------------------------

export default function ChatWidget() {
  const { isOpen, prefilledQuestion, pageContext, sessionId, openMentor, closeMentor } = useMentor();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [showRateLimit, setShowRateLimit] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle pre-filled question from Learning Layer
  useEffect(() => {
    if (isOpen && prefilledQuestion) {
      setInput(prefilledQuestion);
      // Small delay so the widget renders first
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, prefilledQuestion]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [isOpen, isMinimized]);

  // Initial greeting
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const ticker = pageContext?.ticker?.replace('.JK', '');
      const greeting = ticker
        ? `Halo! Saya **Liquidity Mentor** 👋\n\nSaya siap membantu menjelaskan analisis untuk saham **${ticker}**. Apa yang ingin kamu pelajari hari ini?`
        : `Halo! Saya **Liquidity Mentor** 👋\n\nSaya adalah asisten edukasi keuangan untuk platform LiquidityResearch. Tanyakan apa saja tentang analisis teknikal, klaster ML, atau strategi manajemen risiko!`;
      setMessages([{ role: 'model', content: greeting, id: 'greeting' }]);
    }
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const suggestions = pageContext?.cluster_label
    ? (CLUSTER_SUGGESTIONS[pageContext.cluster_label] || DEFAULT_SUGGESTIONS)
    : DEFAULT_SUGGESTIONS;

  // ---------------------------------------------------------------------------
  // Send message
  // ---------------------------------------------------------------------------

  const sendMessage = useCallback(async (text) => {
    const question = (text || input).trim();
    if (!question || isStreaming) return;

    setInput('');
    const userMsg = { role: 'user', content: question, id: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setIsStreaming(true);

    // Placeholder for streaming AI message
    const aiMsgId = Date.now() + 1;
    setMessages(prev => [...prev, { role: 'model', content: '', id: aiMsgId, isStreaming: true }]);

    // Build history for API
    const history = [...messages, userMsg].map(m => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const controller = new AbortController();
      abortRef.current = controller;

      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: history,
          context: pageContext,
          session_id: sessionId,
        }),
        signal: controller.signal,
      });

      if (res.status === 429) {
        setMessages(prev => prev.filter(m => m.id !== aiMsgId));
        setShowRateLimit(true);
        setTimeout(() => setShowRateLimit(false), 4000);
        setIsStreaming(false);
        return;
      }

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const raw = decoder.decode(value, { stream: true });
        const lines = raw.split('\n');

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const data = line.slice(6);
          try {
            const token = JSON.parse(data);
            if (token === '[DONE]') break;
            accumulated += token;
            setMessages(prev =>
              prev.map(m =>
                m.id === aiMsgId
                  ? { ...m, content: accumulated, isStreaming: true }
                  : m
              )
            );
          } catch {
            // malformed chunk, skip
          }
        }
      }

      // Finalize message (remove cursor)
      setMessages(prev =>
        prev.map(m =>
          m.id === aiMsgId ? { ...m, isStreaming: false } : m
        )
      );
    } catch (err) {
      if (err.name === 'AbortError') return;
      setMessages(prev =>
        prev.map(m =>
          m.id === aiMsgId
            ? {
                ...m,
                content: '⚠️ Maaf, Mentor mengalami gangguan koneksi. Silakan coba lagi.',
                isStreaming: false,
              }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  }, [input, isStreaming, messages, pageContext, sessionId]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleStop = () => {
    abortRef.current?.abort();
    setIsStreaming(false);
    setMessages(prev =>
      prev.map(m => m.isStreaming ? { ...m, isStreaming: false } : m)
    );
  };

  const handleClear = () => {
    setMessages([]);
    setInput('');
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <>
      {/* ── Floating Trigger Button ──────────────────────────────────── */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            key="trigger"
            initial={{ opacity: 0, scale: 0.7, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.7, y: 20 }}
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
            onClick={() => openMentor()}
            id="mentor-trigger-btn"
            aria-label="Buka Liquidity Mentor AI"
            className="mentor-trigger"
          >
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ repeat: Infinity, duration: 4, ease: 'easeInOut', repeatDelay: 3 }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>auto_awesome</span>
            </motion.div>
            <span className="mentor-trigger-label">Ask Mentor</span>
            <div className="mentor-trigger-ping" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* ── Chat Window ─────────────────────────────────────────────── */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="chat-window"
            initial={{ opacity: 0, scale: 0.92, y: 24, originX: 1, originY: 1 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: 24 }}
            transition={{ type: 'spring', stiffness: 350, damping: 30 }}
            className="mentor-window"
            role="dialog"
            aria-label="Liquidity Mentor Chat"
          >
            {/* Header */}
            <div className="mentor-header">
              <div className="mentor-header-left">
                <div className="mentor-logo">
                  <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>auto_awesome</span>
                </div>
                <div>
                  <div className="mentor-header-title">Liquidity Mentor</div>
                  {pageContext?.ticker && (
                    <div className="mentor-header-context">
                      <span className="material-symbols-outlined" style={{ fontSize: '11px' }}>pin</span>
                      {pageContext.ticker.replace('.JK', '')}
                      {pageContext.cluster_label && ` · ${pageContext.cluster_label}`}
                    </div>
                  )}
                  {!pageContext?.ticker && (
                    <div className="mentor-header-context">
                      <span className="mentor-online-dot" />
                      Online · Siap membantu
                    </div>
                  )}
                </div>
              </div>
              <div className="mentor-header-actions">
                {messages.length > 1 && (
                  <button
                    onClick={handleClear}
                    title="Hapus percakapan"
                    className="mentor-icon-btn"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>restart_alt</span>
                  </button>
                )}
                <button
                  onClick={() => setIsMinimized(v => !v)}
                  title={isMinimized ? 'Perluas' : 'Perkecil'}
                  className="mentor-icon-btn"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                    {isMinimized ? 'expand_less' : 'remove'}
                  </span>
                </button>
                <button
                  onClick={closeMentor}
                  title="Tutup"
                  className="mentor-icon-btn"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>close</span>
                </button>
              </div>
            </div>

            <AnimatePresence>
              {!isMinimized && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2, ease: 'easeInOut' }}
                  className="mentor-body"
                >
                  {/* Messages */}
                  <div className="mentor-messages" id="mentor-messages-list">
                    {messages.map(msg => (
                      <MessageBubble key={msg.id} message={msg} />
                    ))}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Suggestions (show only when few messages) */}
                  {messages.length <= 1 && (
                    <div className="mentor-suggestions">
                      <div className="mentor-suggestions-label">
                        <span className="material-symbols-outlined" style={{ fontSize: '12px' }}>lightbulb</span>
                        Pertanyaan yang disarankan
                      </div>
                      <div className="mentor-suggestions-list">
                        {suggestions.slice(0, 4).map((s, i) => (
                          <SuggestionChip
                            key={i}
                            text={s}
                            onClick={(t) => sendMessage(t)}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Rate limit toast */}
                  <RateLimitToast visible={showRateLimit} />

                  {/* Input */}
                  <div className="mentor-input-area">
                    <textarea
                      ref={inputRef}
                      id="mentor-input"
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Tanya Mentor tentang saham, indikator, atau strategi..."
                      rows={2}
                      className="mentor-input"
                      disabled={isStreaming}
                      aria-label="Pesan untuk Liquidity Mentor"
                    />
                    <div className="mentor-input-actions">
                      <span className="mentor-hint">Enter untuk kirim · Shift+Enter baris baru</span>
                      {isStreaming ? (
                        <button
                          onClick={handleStop}
                          className="mentor-btn mentor-btn-stop"
                          title="Hentikan"
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>stop_circle</span>
                          Stop
                        </button>
                      ) : (
                        <button
                          onClick={() => sendMessage()}
                          disabled={!input.trim()}
                          className="mentor-btn mentor-btn-send"
                          id="mentor-send-btn"
                          title="Kirim pertanyaan"
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>send</span>
                          Kirim
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Footer disclaimer */}
                  <div className="mentor-footer">
                    <span className="material-symbols-outlined" style={{ fontSize: '11px' }}>info</span>
                    Hanya untuk tujuan edukasi · Bukan saran investasi
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
