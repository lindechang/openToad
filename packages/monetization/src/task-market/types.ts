export interface Task {
  id: string;
  type: 'survey' | 'purchase' | 'booking';
  title: string;
  description: string;
  reward: number;
  status: 'pending' | 'completed' | 'failed';
  userId: string;
  metadata: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskSubmission {
  taskId: string;
  answers?: Record<string, string>;
  proof?: string;
}

export interface TaskFilter {
  userId?: string;
  status?: Task['status'];
  type?: Task['type'];
}