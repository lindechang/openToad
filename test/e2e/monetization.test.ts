import { test, expect, describe } from 'vitest';
import { AdManager } from '../../packages/monetization/src/index.js';
import { AdMobProvider } from '../../packages/monetization/src/ad-plugins/admob.js';

describe('Monetization E2E', () => {
  test('should create AdManager instance', () => {
    const adManager = new AdManager();
    expect(adManager).toBeDefined();
    expect(adManager.getProviders()).toContain('admob');
    expect(adManager.getProviders()).toContain('union');
  });

  test('should load ad config', async () => {
    const provider = new AdMobProvider();
    const ad = await provider.loadAd({
      appId: 'test-app-id',
      adUnitId: 'test-ad-unit'
    });
    
    expect(ad).toBeDefined();
    expect(ad.type).toBe('banner');
  });
});
