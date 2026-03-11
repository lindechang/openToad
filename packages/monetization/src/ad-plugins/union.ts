import type { AdProvider, AdConfig, AdUnit } from './admob';

export class UnionAdProvider implements AdProvider {
  name = 'union';

  private configs: Map<string, AdConfig> = new Map();

  isSupported(): boolean {
    return typeof window !== 'undefined';
  }

  async loadAd(config: AdConfig): Promise<AdUnit> {
    this.configs.set(config.adUnitId, config);

    return {
      id: config.adUnitId,
      type: 'banner',
      loaded: true
    };
  }

  async showAd(unit: AdUnit): Promise<void> {
    const config = this.configs.get(unit.id);
    if (config) {
      console.log('[UnionAd] Showing ad from:', config.appId);
    }
  }
}