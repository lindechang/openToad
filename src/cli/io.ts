export function printWelcome(): void {
  console.log(`
╔════════════════════════════════════════╗
║         OpenToad 🐸                     ║
║    Self-Sustainable AI Assistant        ║
╚════════════════════════════════════════╝

Type your message and press Enter.
Commands: exit, quit
`);
}

export function printResponse(content: string): void {
  console.log('\n' + content + '\n');
}

export async function handleInput(rl: ReturnType<typeof createInterface>): Promise<string> {
  return new Promise((resolve) => {
    rl.question('> ', (answer: string) => {
      resolve(answer);
    });
  });
}

import { createInterface } from 'readline';
