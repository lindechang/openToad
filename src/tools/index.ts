import { globalTools } from './registry.js';
import { shellTool } from './impl/shell.js';
import { filesystemTool } from './impl/filesystem.js';

export function registerDefaultTools(): void {
  globalTools.register(shellTool);
  globalTools.register(filesystemTool);
}

export * from './base.js';
export * from './registry.js';
