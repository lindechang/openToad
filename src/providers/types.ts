export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatOptions {
  model: string;
  messages: Message[];
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
}

export interface ChatResponse {
  content: string;
  finishReason: 'stop' | 'length' | 'content_filter';
}

export interface StreamCallback {
  (chunk: string): void;
}

export interface LLMProvider {
  name: string;
  chat(options: ChatOptions): Promise<ChatResponse>;
  chatStream(options: ChatOptions, onChunk: StreamCallback): Promise<ChatResponse>;
  listModels(): Promise<string[]>;
}
