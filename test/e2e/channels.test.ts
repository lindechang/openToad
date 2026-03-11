import { test, expect, describe, vi } from 'vitest';
import { wechatChannel } from '../../extensions/wechat/src/index.js';

describe('Channels E2E', () => {
  test('should have wechat channel defined', () => {
    expect(wechatChannel.name).toBe('wechat');
    expect(wechatChannel.send).toBeDefined();
    expect(wechatChannel.startPolling).toBeDefined();
  });

  test('should send message without error', async () => {
    const mockMessage = {
      id: 'test-123',
      content: 'Hello',
      channelId: 'user123',
      timestamp: Date.now()
    };

    const mockCredentials = {
      appId: 'test-app-id',
      appSecret: 'test-secret',
      token: 'test-token'
    };

    await expect(
      wechatChannel.send(mockMessage, mockCredentials as any)
    ).resolves.not.toThrow();
  });
});
