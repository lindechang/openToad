import type { Message } from '../providers/types.js';
import type { ToolDefinition } from '../tools/base.js';

export interface AgentConfig {
  model: string;
  temperature?: number;
  maxIterations?: number;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

export interface AgentStep {
  thought: string;
  action?: ToolCall;
  observation?: string;
}

export interface AgentState {
  messages: Message[];
  steps: AgentStep[];
  tools: ToolDefinition[];
}
