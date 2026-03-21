import Database from "better-sqlite3";
import path from "path";

const DB_PATH = path.join(process.cwd(), "data", "waitlist.db");

let db: Database.Database | null = null;

function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma("journal_mode = WAL");
    db.exec(`
      CREATE TABLE IF NOT EXISTS waitlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        source TEXT DEFAULT 'landing'
      )
    `);
  }
  return db;
}

export function addToWaitlist(
  email: string,
  source = "landing"
): { success: boolean; message: string } {
  const database = getDb();
  try {
    database
      .prepare("INSERT INTO waitlist (email, source) VALUES (?, ?)")
      .run(email, source);
    return { success: true, message: "You're on the list!" };
  } catch (e: unknown) {
    if (
      e instanceof Error &&
      "code" in e &&
      (e as { code: string }).code === "SQLITE_CONSTRAINT_UNIQUE"
    ) {
      return { success: true, message: "You're already on the list!" };
    }
    throw e;
  }
}

export function getWaitlistCount(): number {
  const database = getDb();
  const row = database
    .prepare("SELECT COUNT(*) as count FROM waitlist")
    .get() as { count: number };
  return row.count;
}
