import type { ChannelPlugin, Message, ChannelCredentials } from 'openclaw/plugin-sdk';

export interface WeChatCredentials {
  appId: string;
  appSecret: string;
  token: string;
  encodingAESKey?: string;
}

export interface WeChatMessage {
  msgId: string;
  fromUserName: string;
  createTime: number;
  msgType: string;
  content: string;
  event?: string;
}

export const wechatChannel: ChannelPlugin = {
  name: 'wechat',
  
  async send(message: Message, channel: ChannelCredentials): Promise<void> {
    const creds = channel as WeChatCredentials;
    const accessToken = await getAccessToken(creds);
    
    await fetch(`https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=${accessToken}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        touser: message.channelId,
        msgtype: 'text',
        text: { content: message.content }
      })
    });
  },

  async startPolling(credentials: ChannelCredentials, handler: (message: Message) => Promise<void>): Promise<void> {
    const creds = credentials as WeChatCredentials;
    const server = createWebServer(creds, handler);
    await server.start();
  },

  async stopPolling(): Promise<void> {
  }
};

async function getAccessToken(creds: WeChatCredentials): Promise<string> {
  const response = await fetch(
    `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${creds.appId}&secret=${creds.appSecret}`
  );
  const data = await response.json() as { access_token?: string; errmsg?: string };
  if (!data.access_token) throw new Error(data.errmsg || 'Failed to get access token');
  return data.access_token;
}

function createWebServer(creds: WeChatCredentials, handler: (message: Message) => Promise<void>) {
  return {
    async start() {
      console.log('[WeChat] Channel polling started');
    }
  };
}