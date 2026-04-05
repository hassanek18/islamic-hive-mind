# Foundation + AI Chatbot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Next.js web app with Quran reader pages, API layer, and Claude-powered chatbot on top of the existing SQLite Quran corpus.

**Architecture:** Next.js 14 App Router in `web/` subdirectory. better-sqlite3 for local dev, Turso for prod, unified behind async DB abstraction. Claude API with RAG pipeline (keyword intent classification → DB query → context enrichment → streaming response).

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, Framer Motion, better-sqlite3, @libsql/client, @anthropic-ai/sdk, Vercel AI SDK

**Spec:** `docs/superpowers/specs/2026-04-05-foundation-chatbot-design.md`

**Database:** `db/hive-mind.db` — 114 surahs, 6,236 ayat, 77,429 words, 325,665 letters (verified 2026-04-05)

---

## File Map

```
web/
├── app/
│   ├── layout.tsx                              ← Root layout, fonts, metadata, error boundary
│   ├── page.tsx                                ← Landing page
│   ├── globals.css                             ← Tailwind + custom CSS vars
│   ├── error.tsx                               ← App-level error boundary UI
│   ├── quran/
│   │   ├── page.tsx                            ← Surah list (114 cards)
│   │   └── [id]/
│   │       └── page.tsx                        ← Individual surah (all verses)
│   ├── ask/
│   │   └── page.tsx                            ← Full-page chat experience
│   └── api/
│       ├── chat/
│       │   └── route.ts                        ← POST: streaming chat with RAG
│       └── quran/
│           ├── surah/[id]/route.ts             ← GET: surah + verses
│           ├── verse/[surah]/[verse]/route.ts  ← GET: single verse + words
│           └── search/route.ts                 ← GET: search by root/english
├── components/
│   ├── chat/
│   │   ├── ChatPanel.tsx                       ← Slide-out panel
│   │   ├── ChatMessage.tsx                     ← Message bubble
│   │   ├── ChatInput.tsx                       ← Input + send
│   │   ├── FloatingChatButton.tsx              ← Bottom-right button
│   │   ├── SuggestedQuestions.tsx               ← Starter chips
│   │   └── ChatErrorBoundary.tsx               ← Chat-specific error boundary
│   ├── quran/
│   │   ├── QuranVerse.tsx                      ← Arabic + translit + English
│   │   └── SurahCard.tsx                       ← Card for surah list
│   ├── layout/
│   │   ├── Header.tsx                          ← Nav with coming-soon links
│   │   └── Footer.tsx                          ← Footer
│   └── ui/
│       ├── Button.tsx                          ← Primary/secondary buttons
│       ├── Card.tsx                            ← Base card component
│       ├── ConfidenceTier.tsx                  ← Tier 1-6 badge
│       └── LoadingDots.tsx                     ← Chat typing indicator
├── lib/
│   ├── db.ts                                   ← Unified async DB abstraction
│   ├── quran.ts                                ← Query functions
│   ├── chat-context.ts                         ← Intent classifier + RAG pipeline
│   └── prompts.ts                              ← System prompt
├── hooks/
│   └── useChat.ts                              ← Chat state + streaming hook
├── types/
│   └── index.ts                                ← All TypeScript interfaces
├── public/
│   └── fonts/
│       ├── Amiri-Regular.woff2
│       ├── Amiri-Bold.woff2
│       └── OFL.txt                             ← SIL Open Font License
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.local
```

---

### Task 1: Scaffold Next.js App

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/next.config.ts`
- Create: `web/tailwind.config.ts`
- Create: `web/app/globals.css`
- Create: `web/.env.local`

- [ ] **Step 1: Create web directory and initialize Next.js**

```bash
cd /c/Users/hassa/islamic-hive-mind
mkdir web && cd web
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm
```

When prompted: Accept defaults. This creates the Next.js 14 app with App Router.

- [ ] **Step 2: Install project dependencies**

```bash
cd /c/Users/hassa/islamic-hive-mind/web
npm install better-sqlite3 @libsql/client @anthropic-ai/sdk ai framer-motion
npm install -D @types/better-sqlite3
```

- [ ] **Step 3: Create .env.local**

Create `web/.env.local`:
```env
ANTHROPIC_API_KEY=sk-ant-PLACEHOLDER
```

- [ ] **Step 4: Configure tailwind.config.ts with design system colors**

Replace `web/tailwind.config.ts`:
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0a0e1a',
        'bg-secondary': '#111827',
        'bg-chat': '#1a1f35',
        'accent-gold': '#d4a843',
        'accent-gold-dim': '#b8942f',
        'text-primary': '#f5f0e8',
        'text-secondary': '#9ca3af',
        'text-arabic': '#ffffff',
        'border-subtle': '#1e293b',
      },
      fontFamily: {
        amiri: ['Amiri', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      maxWidth: {
        'content': '1200px',
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 5: Set up globals.css with CSS variables and base styles**

Replace `web/app/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-chat: #1a1f35;
    --accent-gold: #d4a843;
    --accent-gold-dim: #b8942f;
    --text-primary: #f5f0e8;
    --text-secondary: #9ca3af;
  }

  body {
    @apply bg-bg-primary text-text-primary;
    font-family: 'Inter', system-ui, sans-serif;
  }

  /* Arabic text blocks: always isolated, RTL, generous line-height */
  .arabic-text {
    font-family: 'Amiri', serif;
    direction: rtl;
    text-align: right;
    line-height: 2.2em;
    color: white;
  }
}
```

- [ ] **Step 6: Update next.config.ts for external packages**

Replace `web/next.config.ts`:
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["better-sqlite3"],
};

export default nextConfig;
```

- [ ] **Step 7: Download Amiri font and OFL license**

```bash
cd /c/Users/hassa/islamic-hive-mind/web
mkdir -p public/fonts
curl -L "https://github.com/aliftype/amiri/releases/download/1.000/Amiri-1.000.zip" -o /tmp/amiri.zip
# If the zip download doesn't work, use npm:
npm install @fontsource/amiri
cp node_modules/@fontsource/amiri/files/amiri-latin-400-normal.woff2 public/fonts/Amiri-Regular.woff2 2>/dev/null || echo "Will use Google Fonts fallback"
```

Create `web/public/fonts/OFL.txt`:
```
Copyright 2010-2023 Khaled Hosny (khaled@aliftype.com)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
```

- [ ] **Step 8: Verify the app starts**

```bash
cd /c/Users/hassa/islamic-hive-mind/web
npm run dev
```

Expected: Next.js dev server starts on http://localhost:3000 with the default page.

- [ ] **Step 9: Commit**

```bash
cd /c/Users/hassa/islamic-hive-mind
git add web/
git commit -m "feat: scaffold Next.js app with Tailwind, design system colors, Amiri font"
```

---

### Task 2: TypeScript Types

**Files:**
- Create: `web/types/index.ts`

- [ ] **Step 1: Write all TypeScript interfaces matching the SQLite schema exactly**

