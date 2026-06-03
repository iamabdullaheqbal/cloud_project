"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, Loader2, Sparkles, Database, ArrowUp } from "lucide-react";
import ResponseCard from "./ResponseCard";
import type { Message, MistralParams } from "@/types";

const SUGGESTED = [
  "How does financial stress affect student mental health?",
  "What are the best budgeting strategies for students?",
  "How can I cope with student loan anxiety?",
  "What support do universities offer financially stressed students?",
  "What are the long-term effects of student financial pressure?",
];

function Badge({ children, color }: { children: React.ReactNode; color?: string }) {
  return (
    <span
      className="inline-flex items-center text-[11px] px-2 py-0.5 rounded-full font-medium"
      style={{ background: "var(--bg-secondary)", color: color || "var(--text-muted)", border: "1px solid var(--border)" }}
    >
      {children}
    </span>
  );
}

interface Props {
  conversationId: number | null;
  messages: Message[];
  params: MistralParams;
  isLoading: boolean;
  onSend: (query: string) => Promise<void>;
  error: string | null;
}

export default function ChatPanel({ conversationId, messages, params, isLoading, onSend, error }: Props) {
  const [query, setQuery] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    const q = query.trim();
    if (!q || isLoading || !conversationId) return;
    setQuery("");
    if (textareaRef.current) { textareaRef.current.style.height = "auto"; }
    await onSend(q);
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleTextarea = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  if (!conversationId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center" style={{ background: "var(--bg)" }}>
        <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white text-xl font-bold mb-4" style={{ background: "var(--accent)" }}>F</div>
        <h2 className="text-lg font-semibold mb-1" style={{ color: "var(--text-primary)" }}>How can I help you today?</h2>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>Select a conversation or start a new chat</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden" style={{ background: "var(--bg)" }}>
      {/* Thread */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full px-6">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white text-2xl font-bold mb-5" style={{ background: "var(--accent)" }}>F</div>
            <h2 className="text-xl font-semibold mb-2 text-center" style={{ color: "var(--text-primary)" }}>How can I help you today?</h2>
            <p className="text-sm mb-8 text-center" style={{ color: "var(--text-muted)" }}>Ask anything about financial study pressure</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-2xl">
              {SUGGESTED.map(s => (
                <button
                  key={s}
                  onClick={() => { setQuery(s); textareaRef.current?.focus(); }}
                  className="text-left text-sm px-4 py-3 rounded-xl transition-colors"
                  style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
                  onMouseEnter={e => (e.currentTarget.style.borderColor = "var(--accent)")}
                  onMouseLeave={e => (e.currentTarget.style.borderColor = "var(--border)")}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto px-6 py-6 space-y-8">
            {messages.map(msg => (
              <div key={msg.id} className="fade-in">
                {/* User bubble */}
                <div className="flex justify-end mb-4">
                  <div className="max-w-xl rounded-2xl rounded-br-sm px-4 py-3" style={{ background: "var(--user-bubble)" }}>
                    <p className="text-sm leading-relaxed" style={{ color: "var(--text-primary)" }}>{msg.query}</p>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                      <Badge>T: {msg.temperature.toFixed(2)}</Badge>
                      <Badge>P: {(msg.top_p ?? 0.9).toFixed(2)}</Badge>
                      <Badge>Tok: {msg.max_tokens}</Badge>
                    </div>
                  </div>
                </div>

                {/* Response cards */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
                  <ResponseCard
                    title="Mistral AI"
                    accentColor="var(--accent)"
                    icon={<Sparkles size={14} />}
                    response={msg.mistral_response || ""}
                    isLoading={false}
                    meta={
                      <>
                        {msg.mistral_latency_ms != null && <Badge color="var(--accent)">{msg.mistral_latency_ms}ms</Badge>}
                        <Badge>mistral-small-latest</Badge>
                      </>
                    }
                  />
                  <ResponseCard
                    title="Research Corpus"
                    accentColor="var(--accent-blue)"
                    icon={<Database size={14} />}
                    response={msg.corpus_response || "No corpus match found."}
                    isLoading={false}
                    meta={
                      <>
                        {msg.corpus_latency_ms != null && <Badge color="var(--accent-blue)">{msg.corpus_latency_ms}ms</Badge>}
                        {msg.similarity_score != null && <Badge color="var(--accent-blue)">{(msg.similarity_score * 100).toFixed(1)}% match</Badge>}
                        {msg.corpus_category && <Badge>{msg.corpus_category}</Badge>}
                      </>
                    }
                  />
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="fade-in">
                <div className="flex justify-end mb-4">
                  <div className="rounded-2xl rounded-br-sm px-4 py-3" style={{ background: "var(--user-bubble)" }}>
                    <p className="text-sm" style={{ color: "var(--text-muted)" }}>Thinking…</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
                  <ResponseCard title="Mistral AI" accentColor="var(--accent)" icon={<Sparkles size={14} />} response="" isLoading />
                  <ResponseCard title="Research Corpus" accentColor="var(--accent-blue)" icon={<Database size={14} />} response="" isLoading />
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="mx-6 mb-2 px-4 py-2 rounded-xl text-xs" style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#dc2626" }}>
          {error}
        </div>
      )}

      {/* Input */}
      <div className="px-6 pb-6 pt-4" style={{ borderTop: "1px solid var(--border)" }}>
        <div className="max-w-4xl mx-auto">
          <div
            className="flex items-end gap-3 rounded-2xl px-4 py-3"
            style={{ background: "var(--bg)", border: "1px solid var(--border-strong)", boxShadow: "0 1px 6px rgba(0,0,0,0.06)" }}
          >
            <textarea
              ref={textareaRef}
              rows={1}
              maxLength={500}
              value={query}
              onChange={handleTextarea}
              onKeyDown={handleKey}
              placeholder="Message FinStress Bot…"
              className="flex-1 resize-none bg-transparent text-sm outline-none leading-relaxed"
              style={{ color: "var(--text-primary)", minHeight: 24, maxHeight: 160 }}
            />
            <div className="flex items-center gap-2 pb-0.5 flex-shrink-0">
              <span className="text-[10px]" style={{ color: query.length > 450 ? "#dc2626" : "var(--text-muted)" }}>
                {query.length}/500
              </span>
              <button
                onClick={handleSend}
                disabled={!query.trim() || isLoading || !conversationId}
                className="w-8 h-8 rounded-xl flex items-center justify-center transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                style={{ background: "var(--accent)", color: "#fff" }}
              >
                {isLoading ? <Loader2 size={14} className="animate-spin" /> : <ArrowUp size={14} />}
              </button>
            </div>
          </div>
          <p className="text-[11px] text-center mt-2" style={{ color: "var(--text-muted)" }}>
            Enter to send · Shift+Enter for newline
          </p>
        </div>
      </div>
    </div>
  );
}
