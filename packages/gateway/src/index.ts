import http from 'node:http';
import { createAgent, type Message } from 'opentoad';
import { AdManager } from '@opentoad/monetization';

const PORT = parseInt(process.env.PORT || '18789');

const agent = createAgent({ name: 'OpenToad' });
const adManager = new AdManager();

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url || '/', `http://localhost:${PORT}`);
    
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    if (url.pathname === '/') {
      res.end(JSON.stringify({
        name: 'OpenToad Gateway',
        version: '1.0.0',
        status: 'running'
      }));
      return;
    }
    
    if (url.pathname === '/health') {
      res.end(JSON.stringify({ status: 'ok', timestamp: Date.now() }));
      return;
    }
    
    if (url.pathname === '/channels') {
      res.end(JSON.stringify({
        channels: ['web', 'wechat', 'telegram', 'discord', 'slack']
      }));
      return;
    }
    
    if (url.pathname === '/monetization/providers') {
      res.end(JSON.stringify({
        providers: adManager.getProviders()
      }));
      return;
    }
    
    if (url.pathname === '/message' && req.method === 'POST') {
      let body = '';
      for await (const chunk of req) {
        body += chunk;
      }
      const data = JSON.parse(body);
      
      const message: Message = {
        id: `msg-${Date.now()}`,
        channel: data.channel || 'web',
        from: 'user',
        to: 'OpenToad',
        content: data.content,
        type: 'text',
        timestamp: Date.now()
      };
      
      agent.emit('message', message);
      
      res.end(JSON.stringify({ success: true, messageId: message.id }));
      return;
    }
    
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  } catch (error) {
    console.error('Server error:', error);
    res.writeHead(500);
    res.end(JSON.stringify({ error: 'Internal server error' }));
  }
});

agent.on('message', async (message: Message) => {
  console.log(`[Agent] Received message: ${message.content.substring(0, 50)}...`);
});

server.listen(PORT, () => {
  console.log(`
🚀 OpenToad Gateway Starting...
   Port: ${PORT}
   Channels: web, wechat, telegram, discord
   Monetization: ${adManager.getProviders().join(', ')}
   Server running at http://localhost:${PORT}
`);
});