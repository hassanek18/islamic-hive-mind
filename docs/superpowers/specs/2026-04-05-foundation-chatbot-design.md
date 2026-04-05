# Islamic Hive Mind — Sub-Project 1: Foundation + AI Chatbot

## Immutable Project Law: The Zero-Guess Principle

This law governs every component of the system. It cannot be overridden.

### Rule 1: Never Guess. Never Fabricate. Never Approximate.

- The chatbot NEVER generates a Quran verse from memory. Every verse is retrieved from the database. If the query returns no results, it says so honestly.
- The chatbot NEVER generates a hadith from memory. Until the hadith database is built, it says: "The hadith database has not been built yet. I cannot verify this hadith. Please check with a qualified scholar."
- The chatbot NEVER fabricates a scholarly opinion. If it cannot cite a specific named scholar and a specific named work, it does not make the claim.
- Numbers come from the database. The chatbot does not perform mental arithmetic on Quranic statistics — it runs a query and reports the result.
- When the system lacks verified data, it says: "I do not have verified information on this topic. Please consult a qualified scholar or marja'."

### Rule 2: Confidence Tiers

Every statement the system makes carries a tier:

- **Tier 1 — Quranic Text:** Arabic text from the Uthmani Mushaf, served from the database. No label needed.
- **Tier 2 — Ijma' (Consensus):** All scholars agree. Label: "Agreed upon by Shia scholars (ijma')."
- **Tier 3 — Majority Position:** Vast majority agrees, 1-2 dissent. Label: "Majority scholarly position. [Scholar X] holds [alternative view]."
- **Tier 4 — Scholarly Debate:** Significant disagreement. Multiple positions presented with proponents. Label: "Scholars differ on this matter."
- **Tier 5 — Modern Analysis:** Computational findings from this project. Label: "This is a computational observation from our analysis. It has not been endorsed by traditional Islamic scholarship."
- **Tier 6 — Unknown:** Insufficient verified data. Label: "I do not have verified information on this. Please consult a qualified scholar."

Tier 6 is not a failure. It is intellectual honesty.

## Context

The Islamic Hive Mind data layer (Phase 1) is complete: **114 surahs, 6,236 ayat, 77,429 words, 325,665 letters** in a SQLite database with full Arabic (Uthmani), English (Sahih International), transliteration, word-by-word morphology (1,651 unique roots), and Abjad values (total: 23,381,357). (Verified 2026-04-05, see METHODOLOGY.md for counting conventions.)

No web code exists yet. This sub-project builds the Next.js app shell, database API layer, design system, and AI chatbot. Stories and Discoveries sections will be built as separate sub-projects afterward.

## Architecture

### Directory Structure

```
islamic-hive-mind/
├── web/                              ← Next.js 14 app (App Router, TypeScript)
│   ├── app/
│   │   ├── layout.tsx                ← Root layout: fonts, theme, metadata, chat provider
│   │   ├── page.tsx                  ← Landing page
│   │   ├── ask/
│   │   │   └── page.tsx              ← Full-page chatbot experience
│   │   ├── api/
│   │   │   ├── chat/
│   │   │   │   └── route.ts          ← POST: Claude chat with RAG (streaming SSE)
│   │   │   └── quran/
│   │   │       ├── surah/
│   │   │       │   └── [id]/route.ts ← GET: /api/quran/surah/1
│   │   │       ├── verse/
│   │   │       │   └── [surah]/
│   │   │       │       └── [verse]/route.ts ← GET: /api/quran/verse/2/255
│   │   │       └── search/route.ts   ← GET: /api/quran/search?q=mercy&type=english
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx         ← Slide-out chat panel (used on every page)
│   │   │   ├── ChatMessage.tsx       ← Single message bubble with confidence tier badge
│   │   │   ├── ChatInput.tsx         ← Input field with send button
│   │   │   ├── FloatingChatButton.tsx ← Gold geometric button, bottom-right
│   │   │   └── SuggestedQuestions.tsx ← Starter question chips
│   │   ├── quran/
│   │   │   └── QuranVerse.tsx        ← Reusable: Arabic (Amiri) + transliteration + English
│   │   ├── layout/
│   │   │   ├── Header.tsx            ← Site header with nav
│   │   │   └── Footer.tsx            ← Site footer
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── ConfidenceTier.tsx    ← Displays tier badge (Tier 1-6)
│   │       └── LoadingDots.tsx       ← Typing indicator for chat
│   ├── lib/
│   │   ├── db.ts                     ← Unified async database abstraction
│   │   ├── quran.ts                  �� Quran query functions (all async)
│   │   ├── chat-context.ts           ← RAG pipeline: analyze intent → query DB → build context
│   │   └── prompts.ts               ← System prompt for The Scholar chatbot
│   ├── hooks/
│   │   └── useChat.ts               ← Custom hook for chat state + streaming
│   ├── types/
│   │   └── index.ts                  ← TypeScript types for Surah, Ayah, Word, etc.
│   ├── public/
│   │   ├── fonts/                    ← Amiri font files (self-hosted for performance)
│   │   └── patterns/                 ← Islamic geometric SVG patterns
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.local                    ← ANTHROPIC_API_KEY, TURSO_DATABASE_URL, etc.
├── db/hive-mind.db                   ← Existing SQLite database (unchanged)
├���─ scripts/                          ← Existing Python pipeline (unchanged)
└── ...
```

