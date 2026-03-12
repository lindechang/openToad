import type { Task, TaskSubmission, TaskFilter } from './types';

export class TaskMarket {
  private tasks: Map<string, Task> = new Map();

  async listTasks(filter: TaskFilter): Promise<Task[]> {
    let result = Array.from(this.tasks.values());

    if (filter.userId) {
      result = result.filter(t => t.userId === filter.userId);
    }
    if (filter.status) {
      result = result.filter(t => t.status === filter.status);
    }
    if (filter.type) {
      result = result.filter(t => t.type === filter.type);
    }

    return result.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async getTask(id: string): Promise<Task | null> {
    return this.tasks.get(id) || null;
  }

  async createTask(task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>): Promise<Task> {
    const newTask: Task = {
      ...task,
      id: crypto.randomUUID(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    this.tasks.set(newTask.id, newTask);
    return newTask;
  }

  async submitTask(submission: TaskSubmission): Promise<Task> {
    const task = this.tasks.get(submission.taskId);
    if (!task) {
      throw new Error(`Task ${submission.taskId} not found`);
    }

    if (task.status !== 'pending') {
      throw new Error(`Task ${submission.taskId} is not pending`);
    }

    task.status = 'completed';
    task.updatedAt = new Date();
    this.tasks.set(task.id, task);

    return task;
  }

  async getReward(taskId: string): Promise<number> {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }
    return task.status === 'completed' ? task.reward : 0;
  }
}

export * from './types';