export interface MistralResponseData {
  response: string;
  latency_ms: number;
  source: string;
}

export interface CorpusResponseData {
  response: string | null;
  key_points: string | null;
  matched_question: string | null;
  category: string | null;
  source: string | null;
  similarity: number | null;
  latency_ms: number;
  found: boolean;
}

export interface Message {
  id: number;
  conversation_id: number;
  query: string;
  mistral_response: string | null;
  corpus_response: string | null;
  corpus_question_matched: string | null;
  corpus_category: string | null;
  corpus_source: string | null;
  similarity_score: number | null;
  mistral_latency_ms: number | null;
  corpus_latency_ms: number | null;
  temperature: number;
  top_p: number | null;
  max_tokens: number;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface MistralParams {
  temperature: number;
  top_p: number;
  max_tokens: number;
}
