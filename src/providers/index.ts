import { AnthropicProvider } from './anthropic.js';
import { OpenAIProvider } from './openai.js';
import { DeepSeekProvider } from './deepseek.js';
import { OllamaProvider } from './ollama.js';
import type { LLMProvider } from './types.js';

export function createProvider(type: string, apiKey: string, baseURL?: string): LLMProvider {
  switch (type) {
    case 'anthropic':
      return new AnthropicProvider(apiKey);
    case 'openai':
      return new OpenAIProvider(apiKey);
    case 'deepseek':
      return new DeepSeekProvider(apiKey);
    case 'ollama':
      return new OllamaProvider(apiKey, baseURL);
    default:
      throw new Error(`Unknown provider: ${type}`);
  }
}

export * from './types.js';
export { AnthropicProvider } from './anthropic.js';
export { OpenAIProvider } from './openai.js';
export { DeepSeekProvider } from './deepseek.js';
export { OllamaProvider } from './ollama.js';