Create `web/types/index.ts`:
```typescript
// Types matching db/hive-mind.db schema exactly
// Verified against PRAGMA table_info() on 2026-04-05

export interface Surah {
  id: number;
  name_arabic: string;
  name_english: string;
  name_transliteration: string;
  revelation_type: 'meccan' | 'medinan';
  revelation_order: number | null;
  verse_count: number;
  word_count: number | null;
  letter_count: number | null;
  bismillah: boolean;
}

export interface Ayah {
  id: number;
  surah_id: number;
  verse_number: number;
  text_arabic: string;
  text_arabic_simple: string;
  text_english: string | null;
  text_transliteration: string | null;
  word_count: number | null;
  letter_count: number | null;
  letter_count_no_spaces: number | null;
  abjad_value: number | null;
  juz: number | null;
  hizb: number | null;
  page: number | null;
  sajdah: boolean;
}

export interface Word {
  id: number;
  ayah_id: number;
  surah_id: number;
  verse_number: number;
  word_position: number;
  text_arabic: string;
  text_simple: string;
  text_english: string | null;
  text_transliteration: string | null;
  root: string | null;
  lemma: string | null;
  part_of_speech: string | null;
  morphology: string | null;
  abjad_value: number | null;
  letter_count: number | null;
}

export interface Pattern {
  id: number;
  name: string;
  category: string;
  description: string;
  claim: string | null;
  method: string | null;
  result: string | null;
  verified: boolean;
  significance: string | null;
  data: string | null;  // JSON string
  notes: string | null;
  source: string | null;
  discovered_at: string | null;
  scholarly_consensus: string | null;
}

export interface SearchResult {
  surah_id: number;
  verse_number: number;
  surah_name_english: string;
  surah_name_arabic: string;
  text_arabic: string;
  text_english: string | null;
  text_transliteration: string | null;
  match_context?: string;  // snippet around the match
}

export interface FrequencyResult {
  root: string;
  count: number;
  sample_verses: Ayah[];
}

export type IntentType =
  | 'verse_lookup'
  | 'word_query'
  | 'pattern_query'
  | 'surah_info'
  | 'story_request'
  | 'fiqh_ruling'
  | 'hadith_request'
  | 'general_islamic';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  model?: 'haiku' | 'sonnet';
}
```

- [ ] **Step 2: Commit**

```bash
git add web/types/
git commit -m "feat: add TypeScript types matching SQLite schema"
```

---

### Task 3: Database Abstraction Layer

**Files:**
- Create: `web/lib/db.ts`

- [ ] **Step 1: Build unified async DB abstraction**

Create `web/lib/db.ts`:
```typescript
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
  // Dynamic import to avoid bundling better-sqlite3 on client
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
```

- [ ] **Step 2: Verify DB connection works**

Create a quick test. Temporarily add to `web/app/page.tsx`:
```typescript
import { getDb } from '@/lib/db';

export default async function Home() {
  const db = getDb();
  const result = await db.queryOne<{ count: number }>('SELECT COUNT(*) as count FROM surahs');
  return <div>Surahs: {result?.count}</div>;
}
```

Run `cd web && npm run dev` — should show "Surahs: 114".

- [ ] **Step 3: Commit**

```bash
git add web/lib/db.ts
git commit -m "feat: add unified async database abstraction (better-sqlite3/Turso)"
```

---

### Task 4: Quran Query Functions

**Files:**
- Create: `web/lib/quran.ts`

- [ ] **Step 1: Build all query functions**

Create `web/lib/quran.ts`:
```typescript
import { getDb } from './db';
import type { Surah, Ayah, Word, Pattern, SearchResult, FrequencyResult } from '@/types';

export async function getSurah(id: number): Promise<Surah | null> {
  const db = getDb();
  return db.queryOne<Surah>('SELECT * FROM surahs WHERE id = ?', [id]);
}

export async function getSurahVerses(id: number): Promise<Ayah[]> {
  const db = getDb();
  const result = await db.query<Ayah>(
    'SELECT * FROM ayat WHERE surah_id = ? ORDER BY verse_number',
    [id]
  );
  return result.rows;
}

export async function getSurahStats(): Promise<Surah[]> {
  const db = getDb();
  const result = await db.query<Surah>(
    'SELECT * FROM surahs ORDER BY id'
  );
  return result.rows;
}

export async function getVerse(surah: number, verse: number): Promise<Ayah | null> {
  const db = getDb();
  return db.queryOne<Ayah>(
    'SELECT * FROM ayat WHERE surah_id = ? AND verse_number = ?',
    [surah, verse]
  );
}

export async function getVerseWords(surah: number, verse: number): Promise<Word[]> {
  const db = getDb();
  const result = await db.query<Word>(
    'SELECT * FROM words WHERE surah_id = ? AND verse_number = ? ORDER BY word_position',
    [surah, verse]
  );
  return result.rows;
}

export async function searchByRoot(root: string): Promise<SearchResult[]> {
  const db = getDb();
  const result = await db.query<SearchResult>(
    `SELECT w.surah_id, w.verse_number, s.name_english as surah_name_english,
            s.name_arabic as surah_name_arabic, a.text_arabic, a.text_english,
            a.text_transliteration
     FROM words w
     JOIN ayat a ON a.surah_id = w.surah_id AND a.verse_number = w.verse_number
     JOIN surahs s ON s.id = w.surah_id
     WHERE w.root = ?
     GROUP BY w.surah_id, w.verse_number
     ORDER BY w.surah_id, w.verse_number
     LIMIT 20`,
    [root]
  );
  return result.rows;
}

export async function searchByEnglish(query: string): Promise<SearchResult[]> {
  const db = getDb();
  const result = await db.query<SearchResult>(
    `SELECT a.surah_id, a.verse_number, s.name_english as surah_name_english,
            s.name_arabic as surah_name_arabic, a.text_arabic, a.text_english,
            a.text_transliteration
     FROM ayat a
     JOIN surahs s ON s.id = a.surah_id
     WHERE a.text_english LIKE ?
     ORDER BY a.surah_id, a.verse_number
     LIMIT 20`,
    [`%${query}%`]
  );
  return result.rows;
}

export async function getWordFrequency(root: string): Promise<FrequencyResult> {
  const db = getDb();
  const countResult = await db.queryOne<{ count: number }>(
    'SELECT COUNT(*) as count FROM words WHERE root = ?',
    [root]
  );

  const sampleResult = await db.query<Ayah>(
    `SELECT DISTINCT a.* FROM words w
     JOIN ayat a ON a.id = w.ayah_id
     WHERE w.root = ?
     LIMIT 5`,
    [root]
  );

  return {
    root,
    count: countResult?.count || 0,
    sample_verses: sampleResult.rows,
  };
}

export async function getPatterns(): Promise<Pattern[]> {
  const db = getDb();
  const result = await db.query<Pattern>('SELECT * FROM patterns ORDER BY category, name');
  return result.rows;
}

export async function getRandomVerse(): Promise<Ayah | null> {
  const db = getDb();
  // Pick from a curated set of beautiful/well-known verses
  const CURATED_VERSES = [
    [2, 255],   // Ayat al-Kursi
    [55, 13],   // Which of the favors of your Lord will you deny?
    [94, 5],    // Indeed, with hardship comes ease
    [3, 139],   // Do not weaken and do not grieve
    [2, 286],   // Allah does not burden a soul beyond its capacity
    [112, 1],   // Say: He is Allah, the One
    [93, 3],    // Your Lord has not abandoned you
    [49, 13],   // We created you from a male and female
    [21, 87],   // There is no deity except You; exalted are You
    [13, 28],   // Verily in the remembrance of Allah do hearts find rest
  ];
  const [surah, verse] = CURATED_VERSES[Math.floor(Math.random() * CURATED_VERSES.length)];
  return getVerse(surah, verse);
}
```

