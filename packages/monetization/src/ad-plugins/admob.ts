import type { AdProvider, AdConfig, AdUnit } from './admob';

export class AdMobProvider implements AdProvider {
  name = 'admob';

  isSupported(): boolean {
    return typeof window !== 'undefined' && !!window.google?.adsbygoogle;
  }

  async loadAd(config: AdConfig): Promise<AdUnit> {
    if (!this.isSupported()) {
      console.warn('[AdMob] Google Ads not available');
      return { id: '', type: 'banner', loaded: false };
    }

    return new Promise((resolve) => {
      const adUnit: AdUnit = {
        id: config.adUnitId,
        type: 'banner',
        loaded: false
      };

      try {
        (window.google as any).adsbygoogle = (window.google as any).adsbygoogle || [];
        (window.google as any).adsbygoogle.push({
          adUnitId: config.adUnitId,
          adSize: 'BANNER',
          elementId: `admob-${config.adUnitId}`,
          onload: () => {
            adUnit.loaded = true;
            resolve(adUnit);
          }
        });
      } catch (e) {
        console.error('[AdMob] Failed to load ad:', e);
        resolve(adUnit);
      }
    });
  }

  async showAd(unit: AdUnit): Promise<void> {
    if (unit.loaded) {
      console.log('[AdMob] Showing ad:', unit.id);
    }
  }
}

declare global {
  interface Window {
    google: any;
    adsbygoogle: any[];
  }
}