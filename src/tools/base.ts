export interface ToolParameter {
  type: string;
  description: string;
  required?: boolean;
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, ToolParameter>;
}

export interface ToolResult {
  success: boolean;
  output: string;
  error?: string;
}

export interface Tool {
  definition: ToolDefinition;
  execute(params: Record<string, unknown>): Promise<ToolResult>;
}