- [ ] **Step 2: Commit**

```bash
git add web/lib/quran.ts
git commit -m "feat: add Quran query functions (getSurah, search, frequency, etc.)"
```

---

### Task 5: API Routes

**Files:**
- Create: `web/app/api/quran/surah/[id]/route.ts`
- Create: `web/app/api/quran/verse/[surah]/[verse]/route.ts`
- Create: `web/app/api/quran/search/route.ts`

- [ ] **Step 1: Build surah API route**

Create `web/app/api/quran/surah/[id]/route.ts`:
```typescript
import { NextResponse } from 'next/server';
import { getSurah, getSurahVerses } from '@/lib/quran';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const surahId = parseInt(id, 10);

  if (isNaN(surahId) || surahId < 1 || surahId > 114) {
    return NextResponse.json({ error: 'Invalid surah ID. Must be 1-114.' }, { status: 400 });
  }

  const surah = await getSurah(surahId);
  if (!surah) {
    return NextResponse.json({ error: 'Surah not found.' }, { status: 404 });
  }

  const verses = await getSurahVerses(surahId);
  return NextResponse.json({ surah, verses });
}
```

- [ ] **Step 2: Build verse API route**

Create `web/app/api/quran/verse/[surah]/[verse]/route.ts`:
```typescript
import { NextResponse } from 'next/server';
import { getVerse, getVerseWords, getSurah } from '@/lib/quran';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ surah: string; verse: string }> }
) {
  const { surah: surahStr, verse: verseStr } = await params;
  const surahId = parseInt(surahStr, 10);
  const verseNum = parseInt(verseStr, 10);

  if (isNaN(surahId) || isNaN(verseNum)) {
    return NextResponse.json({ error: 'Invalid surah or verse number.' }, { status: 400 });
  }

  const surah = await getSurah(surahId);
  if (!surah) {
    return NextResponse.json({ error: 'Surah not found.' }, { status: 404 });
  }

  if (verseNum < 1 || verseNum > surah.verse_count) {
    return NextResponse.json({
      error: `Verse ${verseNum} does not exist in Surah ${surah.name_english}. This surah has ${surah.verse_count} verses.`
    }, { status: 404 });
  }

  const verse = await getVerse(surahId, verseNum);
  const words = await getVerseWords(surahId, verseNum);
  return NextResponse.json({ surah, verse, words });
}
```

- [ ] **Step 3: Build search API route**

Create `web/app/api/quran/search/route.ts`:
```typescript
import { NextResponse } from 'next/server';
import { searchByRoot, searchByEnglish } from '@/lib/quran';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q');
  const type = searchParams.get('type') || 'english';

  if (!query || query.trim().length === 0) {
    return NextResponse.json({ error: 'Query parameter "q" is required.' }, { status: 400 });
  }

  let results;
  if (type === 'root') {
    results = await searchByRoot(query.trim());
  } else {
    results = await searchByEnglish(query.trim());
  }

  return NextResponse.json({ results, count: results.length });
}
```

- [ ] **Step 4: Test all API routes**

```bash
cd /c/Users/hassa/islamic-hive-mind/web && npm run dev
# In another terminal:
curl http://localhost:3000/api/quran/surah/1 | head -c 500
curl http://localhost:3000/api/quran/verse/2/255 | head -c 500
curl "http://localhost:3000/api/quran/search?q=mercy&type=english" | head -c 500
```

Expected: JSON responses with Quran data.

- [ ] **Step 5: Commit**

```bash
git add web/app/api/
git commit -m "feat: add Quran API routes (surah, verse, search)"
```

---

### Task 6: QuranVerse and SurahCard Components

**Files:**
- Create: `web/components/quran/QuranVerse.tsx`
- Create: `web/components/quran/SurahCard.tsx`

- [ ] **Step 1: Build QuranVerse component**

Create `web/components/quran/QuranVerse.tsx`:
```tsx
import type { Ayah } from '@/types';

interface QuranVerseProps {
  verse: Ayah;
  showVerseNumber?: boolean;
  surahName?: string;
}

export default function QuranVerse({ verse, showVerseNumber = true, surahName }: QuranVerseProps) {
  return (
    <div className="py-6 border-b border-border-subtle last:border-b-0">
      {/* Verse number badge */}
      {showVerseNumber && (
        <div className="flex justify-center mb-4">
          <span className="inline-flex items-center justify-center w-10 h-10 rounded-full border-2 border-accent-gold text-accent-gold text-sm font-mono">
            {verse.verse_number}
          </span>
        </div>
      )}

      {/* Arabic text — isolated RTL block */}
      <div dir="rtl" className="arabic-text text-center text-2xl md:text-3xl text-white mb-4 px-4 leading-[2.2em]" style={{ fontFamily: "'Amiri', serif" }}>
        {verse.text_arabic}
      </div>

      {/* Transliteration */}
      {verse.text_transliteration && (
        <p className="text-center text-sm text-text-secondary italic mb-2 px-4">
          {verse.text_transliteration}
        </p>
      )}

      {/* English translation */}
      {verse.text_english && (
        <p className="text-center text-text-primary px-4 max-w-3xl mx-auto">
          {verse.text_english}
        </p>
      )}

      {/* Reference */}
      {surahName && (
        <p className="text-center text-xs text-text-secondary mt-2">
          {surahName} ({verse.surah_id}:{verse.verse_number})
        </p>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Build SurahCard component**

Create `web/components/quran/SurahCard.tsx`:
```tsx
import Link from 'next/link';
import type { Surah } from '@/types';

interface SurahCardProps {
  surah: Surah;
}

