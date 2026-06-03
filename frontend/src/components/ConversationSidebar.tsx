"use client";

import { useState } from "react";
import { Plus, Trash2, Pencil, Check, X, MessageSquare } from "lucide-react";
import type { Conversation } from "@/types";
import { deleteConversation, renameConversation } from "@/lib/api";

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const h = Math.floor(mins / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

interface Props {
  conversations: Conversation[];
  activeId: number | null;
  onSelect: (id: number) => void;
  onNew: () => void;
  onDelete: (id: number) => void;
  onRename: (id: number, title: string) => void;
}

export default function ConversationSidebar({ conversations, activeId, onSelect, onNew, onDelete, onRename }: Props) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState("");
  const [hoveredId, setHoveredId] = useState<number | null>(null);

  const startEdit = (conv: Conversation, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditValue(conv.title);
  };

  const commitEdit = async (id: number) => {
    if (editValue.trim()) {
      await renameConversation(id, editValue.trim());
      onRename(id, editValue.trim());
    }
    setEditingId(null);
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteConversation(id);
    onDelete(id);
  };

  return (
    <div className="flex flex-col h-full" style={{ width: 260, minWidth: 260, background: "var(--sidebar-bg)", borderRight: "1px solid var(--border)" }}>
      {/* Brand */}
      <div className="px-4 pt-5 pb-3" style={{ borderBottom: "1px solid var(--border)" }}>
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold" style={{ background: "var(--accent)" }}>
            F
          </div>
          <div>
            <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>FinStress Bot</p>
            <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>Financial Study Assistant</p>
          </div>
        </div>
      </div>

      {/* New Chat */}
      <div className="px-3 py-3">
        <button
          onClick={onNew}
          className="w-full flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-colors"
          style={{ background: "var(--bg)", border: "1px solid var(--border-strong)", color: "var(--text-primary)" }}
          onMouseEnter={e => (e.currentTarget.style.background = "var(--sidebar-hover)")}
          onMouseLeave={e => (e.currentTarget.style.background = "var(--bg)")}
        >
          <Plus size={15} style={{ color: "var(--text-secondary)" }} />
          New chat
        </button>
      </div>

      {/* Section label */}
      {conversations.length > 0 && (
        <p className="px-4 pb-1 text-[11px] font-medium uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
          Recent
        </p>
      )}

      {/* List */}
      <div className="flex-1 overflow-y-auto px-2 pb-4">
        {conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-center px-4">
            <MessageSquare size={20} style={{ color: "var(--text-muted)", marginBottom: 8 }} />
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>No conversations yet</p>
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeId;
            const isEditing = editingId === conv.id;
            const isHovered = hoveredId === conv.id;

            return (
              <div
                key={conv.id}
                onClick={() => !isEditing && onSelect(conv.id)}
                onMouseEnter={() => setHoveredId(conv.id)}
                onMouseLeave={() => setHoveredId(null)}
                className="group flex items-center gap-2 rounded-xl px-3 py-2 mb-0.5 cursor-pointer transition-colors"
                style={{ background: isActive ? "var(--sidebar-active)" : isHovered ? "var(--sidebar-hover)" : "transparent" }}
              >
                {isEditing ? (
                  <div className="flex flex-1 items-center gap-1" onClick={e => e.stopPropagation()}>
                    <input
                      autoFocus
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onKeyDown={e => { if (e.key === "Enter") commitEdit(conv.id); if (e.key === "Escape") setEditingId(null); }}
                      className="flex-1 text-xs rounded-lg px-2 py-1 outline-none"
                      style={{ background: "var(--bg)", border: "1px solid var(--accent)", color: "var(--text-primary)" }}
                    />
                    <button onClick={() => commitEdit(conv.id)} className="p-0.5"><Check size={12} style={{ color: "var(--accent)" }} /></button>
                    <button onClick={() => setEditingId(null)} className="p-0.5"><X size={12} style={{ color: "var(--text-muted)" }} /></button>
                  </div>
                ) : (
                  <>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate" style={{ color: "var(--text-primary)" }}>{conv.title}</p>
                      <p className="text-[10px] mt-0.5" style={{ color: "var(--text-muted)" }}>{relativeTime(conv.updated_at)}</p>
                    </div>
                    {(isHovered || isActive) && (
                      <div className="flex items-center gap-0.5 flex-shrink-0">
                        <button
                          onClick={e => startEdit(conv, e)}
                          className="p-1 rounded-md transition-colors"
                          style={{ color: "var(--text-muted)" }}
                          onMouseEnter={e => (e.currentTarget.style.color = "var(--text-primary)")}
                          onMouseLeave={e => (e.currentTarget.style.color = "var(--text-muted)")}
                        >
                          <Pencil size={11} />
                        </button>
                        <button
                          onClick={e => handleDelete(conv.id, e)}
                          className="p-1 rounded-md transition-colors"
                          style={{ color: "var(--text-muted)" }}
                          onMouseEnter={e => (e.currentTarget.style.color = "var(--danger)")}
                          onMouseLeave={e => (e.currentTarget.style.color = "var(--text-muted)")}
                        >
                          <Trash2 size={11} />
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
