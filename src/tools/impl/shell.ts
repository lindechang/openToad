import { exec } from 'child_process';
import { promisify } from 'util';
import type { Tool, ToolResult } from '../base.js';

const execAsync = promisify(exec);

export const shellTool: Tool = {
  definition: {
    name: 'shell',
    description: 'Execute shell commands',
    parameters: {
      command: {
        type: 'string',
        description: 'The shell command to execute',
        required: true
      }
    }
  },
  
  async execute(params: Record<string, unknown>): Promise<ToolResult> {
    const command = params.command as string;
    try {
      const { stdout, stderr } = await execAsync(command, { timeout: 30000 });
      return {
        success: true,
        output: stdout || stderr
      };
    } catch (error: unknown) {
      const err = error as Error;
      return {
        success: false,
        output: '',
        error: err.message
      };
    }
  }
};