export default function SurahCard({ surah }: SurahCardProps) {
  return (
    <Link href={`/quran/${surah.id}`}>
      <div className="bg-bg-secondary border border-border-subtle rounded-xl p-6 hover:border-accent-gold/30 transition-colors cursor-pointer group">
        {/* Surah number */}
        <div className="flex items-start justify-between mb-3">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full border border-accent-gold/40 text-accent-gold text-xs font-mono">
            {surah.id}
          </span>
          <span className={`text-xs px-2 py-1 rounded-full ${
            surah.revelation_type === 'meccan'
              ? 'bg-teal-900/30 text-teal-400'
              : 'bg-amber-900/30 text-amber-400'
          }`}>
            {surah.revelation_type === 'meccan' ? 'Meccan' : 'Medinan'}
          </span>
        </div>

        {/* Arabic name */}
        <div dir="rtl" className="text-right text-xl text-white mb-1" style={{ fontFamily: "'Amiri', serif" }}>
          {surah.name_arabic}
        </div>

        {/* English name + transliteration */}
        <h3 className="text-text-primary font-semibold group-hover:text-accent-gold transition-colors">
          {surah.name_english}
        </h3>
        <p className="text-text-secondary text-sm">{surah.name_transliteration}</p>

        {/* Stats */}
        <p className="text-text-secondary text-xs mt-3">
          {surah.verse_count} verses
        </p>
      </div>
    </Link>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add web/components/quran/
git commit -m "feat: add QuranVerse and SurahCard components"
```

---

### Task 7: Quran Reader Pages (Server-Rendered)

**Files:**
- Create: `web/app/quran/page.tsx`
- Create: `web/app/quran/[id]/page.tsx`

- [ ] **Step 1: Build surah list page**

Create `web/app/quran/page.tsx`:
```tsx
import type { Metadata } from 'next';
import { getSurahStats } from '@/lib/quran';
import SurahCard from '@/components/quran/SurahCard';

export const metadata: Metadata = {
  title: 'Browse the Quran',
  description: 'Explore all 114 surahs of the Holy Quran with Arabic text, English translation, and transliteration.',
};

export default async function QuranPage() {
  const surahs = await getSurahStats();

  return (
    <main className="max-w-content mx-auto px-4 py-12">
      <h1 className="text-3xl font-semibold text-text-primary mb-2">The Holy Quran</h1>
      <p className="text-text-secondary mb-8">114 Surahs &middot; 6,236 Ayat &middot; Hafs &lsquo;an &lsquo;Asim</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {surahs.map((surah) => (
          <SurahCard key={surah.id} surah={surah} />
        ))}
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Build individual surah page with generateMetadata and generateStaticParams**

Create `web/app/quran/[id]/page.tsx`:
```tsx
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getSurah, getSurahVerses, getSurahStats } from '@/lib/quran';
import QuranVerse from '@/components/quran/QuranVerse';

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateStaticParams() {
  const surahs = await getSurahStats();
  return surahs.map((s) => ({ id: String(s.id) }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const surah = await getSurah(parseInt(id, 10));
  if (!surah) return { title: 'Surah Not Found' };

  return {
    title: `Surah ${surah.name_english} (${surah.name_transliteration})`,
    description: `Read Surah ${surah.name_english} — ${surah.verse_count} verses, ${surah.revelation_type}. Full Arabic text with English translation and transliteration.`,
  };
}

export default async function SurahPage({ params }: Props) {
  const { id } = await params;
  const surahId = parseInt(id, 10);
  const surah = await getSurah(surahId);

  if (!surah) notFound();

  const verses = await getSurahVerses(surahId);

  return (
    <main className="max-w-3xl mx-auto px-4 py-12">
      {/* Surah header */}
      <div className="text-center mb-10">
        <div dir="rtl" className="text-4xl text-white mb-2" style={{ fontFamily: "'Amiri', serif", lineHeight: '2.2em' }}>
          {surah.name_arabic}
        </div>
        <h1 className="text-2xl font-semibold text-text-primary">
          {surah.name_english}
        </h1>
        <p className="text-text-secondary">
          {surah.name_transliteration} &middot; {surah.verse_count} verses &middot;{' '}
          <span className={surah.revelation_type === 'meccan' ? 'text-teal-400' : 'text-amber-400'}>
            {surah.revelation_type === 'meccan' ? 'Meccan' : 'Medinan'}
          </span>
        </p>
      </div>

      {/* Bismillah — only if this surah has one */}
      {surah.bismillah && surah.id !== 1 && (
        <div dir="rtl" className="text-center text-2xl text-white mb-8 py-4" style={{ fontFamily: "'Amiri', serif", lineHeight: '2.2em' }}>
          بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
        </div>
      )}

      {/* All verses */}
      <div className="divide-y divide-border-subtle">
        {verses.map((verse) => (
          <QuranVerse key={verse.id} verse={verse} />
        ))}
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Verify pages render**

Navigate to http://localhost:3000/quran — should show 114 surah cards.
Navigate to http://localhost:3000/quran/1 — should show Al-Fatiha with 7 verses in Arabic.
Navigate to http://localhost:3000/quran/9 — should show At-Tawbah WITHOUT Bismillah.

- [ ] **Step 4: Commit**

```bash
git add web/app/quran/
git commit -m "feat: add Quran reader pages (surah list + individual surah)"
```

---

### Task 8: Layout, Header, Footer, Landing Page

**Files:**
- Create: `web/components/layout/Header.tsx`
- Create: `web/components/layout/Footer.tsx`
- Create: `web/components/ui/Button.tsx`
- Modify: `web/app/layout.tsx`
- Modify: `web/app/page.tsx`
- Create: `web/app/error.tsx`

- [ ] **Step 1: Build Header with coming-soon nav links**

Create `web/components/layout/Header.tsx`:
```tsx
import Link from 'next/link';

export default function Header() {
  return (
    <header className="border-b border-border-subtle bg-bg-primary/80 backdrop-blur-sm sticky top-0 z-40">
      <div className="max-w-content mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="text-accent-gold font-semibold text-lg">
          Islamic Hive Mind
        </Link>

        <nav className="flex items-center gap-6 text-sm">
          <Link href="/quran" className="text-text-primary hover:text-accent-gold transition-colors">
            Quran
          </Link>
          <span
            className="text-text-secondary cursor-default"
            title="Coming soon — we're crafting this section with care"
          >
            Stories
          </span>
          <span
            className="text-text-secondary cursor-default"
            title="Coming soon — we're crafting this section with care"
          >
            Discoveries
          </span>
          <Link href="/ask" className="text-accent-gold hover:text-accent-gold-dim transition-colors">
            Ask The Scholar
          </Link>
        </nav>
      </div>
    </header>
  );
}
```

- [ ] **Step 2: Build Footer**

Create `web/components/layout/Footer.tsx`:
```tsx
export default function Footer() {
  return (
    <footer className="border-t border-border-subtle mt-20 py-8">
      <div className="max-w-content mx-auto px-4 text-center text-text-secondary text-sm">
        <p>Islamic Hive Mind — A living Islamic knowledge base</p>
        <p className="mt-1 text-xs">Grounded in the Shia Twelver tradition. Built with taqwa.</p>
      </div>
    </footer>
  );
}
```

- [ ] **Step 3: Build Button component**

Create `web/components/ui/Button.tsx`:
```tsx
import Link from 'next/link';

interface ButtonProps {
  children: React.ReactNode;
  href?: string;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  className?: string;
}

export default function Button({ children, href, variant = 'primary', onClick, className = '' }: ButtonProps) {
  const base = 'inline-flex items-center justify-center px-6 py-3 rounded-lg font-medium text-sm transition-colors';
  const styles = variant === 'primary'
    ? 'bg-accent-gold text-bg-primary hover:bg-accent-gold-dim'
    : 'border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/10';

  if (href) {
    return <Link href={href} className={`${base} ${styles} ${className}`}>{children}</Link>;
  }

  return <button onClick={onClick} className={`${base} ${styles} ${className}`}>{children}</button>;
}
```

- [ ] **Step 4: Build app error boundary**

Create `web/app/error.tsx`:
```tsx
'use client';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary">
      <div className="text-center max-w-md px-4">
        <h2 className="text-xl font-semibold text-text-primary mb-4">Something went wrong</h2>
        <p className="text-text-secondary mb-6">
          The Quran data is safe — please refresh the page.
        </p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-accent-gold text-bg-primary rounded-lg font-medium hover:bg-accent-gold-dim transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Update root layout with fonts, metadata, Header, Footer**

Replace `web/app/layout.tsx`:
```tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: {
    default: 'Islamic Hive Mind — A Living Islamic Knowledge Base',
    template: '%s | Islamic Hive Mind',
  },
  description: 'Explore the Quran with full Arabic text, English translation, word-by-word analysis, and an AI-powered Islamic scholar.',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    siteName: 'Islamic Hive Mind',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-bg-primary text-text-primary min-h-screen">
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
```

- [ ] **Step 6: Build landing page**

Replace `web/app/page.tsx`:
```tsx
import { getRandomVerse, getSurah } from '@/lib/quran';
import QuranVerse from '@/components/quran/QuranVerse';
import Button from '@/components/ui/Button';

export default async function HomePage() {
  const verse = await getRandomVerse();
  const surah = verse ? await getSurah(verse.surah_id) : null;

  return (
    <main>
      {/* Hero */}
      <section className="py-20 md:py-32 text-center px-4">
        <div dir="rtl" className="text-3xl md:text-5xl text-white mb-4" style={{ fontFamily: "'Amiri', serif", lineHeight: '2.2em' }}>
          الخلية الإسلامية
        </div>
        <h1 className="text-3xl md:text-5xl font-bold text-text-primary mb-4">
          Islamic Hive Mind
        </h1>
        <p className="text-text-secondary text-lg mb-8 max-w-xl mx-auto">
          A living Islamic knowledge base — explore the Quran, discover its depth, ask a scholar.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Button href="/ask">Ask The Scholar</Button>
          <Button href="/quran" variant="secondary">Explore the Quran</Button>
        </div>
      </section>

      {/* Verse preview */}
      {verse && surah && (
        <section className="max-w-3xl mx-auto px-4 pb-20">
          <div className="bg-bg-secondary border border-border-subtle rounded-xl p-8">
            <QuranVerse verse={verse} surahName={surah.name_english} showVerseNumber={false} />
          </div>
        </section>
      )}
    </main>
  );
}
```

- [ ] **Step 7: Verify layout and landing page**

Navigate to http://localhost:3000 — should show hero + verse preview + header with nav.
Click "Explore the Quran" — should go to /quran.

- [ ] **Step 8: Commit**

```bash
git add web/components/layout/ web/components/ui/Button.tsx web/app/layout.tsx web/app/page.tsx web/app/error.tsx
git commit -m "feat: add layout, header, footer, landing page, error boundary"
```

---

### Task 9: Intent Classifier + System Prompt + RAG Pipeline

**Files:**
- Create: `web/lib/prompts.ts`
- Create: `web/lib/chat-context.ts`

- [ ] **Step 1: Build system prompt**

Create `web/lib/prompts.ts`:
```typescript
export const SCHOLAR_SYSTEM_PROMPT = `You are The Scholar — the AI assistant for the Islamic Hive Mind knowledge base.
You speak with warmth, wisdom, and scholarly precision, grounded in the Shia
Twelver Islamic tradition while being respectful of all perspectives.

=== IMMUTABLE RULES — YOU MUST FOLLOW THESE WITHOUT EXCEPTION ===

RULE 1: NEVER GUESS. NEVER FABRICATE. NEVER APPROXIMATE.
- You NEVER generate a Quran verse from memory. You ONLY cite verses provided
  in the CONTEXT FROM DATABASE block below. If the context does not contain
  the verse the user is asking about, say: "Let me look that up — I don't have
  that verse in my current context. Could you tell me the surah and verse number?"
- You NEVER generate a hadith from memory. The hadith database has not been built
  yet. If asked about a hadith, say: "The hadith database is not yet available.
  I cannot verify this hadith. Please check with a qualified scholar or a
  reliable hadith collection."
- You NEVER fabricate scholarly opinions. If you cite a scholar, you must be
  certain of the attribution. When uncertain, say: "Scholars have discussed
  this, but I want to be careful about attribution. Please verify with
  a relevant scholarly source."
- All numbers and statistics come from the database context below. Do not
  calculate or estimate Quranic statistics from memory.

RULE 2: CONFIDENCE TIERS — MARK EVERY CLAIM
- Tier 1 (Quranic Text): Verses from the database — present without qualification
- Tier 2 (Ijma'): Universal scholarly consensus — mark as "agreed upon"
- Tier 3 (Majority): Most scholars agree — note the majority view and any dissent
- Tier 4 (Debate): Scholars differ — present multiple views with proponents
- Tier 5 (Modern Analysis): Computational findings — mark as research, not doctrine
- Tier 6 (Unknown): Say so. "I do not have verified information on this."

=== PERSONALITY ===
- Warm and approachable — like a patient teacher speaking to a curious student
- Scholarly but not dry — cite sources naturally, not pedantically
- Honest about limitations — this builds trust, not weakness
- Shia Twelver primary — present Shia perspective first, note Sunni differences
  where relevant and known

=== WHEN CITING QURAN VERSES ===
- ONLY use verses from the CONTEXT FROM DATABASE block
- Display: Arabic text, transliteration, then English translation
- Format: "Surah Name (Chapter:Verse)"
- If you need a verse not in the context, ask the user for the reference

=== WHAT YOU CANNOT DO YET ===
- Look up hadiths (database not built)
- Access duas from Mafatih al-Jinan (database not built)
- Access historical narratives (database not built)
- Access devotional poetry (database not built)
Be transparent about these limitations when relevant.`;
```

- [ ] **Step 2: Build intent classifier and RAG pipeline**

Create `web/lib/chat-context.ts`:
```typescript
import type { IntentType, ChatMessage } from '@/types';
import {
  getVerse, getVerseWords, getSurah, getSurahVerses,
  searchByRoot, searchByEnglish, getWordFrequency, getPatterns
} from './quran';

const INTENT_PATTERNS: Record<string, RegExp[]> = {
  verse_lookup: [
    /surah\s+\d+.*verse\s+\d+/i,
    /\d+:\d+/,
    /ayah?\s+\d+/i,
    /verse\s+\d+\s+of/i,
  ],
  word_query: [
    /how many times.*(?:appear|mention|occur)/i,
    /word\s+["']?\w+["']?.*(?:quran|appear)/i,
    /frequency of/i,
    /meaning of.*(?:arabic|word)/i,
  ],
  pattern_query: [
    /number\s*19/i,
    /numerical.*(?:miracle|discovery|finding)/i,
    /abjad/i,
    /gematria/i,
  ],
  surah_info: [
    /(?:what|tell|about).*surah\s+/i,
    /surah\s+(?:al-?)?[a-z]+(?!\s*\d)/i,
  ],
  story_request: [
    /story of/i,
    /tell me about (?:prophet|imam)/i,
    /what happened (?:at|in|during)\s+(?:karbala|ghadir|saqifa|badr|uhud)/i,
  ],
  fiqh_ruling: [
    /is it (?:halal|haram|makruh|mustahab|wajib)/i,
    /ruling on/i,
    /fatwa/i,
    /can (?:i|we|muslims)\s+(?:eat|drink|pray|fast|marry|divorce)/i,
    /how (?:do i|should i|to)\s+(?:pray|fast|perform)/i,
  ],
  hadith_request: [
    /hadith.*(?:about|on|regarding)/i,
    /(?:prophet|imam).*(?:said|narrated|reported)/i,
    /al-?kafi/i,
    /sahih\s+(?:bukhari|muslim)/i,
    /is this hadith (?:authentic|sahih|real)/i,
  ],
};

// Direct responses that skip the AI entirely
const DIRECT_RESPONSES: Record<string, string> = {
  fiqh_ruling: "For fiqh rulings, please consult your marja' (religious authority). Each marja' may have a different ruling on this matter. I can share relevant Quran verses if you'd like — just let me know the topic.",
  hadith_request: "The hadith database has not been built yet. I cannot verify hadiths at this time. Please check with a qualified scholar or a reliable hadith collection such as Al-Kafi by Al-Kulayni, Man La Yahduruhu al-Faqih by Sheikh Saduq, or other authenticated sources.",
};

export function classifyIntent(message: string): IntentType {
  for (const [intent, patterns] of Object.entries(INTENT_PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(message)) return intent as IntentType;
    }
  }
  return 'general_islamic';
}

export function getDirectResponse(intent: IntentType): string | null {
  return DIRECT_RESPONSES[intent] || null;
}

function extractVerseRef(message: string): { surah: number; verse: number } | null {
  // Match patterns like "2:255" or "surah 2 verse 255"
  const colonMatch = message.match(/(\d+):(\d+)/);
  if (colonMatch) {
    return { surah: parseInt(colonMatch[1]), verse: parseInt(colonMatch[2]) };
  }
  const verboseMatch = message.match(/surah\s+(\d+).*verse\s+(\d+)/i);
  if (verboseMatch) {
    return { surah: parseInt(verboseMatch[1]), verse: parseInt(verboseMatch[2]) };
  }
  return null;
}

function extractSearchTerm(message: string): string {
  // Extract the key concept from the message
  const wordMatch = message.match(/word\s+["']?(\w+)["']?/i);
  if (wordMatch) return wordMatch[1];

  const aboutMatch = message.match(/(?:about|on|regarding)\s+(\w+)/i);
  if (aboutMatch) return aboutMatch[1];

  // Fallback: use the longest word that isn't a stop word
  const stopWords = new Set(['what', 'does', 'the', 'quran', 'say', 'about', 'how', 'many', 'times', 'appear', 'in', 'is', 'are', 'was', 'were', 'a', 'an', 'of', 'to', 'for']);
  const words = message.toLowerCase().split(/\s+/).filter(w => w.length > 2 && !stopWords.has(w));
  return words.sort((a, b) => b.length - a.length)[0] || message.split(' ')[0];
}

export async function buildContext(intent: IntentType, message: string): Promise<string> {
  let context = '';

  try {
    switch (intent) {
      case 'verse_lookup': {
        const ref = extractVerseRef(message);
        if (ref) {
          const verse = await getVerse(ref.surah, ref.verse);
          const surah = await getSurah(ref.surah);
          if (verse && surah) {
            context = `[Database Query: ayat table, surah ${ref.surah} verse ${ref.verse}]\n\n`;
            context += `Surah ${surah.name_english} (${surah.name_transliteration}), Verse ${ref.verse}:\n`;
            context += `Arabic: ${verse.text_arabic}\n`;
            context += `Transliteration: ${verse.text_transliteration || 'N/A'}\n`;
            context += `English: ${verse.text_english || 'N/A'}\n`;
          } else {
            context = `[Database Query: verse ${ref.surah}:${ref.verse} not found. Surah ${ref.surah} ${surah ? `has ${surah.verse_count} verses` : 'does not exist'}.]\n`;
          }
        }
        break;
      }

      case 'word_query': {
        const term = extractSearchTerm(message);
        const results = await searchByEnglish(term);
        const freq = results.length;
        context = `[Database Query: search for "${term}" in English translations]\n`;
        context += `Found ${freq} verses containing "${term}".\n\n`;
        for (const r of results.slice(0, 5)) {
          context += `${r.surah_name_english} (${r.surah_id}:${r.verse_number}):\n`;
          context += `  Arabic: ${r.text_arabic}\n`;
          context += `  Transliteration: ${r.text_transliteration || 'N/A'}\n`;
          context += `  English: ${r.text_english || 'N/A'}\n\n`;
        }
        break;
      }

      case 'pattern_query': {
        const patterns = await getPatterns();
        context = `[Database Query: patterns table]\n`;
        context += `${patterns.length} patterns in database:\n\n`;
        for (const p of patterns) {
          context += `- ${p.name}: ${p.verified ? 'CONFIRMED' : 'NOT CONFIRMED'}`;
          if (p.scholarly_consensus) context += ` (${p.scholarly_consensus})`;
          context += `\n  ${p.description}\n`;
        }
        break;
      }

      case 'surah_info': {
        // Try to extract surah name or number
        const numMatch = message.match(/surah\s+(\d+)/i);
        const nameMatch = message.match(/surah\s+(?:al-?)?(\w+)/i);
        let surahId: number | null = null;

        if (numMatch) {
          surahId = parseInt(numMatch[1]);
        }
        // For name matching, we'd need a lookup — simplified for V1

        if (surahId) {
          const surah = await getSurah(surahId);
          const verses = await getSurahVerses(surahId);
          if (surah) {
            context = `[Database Query: surahs + ayat tables for surah ${surahId}]\n\n`;
            context += `Surah ${surah.name_english} (${surah.name_transliteration} / ${surah.name_arabic})\n`;
            context += `Number: ${surah.id}, Verses: ${surah.verse_count}, Revelation: ${surah.revelation_type}\n`;
            context += `Words: ${surah.word_count}, Letters: ${surah.letter_count}\n`;
            context += `Bismillah: ${surah.bismillah ? 'Yes' : 'No (At-Tawbah)'}\n\n`;
            context += `First 3 verses:\n`;
            for (const v of verses.slice(0, 3)) {
              context += `  ${v.verse_number}. Arabic: ${v.text_arabic}\n`;
              context += `     Transliteration: ${v.text_transliteration || 'N/A'}\n`;
              context += `     English: ${v.text_english || 'N/A'}\n\n`;
            }
          }
        }
        break;
      }

      case 'story_request': {
        const term = extractSearchTerm(message);
        const results = await searchByEnglish(term);
        context = `[Database Query: search English text for "${term}"]\n`;
        context += `Found ${results.length} relevant verses:\n\n`;
        for (const r of results.slice(0, 5)) {
          context += `${r.surah_name_english} (${r.surah_id}:${r.verse_number}):\n`;
          context += `  Arabic: ${r.text_arabic}\n`;
          context += `  English: ${r.text_english || 'N/A'}\n\n`;
        }
        break;
      }

      case 'general_islamic':
      default:
        context = '[No specific database query for this question. Answer from your knowledge, marking confidence tiers appropriately. Remember: NEVER fabricate verses or hadiths.]\n';
        break;
    }
  } catch (error) {
    context = '[Database query failed. Answer carefully without citing specific verses or statistics.]\n';
  }

  return context;
}

export function shouldEscalateToSonnet(messages: ChatMessage[], currentMessage: string): boolean {
  if (messages.length > 10) return true; // 5+ turns (user+assistant pairs)
  if (/\b(theolog|comparative|shia.*sunni|sunni.*shia|debate|scholarly dispute)\b/i.test(currentMessage)) return true;
  if (/\b(pattern|numerical|mathematical|abjad|statistical)\b/i.test(currentMessage)) return true;
  if (/\b(detail|scholarly|in-?depth|thorough)\b/i.test(currentMessage)) return true;
  return false;
}
```

- [ ] **Step 3: Commit**

```bash
git add web/lib/prompts.ts web/lib/chat-context.ts
git commit -m "feat: add intent classifier, system prompt, and RAG pipeline"
```

---

### Task 10: Chat API Route (Streaming)

**Files:**
- Create: `web/app/api/chat/route.ts`

- [ ] **Step 1: Build streaming chat endpoint**

Create `web/app/api/chat/route.ts`:
```typescript
import Anthropic from '@anthropic-ai/sdk';
import { SCHOLAR_SYSTEM_PROMPT } from '@/lib/prompts';
import { classifyIntent, getDirectResponse, buildContext, shouldEscalateToSonnet } from '@/lib/chat-context';
import type { ChatMessage } from '@/types';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { messages, model: requestedModel } = body as {
      messages: ChatMessage[];
      model?: 'haiku' | 'sonnet';
    };

    if (!messages || messages.length === 0) {
      return new Response(JSON.stringify({ error: 'No messages provided.' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const lastMessage = messages[messages.length - 1];
    if (lastMessage.role !== 'user') {
      return new Response(JSON.stringify({ error: 'Last message must be from user.' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const userMessage = lastMessage.content;

    // Step 1: Classify intent
    const intent = classifyIntent(userMessage);

    // Step 2: Check for direct responses (fiqh, hadith)
    const directResponse = getDirectResponse(intent);
    if (directResponse) {
      // Stream the direct response as if it were from Claude
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'text', text: directResponse })}\n\n`));
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done' })}\n\n`));
          controller.close();
        },
      });
      return new Response(stream, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    // Step 3: Build context from database
    const dbContext = await buildContext(intent, userMessage);

    // Step 4: Select model
    let modelId = 'claude-haiku-4-5-20251001';
    if (requestedModel === 'sonnet' || shouldEscalateToSonnet(messages, userMessage)) {
      modelId = 'claude-sonnet-4-6';
    }

    // Step 5: Build conversation for Claude
    const systemPrompt = SCHOLAR_SYSTEM_PROMPT + '\n\n=== CONTEXT FROM DATABASE ===\n' + dbContext;

    const claudeMessages = messages.map((m) => ({
      role: m.role as 'user' | 'assistant',
      content: m.content,
    }));

    // Step 6: Stream response
    const stream = anthropic.messages.stream({
      model: modelId,
      max_tokens: 2048,
      system: systemPrompt,
      messages: claudeMessages,
    });

    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const event of stream) {
            if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
              const data = JSON.stringify({ type: 'text', text: event.delta.text });
              controller.enqueue(encoder.encode(`data: ${data}\n\n`));
            }
          }
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done', model: modelId })}\n\n`));
          controller.close();
        } catch (error: any) {
          const errData = JSON.stringify({ type: 'error', message: error.message || 'An error occurred' });
          controller.enqueue(encoder.encode(`data: ${errData}\n\n`));
          controller.close();
        }
      },
    });

    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error: any) {
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add web/app/api/chat/
git commit -m "feat: add streaming chat API route with RAG pipeline"
```

---

### Task 11: Chat UI Components

**Files:**
- Create: `web/components/ui/LoadingDots.tsx`
- Create: `web/components/chat/ChatErrorBoundary.tsx`
- Create: `web/components/chat/ChatMessage.tsx`
- Create: `web/components/chat/ChatInput.tsx`
- Create: `web/components/chat/SuggestedQuestions.tsx`
- Create: `web/components/chat/ChatPanel.tsx`
- Create: `web/components/chat/FloatingChatButton.tsx`
- Create: `web/hooks/useChat.ts`

- [ ] **Step 1: Build LoadingDots**

Create `web/components/ui/LoadingDots.tsx`:
```tsx
export default function LoadingDots() {
  return (
    <div className="flex gap-1 py-2">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-2 h-2 rounded-full bg-accent-gold animate-pulse"
          style={{ animationDelay: `${i * 200}ms` }}
        />
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Build ChatErrorBoundary**

Create `web/components/chat/ChatErrorBoundary.tsx`:
```tsx
'use client';
import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; }

export default class ChatErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    console.error('Chat error:', error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 text-center">
          <p className="text-text-secondary">
            I encountered an error processing your request. Please try again.
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 text-accent-gold text-sm hover:underline"
          >
            Dismiss
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

- [ ] **Step 3: Build useChat hook**

Create `web/hooks/useChat.ts`:
```typescript
'use client';
import { useState, useCallback, useRef, useEffect } from 'react';
import type { ChatMessage } from '@/types';

const STORAGE_KEY = 'islamic-hive-mind-chat';

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function loadMessages(): ChatMessage[] {
  if (typeof window === 'undefined') return [];
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveMessages(messages: ChatMessage[]) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  } catch { /* localStorage full or unavailable */ }
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [model, setModel] = useState<'haiku' | 'sonnet'>('haiku');
  const abortRef = useRef<AbortController | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    setMessages(loadMessages());
  }, []);

  // Save to localStorage on change
  useEffect(() => {
    if (messages.length > 0) saveMessages(messages);
  }, [messages]);

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };

    const assistantMessage: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      model,
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);

    try {
      abortRef.current = new AbortController();

      const allMessages = [...messages, userMessage];

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: allMessages, model }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`Chat API error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'text') {
              accumulated += data.text;
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  last.content = accumulated;
                }
                return updated;
              });
            } else if (data.type === 'error') {
              accumulated += `\n\n*Error: ${data.message}*`;
              setMessages(prev => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  last.content = accumulated;
                }
                return updated;
              });
            }
          } catch { /* ignore malformed SSE lines */ }
        }
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === 'assistant') {
            last.content = 'I encountered an error. Please try again.';
          }
          return updated;
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, [messages, model]);

  const clearChat = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const toggleModel = useCallback(() => {
    setModel(prev => prev === 'haiku' ? 'sonnet' : 'haiku');
  }, []);

  return { messages, isLoading, model, sendMessage, clearChat, toggleModel };
}
```

