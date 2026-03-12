import Anthropic from '@anthropic-ai/sdk';
import type { Message } from './types.js';
import type { LLMProvider, ChatOptions, ChatResponse } from './types.js';

export class AnthropicProvider implements LLMProvider {
  name = 'anthropic';
  private client: Anthropic;
  
  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }
  
  async chat(options: ChatOptions): Promise<ChatResponse> {
    const systemMessage = options.messages.find(m => m.role === 'system');
    const conversationMessages = options.messages.filter(m => m.role !== 'system') as Message[];
    
    const response = await this.client.messages.create({
      model: options.model,
      system: systemMessage?.content,
      messages: conversationMessages.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content
      })),
      temperature: options.temperature,
      max_tokens: options.maxTokens || 1024
    });
    
    return {
      content: response.content[0].type === 'text' ? response.content[0].text : '',
      finishReason: response.stop_reason === 'end_turn' ? 'stop' : 'length'
    };
  }
  
  async chatStream(options: ChatOptions, onChunk: (chunk: string) => void): Promise<ChatResponse> {
    const systemMessage = options.messages.find(m => m.role === 'system');
    const conversationMessages = options.messages.filter(m => m.role !== 'system') as Message[];
    
    const response = await this.client.messages.stream({
      model: options.model,
      system: systemMessage?.content,
      messages: conversationMessages.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content
      })),
      temperature: options.temperature,
      max_tokens: options.maxTokens || 1024
    });
    
    let content = '';
    for await (const event of response) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        const text = event.delta.text;
        content += text;
        onChunk(text);
      }
    }
    
    return { content, finishReason: 'stop' };
  }
  
  async listModels(): Promise<string[]> {
    return ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229'];
  }
}
