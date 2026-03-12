import type { LLMProvider } from '../providers/types.js';
import type { AgentConfig, AgentState, ToolCall } from './types.js';
import { globalTools } from '../tools/index.js';
import { buildSystemPrompt } from './prompt.js';

export class Agent {
  private provider: LLMProvider;
  private config: AgentConfig;
  
  constructor(provider: LLMProvider, config: AgentConfig) {
    this.provider = provider;
    this.config = config;
  }
  
  async run(userInput: string): Promise<string> {
    const state: AgentState = {
      messages: [
        { role: 'system', content: buildSystemPrompt() },
        { role: 'user', content: userInput }
      ],
      steps: [],
      tools: globalTools.list()
    };
    
    for (let i = 0; i < (this.config.maxIterations || 10); i++) {
      const response = await this.provider.chat({
        model: this.config.model,
        messages: state.messages,
        temperature: this.config.temperature
      });
      
      state.messages.push({
        role: 'assistant',
        content: response.content
      });
      
      const toolCall = this.parseToolCall(response.content);
      
      if (!toolCall) {
        return response.content;
      }
      
      const tool = globalTools.get(toolCall.name);
      if (!tool) {
        state.messages.push({
          role: 'user',
          content: `Tool ${toolCall.name} not found`
        });
        continue;
      }
      
      const result = await tool.execute(toolCall.arguments);
      
      state.messages.push({
        role: 'user',
        content: result.success 
          ? `Observation: ${result.output}`
          : `Error: ${result.error}`
      });
    }
    
    return 'Max iterations reached';
  }
  
  private parseToolCall(content: string): ToolCall | null {
    const match = content.match(/```json\n([\s\S]*?)\n```/);
    if (match) {
      try {
        return JSON.parse(match[1]);
      } catch {
        return null;
      }
    }
    return null;
  }
}