### Why `web/` Subdirectory

The Next.js app lives in `web/` to cleanly separate it from the Python data pipeline. Benefits:
- Independent `package.json` for web dependencies
- Root `package.json` stays minimal (Python tooling)
- Next.js build doesn't interfere with Python scripts
- Clear mental model: `scripts/` = data pipeline, `web/` = user-facing app

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 14+ |
| Language | TypeScript | 5+ |
| Styling | Tailwind CSS | 3+ |
| Animation | Framer Motion | 11+ |
| Database (dev) | better-sqlite3 | 11+ |
| Database (prod) | Turso (LibSQL) | @libsql/client |
| AI | Anthropic Claude API | @anthropic-ai/sdk |
| Streaming | Vercel AI SDK | ai |
| Fonts | Amiri (Arabic), Inter (English) | Self-hosted |

## Design System

### Color Palette

```
--bg-primary:      #0a0e1a    (deep navy — main background)
--bg-secondary:    #111827    (slightly lighter — cards, panels)
--bg-chat:         #1a1f35    (chat panel background)
--accent-gold:     #d4a843    (gold — CTAs, highlights, borders)
--accent-gold-dim: #b8942f    (muted gold — hover states)
--text-primary:    #f5f0e8    (warm cream — body text)
--text-secondary:  #9ca3af    (muted gray — secondary text)
--text-arabic:     #ffffff    (white — Arabic Quranic text for clarity)
--border:          #1e293b    (subtle borders)
--success:         #10b981    (confirmed patterns)
--warning:         #f59e0b    (needs investigation)
--error:           #ef4444    (failed claims)
```

### Typography

- **Arabic Quranic text:** Amiri, 24-32px, `dir="rtl"`, white on dark
- **English body:** Inter, 16px, cream on dark
- **Transliteration:** Inter italic, 14px, muted gray
- **Code/numbers:** JetBrains Mono, 14px
- **Headings:** Inter, semibold, with subtle gold underline accents

### Spacing & Layout

- Max content width: 1200px
- Responsive breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- Card padding: 24px
- Section padding: 80px vertical (desktop), 48px (mobile)

### Components

- Cards: `bg-secondary` with subtle border, rounded-xl, hover glow effect
- Buttons: Gold accent for primary, ghost/outline for secondary
- Arabic text blocks: Special styling with Amiri font, large size, centered, RTL
- Loading states: Pulsing gold dots for chat, skeleton cards for content
- Confidence tier badges: Color-coded labels (Tier 1-6) displayed on chat messages and content

## Database Layer

### Unified Async Abstraction (`lib/db.ts`)

better-sqlite3 and @libsql/client have fundamentally different APIs. The abstraction wraps both behind a single async interface:

```typescript
interface QueryResult<T> {
  rows: T[];
}

interface Database {
  query<T>(sql: string, params?: any[]): Promise<QueryResult<T>>;
  queryOne<T>(sql: string, params?: any[]): Promise<T | null>;
  execute(sql: string, params?: any[]): Promise<void>;
}

// Dev: Wraps better-sqlite3's synchronous API in async interface
function createLocalDb(dbPath: string): Database {
  const db = new BetterSqlite3(dbPath);
  return {
    async query<T>(sql: string, params?: any[]) {
      return { rows: db.prepare(sql).all(...(params || [])) as T[] };
    },
    async queryOne<T>(sql: string, params?: any[]) {
      return (db.prepare(sql).get(...(params || [])) as T) || null;
    },
    async execute(sql: string, params?: any[]) {
      db.prepare(sql).run(...(params || []));
    },
  };
}

// Prod: Wraps @libsql/client's native async API
function createTursoDb(url: string, authToken: string): Database {
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

export function getDb(): Database {
  if (process.env.TURSO_DATABASE_URL) {
    return createTursoDb(
      process.env.TURSO_DATABASE_URL,
      process.env.TURSO_AUTH_TOKEN!
    );
  }
  return createLocalDb(
    path.join(process.cwd(), '../db/hive-mind.db')
  );
}
```

