"use client";

import { useState, useEffect, useCallback } from "react";
import ConversationSidebar from "@/components/ConversationSidebar";
import ChatPanel from "@/components/ChatPanel";
import ParameterPanel from "@/components/ParameterPanel";
import type { Conversation, Message, MistralParams } from "@/types";
import { getConversations, createConversation, getMessages, sendChat } from "@/lib/api";

const DEFAULT_PARAMS: MistralParams = { temperature: 0.4, top_p: 0.9, max_tokens: 800 };

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [params, setParams] = useState<MistralParams>(DEFAULT_PARAMS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectConversation = useCallback(async (id: number) => {
    setActiveConversationId(id);
    setError(null);
    try {
      setMessages(await getMessages(id));
    } catch {
      setError("Failed to load messages.");
      setMessages([]);
    }
  }, []);

  useEffect(() => {
    getConversations().then(convs => {
      setConversations(convs);
      if (convs.length > 0) selectConversation(convs[0].id);
    }).catch(console.error);
  }, [selectConversation]);

  const handleNew = async () => {
    try {
      const conv = await createConversation();
      setConversations(prev => [conv, ...prev]);
      setActiveConversationId(conv.id);
      setMessages([]);
      setError(null);
    } catch { setError("Failed to create conversation."); }
  };

  const handleDelete = (id: number) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (activeConversationId === id) { setActiveConversationId(null); setMessages([]); }
  };

  const handleRename = (id: number, title: string) => {
    setConversations(prev => prev.map(c => c.id === id ? { ...c, title } : c));
  };

  const handleSend = async (query: string) => {
    if (!activeConversationId) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await sendChat(activeConversationId, query, params);
      setMessages(prev => [...prev, result.message]);
      getConversations().then(setConversations).catch(console.error);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "var(--bg)" }}>
      <ConversationSidebar
        conversations={conversations}
        activeId={activeConversationId}
        onSelect={selectConversation}
        onNew={handleNew}
        onDelete={handleDelete}
        onRename={handleRename}
      />
      <ChatPanel
        conversationId={activeConversationId}
        messages={messages}
        isLoading={isLoading}
        onSend={handleSend}
        error={error}
      />
      <ParameterPanel
        params={params}
        onChange={setParams}
        lastMessage={messages.length > 0 ? messages[messages.length - 1] : null}
      />
    </div>
  );
}
