export interface AdProvider {
  name: string;
  isSupported(): boolean;
  loadAd(config: AdConfig): Promise<AdUnit>;
  showAd(unit: AdUnit): Promise<void>;
}

export interface AdConfig {
  appId: string;
  adUnitId: string;
}

export interface AdUnit {
  id: string;
  type: 'banner' | 'interstitial' | 'rewarded';
  loaded: boolean;
}

export class AdMobProvider implements AdProvider {
  name = 'admob';

  isSupported(): boolean {
    if (typeof globalThis === 'undefined') return false;
    const window = globalThis as any;
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
        const window = globalThis as any;
        window.google = window.google || {};
        window.google.adsbygoogle = window.google.adsbygoogle || [];
        window.google.adsbygoogle.push({
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