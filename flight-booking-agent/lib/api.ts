import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  timeout: 60000,
});

export interface ChatRequest {
  message: string;
  thread_id: string;
}

export interface ChatResponse {
  response?: string;
  message?: string;
  answer?: string;
  [key: string]: unknown;
}

export async function sendMessage(
  payload: ChatRequest
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", payload);
  return data;
}

export default api;