### Query Functions (`lib/quran.ts`)

All functions are async and use the unified Database interface:

```typescript
async getSurah(id: number): Promise<Surah>
async getSurahVerses(id: number): Promise<Ayah[]>
async getVerse(surah: number, verse: number): Promise<Ayah>
async getVerseWords(surah: number, verse: number): Promise<Word[]>
async searchByRoot(root: string): Promise<SearchResult[]>
async searchByEnglish(query: string): Promise<SearchResult[]>
async getWordFrequency(root: string): Promise<FrequencyResult>
async getSurahStats(): Promise<SurahStats[]>
async getPatterns(): Promise<Pattern[]>
async getRandomVerse(): Promise<Ayah>  // For landing page verse display
```

### API Routes (Next.js App Router Dynamic Segments)

| Route | Method | Purpose | Response |
|-------|--------|---------|----------|
| `/api/quran/surah/[id]` | GET | Surah metadata + verses | `{ surah: Surah, verses: Ayah[] }` |
| `/api/quran/verse/[surah]/[verse]` | GET | Single verse + words | `{ verse: Ayah, words: Word[] }` |
| `/api/quran/search?q=mercy&type=english` | GET | Search corpus | `{ results: SearchResult[], count: number }` |
| `/api/chat` | POST | Chatbot (streaming) | SSE stream |

Dynamic segment routes use `params` from Next.js route handlers:
```typescript
// app/api/quran/surah/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const surah = await getSurah(parseInt(params.id));
  // ...
}
```

Search remains query-parameter based because search queries are naturally key-value pairs.

## AI Chatbot — "The Scholar"

### System Prompt

```
You are The Scholar — the AI assistant for the Islamic Hive Mind knowledge base.
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
  [relevant source]."
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
Be transparent about these limitations when relevant.

=== CONTEXT FROM DATABASE ===
{database_context}

=== CONVERSATION HISTORY ===
{history}
```

### RAG Pipeline (`lib/chat-context.ts`)

**Step 1: Intent Classification**

Analyze the user's message to determine query type:
- `verse_lookup` — asking about a specific verse → fetch from ayat table
- `word_query` — asking about a word/concept → search words table by root or English
- `pattern_query` — asking about numerical patterns → fetch from patterns table
- `surah_info` — asking about a surah → fetch surah metadata
- `story_request` — asking for a narrative → fetch relevant verses from the database
- `general_islamic` — general question → provide minimal DB context, chatbot uses its knowledge with appropriate tier markings
- `out_of_scope` — asking about hadiths, duas, or data not yet in the system → trigger Tier 6 response

**Step 2: Database Query**

Based on intent, run targeted queries. All queries go through `lib/quran.ts`:
- For `verse_lookup`: `getVerse(surah, verse)` + `getVerseWords(surah, verse)` → full Arabic + English + transliteration + word breakdown
- For `word_query`: `searchByRoot(root)` or `searchByEnglish(query)` → frequency + 5 sample verses with full text
- For `pattern_query`: `getPatterns()` → relevant verified patterns with methodology notes
- For `surah_info`: `getSurah(id)` + first 3 verses + last verse
- For `story_request`: search English text for relevant keywords → return matching verses
- For `out_of_scope`: no DB query, construct a Tier 6 context message

**Step 3: Context Construction**

Build a context block (max ~2,000 tokens) with the retrieved data formatted as structured text. Every verse includes: Arabic (Uthmani), transliteration, and English translation. Context is prefixed with a note indicating which database tables were queried.

**Step 4: Model Selection**

- Default: Claude Haiku (`claude-haiku-4-5-20251001`)
- Auto-escalate to Sonnet (`claude-sonnet-4-6`) when:
  - Conversation exceeds 5 turns
  - User asks about theological disputes or comparative religion
  - Query involves pattern analysis or mathematical content
  - User explicitly requests "detailed" or "scholarly" response
- Manual toggle available in chat UI (small icon button)

**Step 5: Stream to Client**

Use the Anthropic SDK with streaming enabled. Pipe the stream to the client via the Vercel AI SDK's streaming utilities.

### Chat UI

**Floating Button:**
- Bottom-right corner, fixed position
- Gold Islamic geometric icon (octagonal star or arabesque)
- Subtle pulse animation when idle
- Click → slide-out panel from right (480px wide on desktop, full-screen on mobile)

