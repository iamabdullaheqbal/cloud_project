"use client";

import { SlidersHorizontal } from "lucide-react";
import type { MistralParams, Message } from "@/types";

interface Props {
  params: MistralParams;
  onChange: (p: MistralParams) => void;
  lastMessage?: Message | null;
}

const PRESETS = [
  { label: "Precise", values: { temperature: 0.1, top_p: 0.8, max_tokens: 600 } },
  { label: "Balanced", values: { temperature: 0.4, top_p: 0.9, max_tokens: 800 } },
  { label: "Creative", values: { temperature: 0.9, top_p: 1.0, max_tokens: 1200 } },
] as const;

function tempColor(t: number) {
  if (t <= 0.3) return "#16a34a";
  if (t <= 0.8) return "#d97706";
  return "#dc2626";
}

function SliderRow({
  label, helper, value, min, max, step, format, color, onChange,
}: {
  label: string; helper: string; value: number; min: number; max: number;
  step: number; format: (v: number) => string; color?: string; onChange: (v: number) => void;
}) {
  return (
    <div className="mb-5">
      <div className="flex items-center justify-between mb-2">
        <div>
          <p className="text-xs font-medium" style={{ color: "var(--text-primary)" }}>{label}</p>
          <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>{helper}</p>
        </div>
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded-md min-w-[40px] text-center"
          style={{ background: "var(--bg-secondary)", color: color || "var(--accent)", border: "1px solid var(--border)" }}
        >
          {format(value)}
        </span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={e => onChange(parseFloat(e.target.value))} />
    </div>
  );
}

export default function ParameterPanel({ params, onChange, lastMessage }: Props) {
  const set = (key: keyof MistralParams, val: number) => onChange({ ...params, [key]: val });

  return (
    <div
      className="flex flex-col h-full overflow-y-auto"
      style={{ width: 272, minWidth: 272, background: "var(--bg)", borderLeft: "1px solid var(--border)" }}
    >
      {/* Header */}
      <div className="px-5 pt-5 pb-4" style={{ borderBottom: "1px solid var(--border)" }}>
        <div className="flex items-center gap-2">
          <SlidersHorizontal size={15} style={{ color: "var(--accent)" }} />
          <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>Parameters</p>
        </div>
        <p className="text-[11px] mt-1" style={{ color: "var(--text-muted)" }}>Controls the next Mistral AI request</p>
      </div>

      <div className="px-5 py-4">
        {/* Presets */}
        <div className="mb-5">
          <p className="text-[11px] font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>Preset</p>
          <div className="flex gap-1.5">
            {PRESETS.map(p => {
              const active = params.temperature === p.values.temperature && params.top_p === p.values.top_p && params.max_tokens === p.values.max_tokens;
              return (
                <button
                  key={p.label}
                  onClick={() => onChange({ ...p.values })}
                  className="flex-1 py-1.5 rounded-lg text-xs font-medium transition-all"
                  style={{
                    background: active ? "var(--accent)" : "var(--bg-secondary)",
                    color: active ? "#fff" : "var(--text-secondary)",
                    border: `1px solid ${active ? "var(--accent)" : "var(--border)"}`,
                  }}
                >
                  {p.label}
                </button>
              );
            })}
          </div>
        </div>

        <div style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
          <SliderRow
            label="Temperature"
            helper="Lower = focused · Higher = creative"
            value={params.temperature}
            min={0} max={1.5} step={0.05}
            color={tempColor(params.temperature)}
            onChange={v => set("temperature", v)}
            format={v => v.toFixed(2)}
          />
          <SliderRow
            label="Top P"
            helper="Nucleus sampling threshold"
            value={params.top_p}
            min={0.1} max={1.0} step={0.05}
            onChange={v => set("top_p", v)}
            format={v => v.toFixed(2)}
          />
          <SliderRow
            label="Max Tokens"
            helper="Maximum response length"
            value={params.max_tokens}
            min={100} max={2000} step={50}
            onChange={v => set("max_tokens", v)}
            format={v => v.toString()}
          />
        </div>

        {/* Last used */}
        {lastMessage && (
          <div className="mt-1 rounded-xl p-3" style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}>
            <p className="text-[11px] font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>Last Used</p>
            {[
              ["Temperature", lastMessage.temperature.toFixed(2)],
              ["Top P", (lastMessage.top_p ?? 0.9).toFixed(2)],
              ["Max Tokens", lastMessage.max_tokens.toString()],
            ].map(([label, val]) => (
              <div key={label} className="flex justify-between items-center py-0.5">
                <span className="text-xs" style={{ color: "var(--text-secondary)" }}>{label}</span>
                <span className="text-xs font-medium" style={{ color: "var(--text-primary)" }}>{val}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
