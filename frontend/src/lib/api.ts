import type {
  Conversation,
  Message,
  MistralParams,
  MistralResponseData,
  CorpusResponseData,
  RagResponseData,
  SafetyRagResponseData,
} from "@/types";

const BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // ignore parse error
    }
    throw new Error(`API ${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function createConversation(): Promise<Conversation> {
  return request<Conversation>("/api/conversations", { method: "POST" });
}

export async function getConversations(): Promise<Conversation[]> {
  return request<Conversation[]>("/api/conversations");
}

export async function deleteConversation(id: number): Promise<void> {
  return request<void>(`/api/conversations/${id}`, { method: "DELETE" });
}

export async function renameConversation(
  id: number,
  title: string
): Promise<Conversation> {
  return request<Conversation>(`/api/conversations/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

export async function getMessages(conversationId: number): Promise<Message[]> {
  return request<Message[]>(`/api/conversations/${conversationId}/messages`);
}

export async function sendChat(
  conversationId: number,
  query: string,
  params: MistralParams
): Promise<{
  message: Message;
  mistral: MistralResponseData;
  corpus: CorpusResponseData;
  s1: RagResponseData;
  s2: SafetyRagResponseData;
}> {
  return request(`/api/conversations/${conversationId}/chat`, {
    method: "POST",
    body: JSON.stringify({
      query,
      temperature: params.temperature,
      top_p: params.top_p,
      max_tokens: params.max_tokens,
    }),
  });
}
