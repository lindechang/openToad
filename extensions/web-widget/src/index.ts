import type { ChannelPlugin, Message, ChannelCredentials } from 'openclaw/plugin-sdk';
import { Hono } from 'hono';

export interface WebWidgetCredentials {
  port?: number;
  apiKey?: string;
}

export const webWidgetChannel: ChannelPlugin = {
  name: 'web-widget',
  
  async send(message: Message): Promise<void> {
    console.log(`[Web Widget] Sending message: ${message.content.substring(0, 50)}...`);
  },

  async startPolling(credentials: ChannelCredentials, handler: (message: Message) => Promise<void>): Promise<void> {
    const creds = credentials as WebWidgetCredentials;
    const port = creds.port || 8080;
    
    const app = new Hono();
    
    app.post('/webhook', async (c) => {
      const body = await c.req.json() as { message?: string; sessionId?: string };
      const message: Message = {
        id: crypto.randomUUID(),
        content: body.message || '',
        channelId: body.sessionId || 'anonymous',
        timestamp: Date.now()
      };
      await handler(message);
      return c.json({ status: 'ok' });
    });

    app.get('/health', (c) => c.json({ status: 'ok' }));

    console.log(`[Web Widget] Server starting on port ${port}`);
    
    const server = Bun?.serve?.({
      port,
      fetch: app.fetch
    });
    
    if (server) {
      console.log(`[Web Widget] Server running at http://localhost:${server.port}`);
    }
  },

  async stopPolling(): Promise<void> {
    console.log('[Web Widget] Server stopped');
  }
};