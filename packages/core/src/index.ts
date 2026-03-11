import { EventEmitter } from 'events';

export interface Message {
  id: string;
  channel: string;
  from: string;
  to: string;
  content: string;
  type: 'text' | 'image' | 'voice' | 'audio' | 'video';
  timestamp: number;
  raw?: unknown;
}

export interface Channel {
  name: string;
  start(config: ChannelConfig, handler: (msg: Message) => Promise<void>): Promise<void>;
  send(message: Message): Promise<void>;
  stop(): Promise<void>;
}

export interface ChannelConfig {
  token?: string;
  apiKey?: string;
  appId?: string;
  [key: string]: unknown;
}

export interface AgentConfig {
  name: string;
  model?: string;
  systemPrompt?: string;
  maxTokens?: number;
  temperature?: number;
}

export class Agent extends EventEmitter {
  private channels: Map<string, Channel> = new Map();
  private running: boolean = false;

  constructor(private config: AgentConfig) {
    super();
  }

  registerChannel(channel: Channel): void {
    this.channels.set(channel.name, channel);
  }

  async startChannel(name: string, config: ChannelConfig): Promise<void> {
    const channel = this.channels.get(name);
    if (!channel) {
      throw new Error(`Channel ${name} not registered`);
    }
    await channel.start(config, this.handleMessage.bind(this));
  }

  private async handleMessage(message: Message): Promise<void> {
    this.emit('message', message);
  }

  async sendMessage(channelName: string, to: string, content: string): Promise<void> {
    const channel = this.channels.get(channelName);
    if (!channel) {
      throw new Error(`Channel ${channelName} not found`);
    }

    const message: Message = {
      id: `msg-${Date.now()}`,
      channel: channelName,
      from: this.config.name,
      to,
      content,
      type: 'text',
      timestamp: Date.now()
    };

    await channel.send(message);
  }

  async stop(): Promise<void> {
    this.running = false;
    for (const channel of this.channels.values()) {
      await channel.stop();
    }
  }

  isRunning(): boolean {
    return this.running;
  }
}

export function createAgent(config: AgentConfig): Agent {
  return new Agent(config);
}

export interface ChannelPlugin {
  name: string;
  send(message: Message, credentials: ChannelCredentials): Promise<void>;
  startPolling(credentials: ChannelCredentials, handler: (message: Message) => Promise<void>): Promise<void>;
  stopPolling(): Promise<void>;
}

export type ChannelCredentials = Record<string, unknown>;

export interface PluginContext {
  registerChannel(plugin: ChannelPlugin): void;
  getConfig(key: string): unknown;
}