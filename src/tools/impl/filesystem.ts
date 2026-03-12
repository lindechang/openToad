import { readFile, writeFile, mkdir, readdir } from 'fs/promises';
import { existsSync } from 'fs';
import type { Tool, ToolResult } from '../base.js';

export const filesystemTool: Tool = {
  definition: {
    name: 'filesystem',
    description: 'Read, write, or list files',
    parameters: {
      action: {
        type: 'string',
        description: 'Action: read, write, list',
        required: true
      },
      path: {
        type: 'string',
        description: 'File path',
        required: true
      },
      content: {
        type: 'string',
        description: 'Content to write (for write action)',
        required: false
      }
    }
  },
  
  async execute(params: Record<string, unknown>): Promise<ToolResult> {
    const action = params.action as string;
    const path = params.path as string;
    
    try {
      switch (action) {
        case 'read':
          if (!existsSync(path)) {
            return { success: false, output: '', error: 'File not found' };
          }
          const content = await readFile(path, 'utf-8');
          return { success: true, output: content };
          
        case 'write':
          await writeFile(path, params.content as string);
          return { success: true, output: 'File written' };
          
        case 'list':
          const files = await readdir(path);
          return { success: true, output: files.join('\n') };
          
        default:
          return { success: false, output: '', error: 'Unknown action' };
      }
    } catch (error: unknown) {
      const err = error as Error;
      return { success: false, output: '', error: err.message };
    }
  }
};
