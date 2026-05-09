'use client';

import { createContext, useContext, useState, useCallback, useRef } from 'react';

/**
 * MentorContext — shared state for the Liquidity Mentor chatbot.
 *
 * Any component can call `openMentor(question, context)` to open
 * the floating chat widget with a pre-filled question and page context.
 * This powers the "Learning Layer": clicking RSI, MACD, ATR, etc. in the
 * dashboard auto-opens the mentor with a targeted explanation request.
 */
const MentorContext = createContext(null);

export function MentorProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const [prefilledQuestion, setPrefilledQuestion] = useState('');
  const [pageContext, setPageContext] = useState({});

  // Stable session ID for rate-limiting (per browser tab)
  const sessionId = useRef(
    (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function')
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2)
  ).current;

  /**
   * Open the mentor widget with an optional pre-filled question.
   * @param {string} question - Pre-filled question text
   * @param {object} ctx - Page context (ticker, cluster_label, indicators, trade_plan)
   */
  const openMentor = useCallback((question = '', ctx = {}) => {
    setPrefilledQuestion(question);
    setPageContext(ctx);
    setIsOpen(true);
  }, []);

  /**
   * Convenience: ask about a technical term in the context of a stock.
   * @param {string} term - e.g. "RSI", "ATR", "Fibonacci"
   * @param {string} ticker - e.g. "BBCA"
   * @param {object} ctx - Full page context object
   */
  const askAboutTerm = useCallback((term, ticker, ctx = {}) => {
    const question = `Tolong jelaskan **${term}** dalam konteks saham **${ticker}** ini.`;
    openMentor(question, ctx);
  }, [openMentor]);

  const closeMentor = useCallback(() => {
    setIsOpen(false);
    setPrefilledQuestion('');
  }, []);

  const value = {
    isOpen,
    prefilledQuestion,
    pageContext,
    sessionId,
    openMentor,
    askAboutTerm,
    closeMentor,
  };

  return (
    <MentorContext.Provider value={value}>
      {children}
    </MentorContext.Provider>
  );
}

export function useMentor() {
  const ctx = useContext(MentorContext);
  if (!ctx) {
    throw new Error('useMentor must be used within a MentorProvider');
  }
  return ctx;
}
