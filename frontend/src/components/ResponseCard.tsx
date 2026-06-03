"use client";

import { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ResponseCardProps {
  title: string;
  icon: ReactNode;
  accentColor: string;
  response: string;
  isLoading: boolean;
  meta?: ReactNode;
}

export default function ResponseCard({ title, icon, accentColor, response, isLoading, meta }: ResponseCardProps) {
  return (
    <div
      className="flex flex-col rounded-2xl overflow-hidden fade-in"
      style={{ background: "var(--bg)", border: "1px solid var(--border)", minHeight: 120 }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3" style={{ borderBottom: "1px solid var(--border)" }}>
        <span style={{ color: accentColor }}>{icon}</span>
        <span className="text-xs font-semibold" style={{ color: "var(--text-primary)" }}>{title}</span>
      </div>

      {/* Body */}
      <div className="flex-1 px-4 py-4">
        {isLoading ? (
          <div className="space-y-2 py-1">
            {[95, 80, 90, 65, 75].map((w, i) => (
              <div key={i} className="shimmer h-3 rounded-full" style={{ width: `${w}%` }} />
            ))}
          </div>
        ) : (
          <div className="md-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {response || "No response available."}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* Footer meta */}
      {!isLoading && meta && (
        <div className="px-4 py-2 flex flex-wrap gap-2 items-center" style={{ borderTop: "1px solid var(--border)" }}>
          {meta}
        </div>
      )}
    </div>
  );
}