**Chat Panel:**
- Dark background (`--bg-chat`)
- Header: "The Scholar" with subtitle "Ask me about the Quran and Islam"
- Model indicator: small badge showing "Haiku" or "Sonnet"
- Message area: scrollable, auto-scroll to bottom on new messages
- User messages: right-aligned, gold accent bubble
- Assistant messages: left-aligned, dark card with cream text
- Quran verses within messages: rendered with `<QuranVerse>` component (Arabic large, English below)
- Confidence tier badges: small colored labels on relevant claims within messages
- Typing indicator: three pulsing gold dots
- Input: dark input field with gold send button, placeholder "Ask about the Quran..."

**Suggested Questions (shown when chat is empty):**
- "What does the Quran say about patience?"
- "Tell me about Surah Al-Fatiha verse by verse"
- "How many times does the word 'mercy' appear in the Quran?"
- "What is Surah Al-Ikhlas about?"
- "What is the significance of the number 19 in the Quran?"
- "Show me verses about justice"

**Full-Page Experience (`/ask`):**
- Same chat interface but centered, wider (800px), with more vertical space
- Sidebar with conversation history (localStorage)
- Markdown rendering in assistant messages (headers, lists, bold, code blocks)
- Quran verses rendered with the QuranVerse component even within markdown

### Chat State Management

```typescript
// hooks/useChat.ts
interface ChatState {
  messages: ChatMessage[];            // persisted to localStorage
  isLoading: boolean;
  model: 'haiku' | 'sonnet';
  sendMessage(content: string): void; // POST to /api/chat, handle SSE stream
  clearChat(): void;
  toggleModel(): void;
}
```

## Landing Page

### Layout

```
┌─────────────────────────────────────────────┐
│  Header: Logo + Nav (Stories, Discoveries,   │
│          Ask The Scholar)                     │
├─────────────────────────────────────────────┤
│                                              │
│  HERO SECTION                                │
│  Islamic geometric SVG background            │
│  "الخلية الإسلامية" (Arabic calligraphy)    │
│  "Islamic Hive Mind"                         │
│  "A living Islamic knowledge base"           │
│                                              │
│  [Ask The Scholar]  [Explore the Quran]      │
│                                              │
├─────────────────────────────────────────────┤
│                                              │
│  FEATURES SECTION (3 cards)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Stories  │ │Discoveries│ │   Ask    │    │
│  │(Coming   │ │(Coming    │ │  The     │    │
│  │ Soon)    │ │ Soon)     │ │ Scholar  │    │
│  └──────────┘ └──────────┘ └──────────┘    │
│                                              │
├─────────────────────────────────────────────┤
│                                              │
│  QURAN PREVIEW                               │
│  Verse from database displayed in             │
│  Arabic (Amiri) + English + transliteration  │
│  [Show another verse] button                 │
│                                              │
├─────────────────────────────────────────────┤
│  Footer                                      │
└─────────────────────────────────────────────┘
                                    [Chat 💬]  ← Floating button
```

## Environment Variables

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Production only (Turso)
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=...

# Optional
NEXT_PUBLIC_SITE_URL=https://islamichivemind.com
```

## Verification Plan

1. **Database API:** Hit `/api/quran/surah/1` in the browser, verify JSON matches DB content for Al-Fatiha (7 verses, correct Arabic)
2. **Verse endpoint:** Hit `/api/quran/verse/2/255` (Ayat al-Kursi), verify full Arabic + English + transliteration + word data
3. **Search endpoint:** Hit `/api/quran/search?q=mercy&type=english`, verify results contain relevant verses
4. **QuranVerse component:** Render Al-Fatiha 1:1 — verify Arabic displays in Amiri font, RTL, with English and transliteration below
5. **Chatbot Zero-Guess test:** Ask "What is the hadith about..." → verify chatbot responds with Tier 6 (hadith database not available) instead of fabricating
6. **Chatbot RAG test:** Ask "How many times does mercy appear?" → verify DB query runs and EXACT count from database is included in response
7. **Chatbot verse test:** Ask "Show me Surah Al-Ikhlas" → verify all 4 verses are fetched from database, not generated from memory
8. **Model switching:** Toggle to Sonnet, ask a question, verify response comes from the correct model
9. **Mobile responsive:** Test chat panel on 375px viewport — full-screen mode, readable Arabic
10. **Dark theme:** Verify all text is readable, no white backgrounds flash
11. **localStorage:** Send messages, refresh page, verify history persists
12. **Confidence tiers:** Ask a theological question → verify response includes appropriate tier label
