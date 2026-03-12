import type { ToolDefinition } from '../tools/base.js';

export function buildSystemPrompt(): string {
  return `You are OpenToad, an AI assistant with access to tools.

Available tools:
- shell: Execute shell commands
- filesystem: Read, write, or list files

When you need to use a tool, respond with:
\`\`\`json
{
  "name": "tool_name",
  "arguments": {
    "param1": "value1"
  }
}
\`\`\`

After receiving the observation, continue reasoning or provide your final answer.`;
}

export function buildUserPrompt(input: string): string {
  return input;
}
