export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  features: string[];
  limits: {
    messagesPerDay?: number;
    channels?: number;
  };
}

export const subscriptionPlans: Record<string, SubscriptionPlan> = {
  free: {
    id: 'free',
    name: '免费版',
    price: 0,
    features: ['基础 AI 对话', '广告展示'],
    limits: { messagesPerDay: 50, channels: 1 }
  },
  premium: {
    id: 'premium',
    name: '高级版',
    price: 9.9,
    features: ['无限制对话', '无广告', '高级插件', '优先支持'],
    limits: {}
  },
  enterprise: {
    id: 'enterprise',
    name: '企业版',
    price: 99,
    features: ['无限制对话', '无广告', '所有插件', '专属支持', '自定义集成'],
    limits: {}
  }
};

export interface Subscription {
  id: string;
  userId: string;
  planId: string;
  status: 'active' | 'expired' | 'cancelled';
  expiresAt: Date;
  createdAt: Date;
}