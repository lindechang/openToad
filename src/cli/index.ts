#!/usr/bin/env node
import { createInterface } from 'readline';
import { createProvider } from '../providers/index.js';
import { Agent } from '../agent/run.js';
import { registerDefaultTools } from '../tools/index.js';
import { handleInput, printWelcome, printResponse } from './io.js';

registerDefaultTools();

const provider = createProvider(
  process.env.PROVIDER || 'anthropic',
  process.env.API_KEY || ''
);

const agent = new Agent(provider, {
  model: process.env.MODEL || 'claude-3-5-sonnet-20241022',
  temperature: 0.7,
  maxIterations: 10
});

printWelcome();

const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: '> '
});

rl.prompt();

rl.on('line', async (line) => {
  const input = line.trim();
  if (!input) {
    rl.prompt();
    return;
  }
  
  if (input === 'exit' || input === 'quit') {
    rl.close();
    return;
  }
  
  const response = await agent.run(input);
  printResponse(response);
  rl.prompt();
});

rl.on('close', () => {
  console.log('\nGoodbye!');
});
