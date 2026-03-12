export interface DatabaseConfig {
  url: string;
}

export class Database {
  private connected: boolean = false;

  async connect(config: DatabaseConfig): Promise<void> {
    console.log(`[Database] Connecting to ${config.url}`);
    this.connected = true;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }
}

export const database = new Database();

export async function connectDatabase(): Promise<void> {
  await database.connect({ url: process.env.DATABASE_URL || 'postgresql://localhost:5432/opentoad' });
}

export async function disconnectDatabase(): Promise<void> {
  await database.disconnect();
}