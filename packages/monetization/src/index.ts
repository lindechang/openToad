import type { AdProvider, AdConfig, AdUnit } from './ad-plugins/admob';
import { AdMobProvider } from './ad-plugins/admob';
import { UnionAdProvider } from './ad-plugins/union';

export class AdManager {
  private providers: Map<string, AdProvider> = new Map();

  constructor() {
    this.registerProvider(new AdMobProvider());
    this.registerProvider(new UnionAdProvider());
  }

  registerProvider(provider: AdProvider): void {
    this.providers.set(provider.name, provider);
  }

  async showAd(providerName: string, config: AdConfig): Promise<void> {
    const provider = this.providers.get(providerName);
    if (!provider) {
      throw new Error(`Provider ${providerName} not found`);
    }

    if (!provider.isSupported()) {
      console.warn(`[AdManager] Provider ${providerName} not supported in this environment`);
      return;
    }

    const ad = await provider.loadAd(config);
    await provider.showAd(ad);
  }

  getProviders(): string[] {
    return Array.from(this.providers.keys());
  }
}

export { AdMobProvider, UnionAdProvider };
export type { AdProvider, AdConfig, AdUnit } from './ad-plugins/admob';