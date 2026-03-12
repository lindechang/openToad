import OpenAI from 'openai';
import type { LLMProvider, ChatOptions, ChatResponse } from './types.js';

export class OllamaProvider implements LLMProvider {
  name = 'ollama';
  private baseURL: string;
  private client: OpenAI;
  
  constructor(apiKey: string = 'ollama', baseURL: string = 'http://localhost:11434/v1') {
    this.baseURL = baseURL;
    this.client = new OpenAI({ apiKey, baseURL });
  }
  
  async chat(options: ChatOptions): Promise<ChatResponse> {
    const response = await this.client.chat.completions.create({
      model: options.model,
      messages: options.messages,
      temperature: options.temperature,
      max_tokens: options.maxTokens
    });
    
    return {
      content: response.choices[0]?.message?.content || '',
      finishReason: (response.choices[0]?.finish_reason || 'stop') as 'stop' | 'length' | 'content_filter'
    };
  }
  
  async chatStream(options: ChatOptions, onChunk: (chunk: string) => void): Promise<ChatResponse> {
    const stream = await this.client.chat.completions.create({
      model: options.model,
      messages: options.messages,
      temperature: options.temperature,
      max_tokens: options.maxTokens,
      stream: true
    });
    
    let content = '';
    for await (const chunk of stream) {
      const text = chunk.choices[0]?.delta?.content || '';
      content += text;
      onChunk(text);
    }
    
    return { content, finishReason: 'stop' };
  }
  
  async listModels(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseURL}/models`);
      const data = await response.json() as { models?: Array<{ name: string }> };
      return data.models?.map(m => m.name) || [];
    } catch {
      return [];
    }
  }
}
