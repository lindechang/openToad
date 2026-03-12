import { subscriptionPlans, type Subscription, type SubscriptionPlan } from './plans';

export class SubscriptionService {
  private subscriptions: Map<string, Subscription> = new Map();

  async getSubscription(userId: string): Promise<Subscription | null> {
    return Array.from(this.subscriptions.values())
      .find(s => s.userId === userId && s.status === 'active') || null;
  }

  async checkAccess(userId: string, feature: string): Promise<boolean> {
    const sub = await this.getSubscription(userId);
    
    if (!sub) {
      const plan = subscriptionPlans.free;
      return plan.features.includes(feature);
    }

    const plan = subscriptionPlans[sub.planId];
    return plan?.features.includes(feature) || false;
  }

  async checkLimit(userId: string, limitType: string): Promise<boolean> {
    const sub = await this.getSubscription(userId);
    const plan = sub ? subscriptionPlans[sub.planId] : subscriptionPlans.free;
    
    const limit = plan.limits[limitType as keyof typeof plan.limits];
    return limit === undefined || limit > 0;
  }

  async createCheckoutSession(userId: string, planId: string): Promise<string> {
    const plan = subscriptionPlans[planId];
    if (!plan) {
      throw new Error(`Plan ${planId} not found`);
    }

    const sessionId = crypto.randomUUID();
    return `/checkout/${sessionId}?plan=${planId}`;
  }

  async createSubscription(userId: string, planId: string, months: number = 1): Promise<Subscription> {
    const plan = subscriptionPlans[planId];
    if (!plan) {
      throw new Error(`Plan ${planId} not found`);
    }

    const subscription: Subscription = {
      id: crypto.randomUUID(),
      userId,
      planId,
      status: 'active',
      expiresAt: new Date(Date.now() + months * 30 * 24 * 60 * 60 * 1000),
      createdAt: new Date()
    };

    this.subscriptions.set(subscription.id, subscription);
    return subscription;
  }

  getPlan(planId: string): SubscriptionPlan | undefined {
    return subscriptionPlans[planId];
  }

  getAllPlans(): SubscriptionPlan[] {
    return Object.values(subscriptionPlans);
  }
}

export { subscriptionPlans };
export type { Subscription, SubscriptionPlan } from './plans';