- [ ] **Step 4: Build ChatMessage**

Create `web/components/chat/ChatMessage.tsx`:
```tsx
import type { ChatMessage as ChatMessageType } from '@/types';

interface Props {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] rounded-xl px-4 py-3 ${
        isUser
          ? 'bg-accent-gold/20 border border-accent-gold/30 text-text-primary'
          : 'bg-bg-secondary border border-border-subtle text-text-primary'
      }`}>
        <div className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content || '...'}
        </div>
        {!isUser && message.model && (
          <div className="mt-2 text-xs text-text-secondary">
            {message.model === 'sonnet' ? 'Sonnet' : 'Haiku'}
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Build ChatInput**

Create `web/components/chat/ChatInput.tsx`:
```tsx
'use client';
import { useState, useRef, type KeyboardEvent } from 'react';

interface Props {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSend, isLoading }: Props) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex gap-2 p-4 border-t border-border-subtle">
      <textarea
        ref={inputRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about the Quran..."
        rows={1}
        className="flex-1 bg-bg-primary border border-border-subtle rounded-lg px-4 py-3 text-text-primary text-sm resize-none focus:outline-none focus:border-accent-gold/50 placeholder:text-text-secondary"
        disabled={isLoading}
      />
      <button
        onClick={handleSend}
        disabled={isLoading || !input.trim()}
        className="px-4 py-3 bg-accent-gold text-bg-primary rounded-lg font-medium text-sm hover:bg-accent-gold-dim transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </div>
  );
}
```

- [ ] **Step 6: Build SuggestedQuestions**

Create `web/components/chat/SuggestedQuestions.tsx`:
```tsx
interface Props {
  onSelect: (question: string) => void;
}

const QUESTIONS = [
  "What does the Quran say about patience?",
  "Tell me about Surah Al-Fatiha verse by verse",
  "How many times does the word 'mercy' appear in the Quran?",
  "What is Surah Al-Ikhlas about?",
  "What is the significance of the number 19 in the Quran?",
  "Show me verses about justice",
];

export default function SuggestedQuestions({ onSelect }: Props) {
  return (
    <div className="p-4">
      <p className="text-text-secondary text-xs mb-3">Try asking:</p>
      <div className="flex flex-wrap gap-2">
        {QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="text-xs px-3 py-2 rounded-full border border-accent-gold/30 text-accent-gold hover:bg-accent-gold/10 transition-colors text-left"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 7: Build ChatPanel**

Create `web/components/chat/ChatPanel.tsx`:
```tsx
'use client';
import { useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import SuggestedQuestions from './SuggestedQuestions';
import ChatErrorBoundary from './ChatErrorBoundary';
import LoadingDots from '@/components/ui/LoadingDots';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  fullPage?: boolean;
}

export default function ChatPanel({ isOpen, onClose, fullPage = false }: Props) {
  const { messages, isLoading, model, sendMessage, clearChat, toggleModel } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen && !fullPage) return null;

  const panelClasses = fullPage
    ? 'w-full max-w-3xl mx-auto'
    : 'fixed right-0 top-0 h-full w-full sm:w-[480px] z-50';

  return (
    <ChatErrorBoundary>
      {/* Overlay for slide-out panel */}
      {!fullPage && (
        <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />
      )}

      <div className={`${panelClasses} bg-bg-chat flex flex-col ${fullPage ? 'min-h-[600px]' : 'h-full'}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border-subtle">
          <div>
            <h2 className="text-text-primary font-semibold">The Scholar</h2>
            <p className="text-text-secondary text-xs">Ask me about the Quran and Islam</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleModel}
              className="text-xs px-2 py-1 rounded border border-border-subtle text-text-secondary hover:text-accent-gold hover:border-accent-gold/30 transition-colors"
              title={`Using ${model}. Click to switch.`}
            >
              {model === 'sonnet' ? 'Sonnet' : 'Haiku'}
            </button>
            <button
              onClick={clearChat}
              className="text-xs text-text-secondary hover:text-error transition-colors"
              title="Clear chat history"
            >
              Clear
            </button>
            {!fullPage && (
              <button onClick={onClose} className="text-text-secondary hover:text-text-primary text-lg ml-2">
                &times;
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 && (
            <SuggestedQuestions onSelect={sendMessage} />
          )}
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-bg-secondary border border-border-subtle rounded-xl px-4 py-3">
                <LoadingDots />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </ChatErrorBoundary>
  );
}
```

- [ ] **Step 8: Build FloatingChatButton**

Create `web/components/chat/FloatingChatButton.tsx`:
```tsx
'use client';
import { useState } from 'react';
import ChatPanel from './ChatPanel';

export default function FloatingChatButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <ChatPanel isOpen={isOpen} onClose={() => setIsOpen(false)} />

      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-30 w-14 h-14 bg-accent-gold rounded-full shadow-lg shadow-accent-gold/20 flex items-center justify-center hover:bg-accent-gold-dim transition-colors animate-pulse hover:animate-none"
          title="Ask The Scholar"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#0a0e1a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}
    </>
  );
}
```

- [ ] **Step 9: Add FloatingChatButton to layout**

Update `web/app/layout.tsx` — add import and component after `<Footer />`:
```tsx
import FloatingChatButton from '@/components/chat/FloatingChatButton';

// ... inside the body, after <Footer />:
        <Footer />
        <FloatingChatButton />
```

- [ ] **Step 10: Build /ask full-page chat**

Create `web/app/ask/page.tsx`:
```tsx
import type { Metadata } from 'next';
import ChatPanel from '@/components/chat/ChatPanel';

export const metadata: Metadata = {
  title: 'Ask The Scholar',
  description: 'Ask questions about the Quran and Islam. Powered by AI, grounded in the Quran database.',
};

export default function AskPage() {
  return (
    <main className="max-w-content mx-auto px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-semibold text-text-primary mb-2">Ask The Scholar</h1>
        <p className="text-text-secondary">
          Ask questions about the Quran and Islam. Answers are grounded in our verified Quran database.
        </p>
      </div>
      <ChatPanel isOpen={true} onClose={() => {}} fullPage={true} />
    </main>
  );
}
```

- [ ] **Step 11: Commit**

```bash
git add web/components/chat/ web/components/ui/LoadingDots.tsx web/hooks/ web/app/ask/ web/app/layout.tsx
git commit -m "feat: add chat UI (panel, floating button, messages, input, /ask page)"
```

---

### Task 12: Add ANTHROPIC_API_KEY and Test End-to-End

- [ ] **Step 1: Add your real API key to .env.local**

Edit `web/.env.local`:
```env
ANTHROPIC_API_KEY=sk-ant-YOUR_REAL_KEY_HERE
```

- [ ] **Step 2: Start the dev server and test**

```bash
cd /c/Users/hassa/islamic-hive-mind/web && npm run dev
```

Test checklist:
1. http://localhost:3000 — landing page with verse
2. http://localhost:3000/quran — 114 surah cards
3. http://localhost:3000/quran/1 — Al-Fatiha with Arabic
4. http://localhost:3000/quran/9 — At-Tawbah no Bismillah
5. Click floating chat button → send "What is Surah Al-Ikhlas about?"
6. Send "Is it halal to eat pork?" → should get "consult your marja'" response
7. Send "Tell me a hadith" → should get "hadith database not built yet"

- [ ] **Step 3: Commit .env.local to gitignore (already there) and final commit**

```bash
git add -A
git commit -m "feat: complete Foundation + AI Chatbot (all 13 tasks)"
git push origin master
```

---

### Task 13: Verification (Run the 36-Test Plan)

Run through the verification plan from the spec: Phases A through H, 36 tests. Document pass/fail for each. Fix any failures before declaring done.

This is manual testing — open the browser, follow the spec's verification plan, record results.
