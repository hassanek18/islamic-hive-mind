import path from 'path';

export interface QueryResult<T> {
  rows: T[];
}

export interface Database {
  query<T = any>(sql: string, params?: any[]): Promise<QueryResult<T>>;
  queryOne<T = any>(sql: string, params?: any[]): Promise<T | null>;
  execute(sql: string, params?: any[]): Promise<void>;
}

function createLocalDb(dbPath: string): Database {
  const BetterSqlite3 = require('better-sqlite3');
  const db = new BetterSqlite3(dbPath, { readonly: true });
  db.pragma('journal_mode = WAL');

  return {
    async query<T>(sql: string, params?: any[]) {
      const stmt = db.prepare(sql);
      const rows = params && params.length > 0 ? stmt.all(...params) : stmt.all();
      return { rows: rows as T[] };
    },
    async queryOne<T>(sql: string, params?: any[]) {
      const stmt = db.prepare(sql);
      const row = params && params.length > 0 ? stmt.get(...params) : stmt.get();
      return (row as T) || null;
    },
    async execute(sql: string, params?: any[]) {
      const stmt = db.prepare(sql);
      if (params && params.length > 0) {
        stmt.run(...params);
      } else {
        stmt.run();
      }
    },
  };
}

function createTursoDb(url: string, authToken: string): Database {
  const { createClient } = require('@libsql/client');
  const client = createClient({ url, authToken });

  return {
    async query<T>(sql: string, params?: any[]) {
      const result = await client.execute({ sql, args: params || [] });
      return { rows: result.rows as T[] };
    },
    async queryOne<T>(sql: string, params?: any[]) {
      const result = await client.execute({ sql, args: params || [] });
      return (result.rows[0] as T) || null;
    },
    async execute(sql: string, params?: any[]) {
      await client.execute({ sql, args: params || [] });
    },
  };
}

let dbInstance: Database | null = null;

export function getDb(): Database {
  if (dbInstance) return dbInstance;

  if (process.env.TURSO_DATABASE_URL && process.env.TURSO_AUTH_TOKEN) {
    dbInstance = createTursoDb(
      process.env.TURSO_DATABASE_URL,
      process.env.TURSO_AUTH_TOKEN
    );
  } else {
    const dbPath = path.join(process.cwd(), '..', 'db', 'hive-mind.db');
    dbInstance = createLocalDb(dbPath);
  }

  return dbInstance;
}
