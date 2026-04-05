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
│   │   ├── quran/
│   │   │   ├── page.tsx              ← Surah list (114 cards, server-rendered)
│   │   │   └── [id]/page.tsx         ← Individual surah page (all verses, server-rendered)
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
│   │   │   ├── QuranVerse.tsx        ← Reusable: Arabic (Amiri) + transliteration + English
│   │   │   └── SurahCard.tsx         ← Surah card for list page
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
│   │   ├── quran.ts                  ← Quran query functions (all async)
│   │   ├── chat-context.ts           ← RAG: intent classify → query DB → build context
│   │   └── prompts.ts               ← System prompt for The Scholar chatbot
│   ├── hooks/
│   │   └── useChat.ts               ← Custom hook for chat state + streaming
│   ├── types/
│   │   └── index.ts                  ← TypeScript types for Surah, Ayah, Word, etc.
│   ├── public/
│   │   ├── fonts/                    ← Amiri font files + OFL license (self-hosted)
│   │   └── patterns/                 ← Islamic geometric SVG patterns
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.local                    ← ANTHROPIC_API_KEY, TURSO_DATABASE_URL, etc.
├── db/hive-mind.db                   ← Existing SQLite database (unchanged)
├── scripts/                          ← Existing Python pipeline (unchanged)
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

- **Arabic Quranic text:** Amiri, 24-32px, `dir="rtl"`, white on dark, `line-height: 2.2em` minimum (accommodates tashkeel/diacritical marks above and below letters)
- **English body:** Inter, 16px, cream on dark
- **Transliteration:** Inter italic, 14px, muted gray
- **Code/numbers:** JetBrains Mono, 14px
- **Headings:** Inter, semibold, with subtle gold underline accents

**Arabic text isolation:** Arabic blocks are always rendered in their own `<div dir="rtl">`, never inline with English text. This prevents bidirectional text rendering issues.

### Font Licensing

- **Amiri:** Licensed under the SIL Open Font License (OFL). The OFL license file MUST be included in `public/fonts/OFL.txt`.
- **Inter:** Licensed under the SIL Open Font License.

### Spacing & Layout

- Max content width: 1200px
- Responsive breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- Card padding: 24px
- Section padding: 80px vertical (desktop), 48px (mobile)

### Components

- Cards: `bg-secondary` with subtle border, rounded-xl, hover glow effect
- Buttons: Gold accent for primary, ghost/outline for secondary
- Arabic text blocks: Isolated div with Amiri font, large size, centered, RTL, 2.2em line-height
- Loading states: Pulsing gold dots for chat, skeleton cards for content
- Confidence tier badges: Color-coded labels (Tier 1-6) displayed on chat messages and content

### Nav "Coming Soon" Behavior

Stories and Discoveries nav links:
- Visually present but muted (`text-secondary` color, not `text-primary`)
- Show tooltip on hover: "Coming soon — we're crafting this section with care"
- Do NOT navigate anywhere — they are disabled links (`<span>`, not `<a>`)
- Use `cursor-default`, not `cursor-pointer`

### Error Boundaries

Two React Error Boundaries in the component tree:

1. **App-level Error Boundary** — wraps the entire app in `layout.tsx`:
   - Catches unhandled errors from any page or component
   - Displays: "Something went wrong. The Quran data is safe — please refresh the page."
   - Logs error to console (and optionally to an error tracking service in production)

2. **Chat Error Boundary** — wraps only the chat components:
   - Catches chat-specific errors (API failures, streaming errors, JSON parse errors) without crashing the rest of the page
   - Displays within the chat panel: "I encountered an error processing your request. Please try again."
   - Preserves existing chat history in localStorage

## Quran Reader Pages (Server-Rendered Proof of Concept)

These are read-only, server-rendered pages. No client-side complexity. They prove:
- Database connection works
- Arabic rendering works (RTL, Amiri font, diacritics)
- QuranVerse component works
- The API layer works

### Surah List Page (`/quran`)

Displays all 114 surahs as cards. Each card shows:
- Arabic name (Amiri font, RTL)
- English name
- Transliteration
- Verse count
- Revelation type badge (Meccan = teal, Medinan = amber)
- Juz range

Data fetched server-side via `getSurahStats()`. No client JavaScript needed.

### Individual Surah Page (`/quran/[id]`)

Shows:
- Surah header: Arabic name, English name, transliteration, revelation type, verse count
- Bismillah (if `surah.bismillah` is true) rendered with QuranVerse component
- Every verse rendered with QuranVerse component: Arabic (large Amiri, RTL), transliteration, English translation
- Verse numbers displayed as gold badges

Data fetched server-side via `getSurah(id)` + `getSurahVerses(id)`. No client JavaScript needed.

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
async getSurahStats(): Promise<SurahStats[]>        // All 114 surahs for list page
async getVerse(surah: number, verse: number): Promise<Ayah>
async getVerseWords(surah: number, verse: number): Promise<Word[]>
async searchByRoot(root: string): Promise<SearchResult[]>
async searchByEnglish(query: string): Promise<SearchResult[]>
async getWordFrequency(root: string): Promise<FrequencyResult>
async getPatterns(): Promise<Pattern[]>
async getRandomVerse(): Promise<Ayah>                // For landing page verse display
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

## SEO & Meta Tags

```typescript
// app/layout.tsx — Root metadata
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

// app/quran/[id]/page.tsx — Per-surah metadata
export async function generateMetadata({ params }): Promise<Metadata> {
  const surah = await getSurah(parseInt(params.id));
  return {
    title: `Surah ${surah.name_english} (${surah.name_transliteration})`,
    description: `Read Surah ${surah.name_english} — ${surah.verse_count} verses, ${surah.revelation_type}. Full Arabic text with English translation and transliteration.`,
  };
}
```

All Quran pages use `generateStaticParams()` to pre-render at build time (114 surah pages).

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

**Step 1: Intent Classification (V1 — Keyword/Regex)**

V1 uses explicit keyword and regex matching. No embeddings, no ML. Simple, debuggable, reliable.

```typescript
const INTENT_PATTERNS: Record<IntentType, RegExp[]> = {
  verse_lookup: [
    /surah\s+\d+.*verse\s+\d+/i,
    /\d+:\d+/,                              // Pattern like "2:255"
    /ayah?\s+\d+/i,
    /verse\s+\d+\s+of/i,
  ],
  word_query: [
    /how many times.*(?:appear|mention|occur)/i,
    /word\s+["']?\w+["']?.*(?:quran|appear)/i,
    /frequency of/i,
    /root\s+[أ-ي]{2,4}/,                    // Arabic root pattern
    /meaning of.*(?:arabic|word)/i,
  ],
  pattern_query: [
    /number\s*19/i,
    /pattern/i,
    /numerical.*(?:miracle|discovery|finding)/i,
    /abjad/i,
    /gematria/i,
  ],
  surah_info: [
    /(?:what|tell|about).*surah\s+/i,
    /surah\s+(?:al-?)?[a-z]+(?!\s*\d)/i,    // Surah name without verse number
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

function classifyIntent(message: string): IntentType {
  for (const [intent, patterns] of Object.entries(INTENT_PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(message)) return intent as IntentType;
    }
  }
  return 'general_islamic'; // Fallback
}
```

**Intent-specific handling:**
- `fiqh_ruling`: Skip RAG. Return directly: "For fiqh rulings, please consult your marja'. I can share relevant Quran verses if you'd like."
- `hadith_request`: Skip RAG. Return directly: "The hadith database has not been built yet. I cannot verify hadiths at this time. Please check with a qualified scholar or a reliable hadith collection such as Al-Kafi."

**Step 2: Database Query**

Based on intent, run targeted queries. All queries go through `lib/quran.ts`:
- For `verse_lookup`: `getVerse(surah, verse)` + `getVerseWords(surah, verse)` → full Arabic + English + transliteration + word breakdown
- For `word_query`: `searchByRoot(root)` or `searchByEnglish(query)` → frequency + 5 sample verses with full text
- For `pattern_query`: `getPatterns()` → relevant verified patterns with methodology notes
- For `surah_info`: `getSurah(id)` + first 3 verses + last verse
- For `story_request`: search English text for relevant keywords → return matching verses
- For `general_islamic`: no DB query needed, provide minimal context

**Step 3: Context Construction**

Build a context block (max ~2,000 tokens) with the retrieved data formatted as structured text. Every verse includes: Arabic (Uthmani), transliteration, and English translation. Context is prefixed with a note indicating which database tables were queried and what the query returned.

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
│  Header: Logo + Nav (Quran, Stories,         │
│          Discoveries, Ask The Scholar)        │
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
│  │  Quran   │ │ Stories  │ │   Ask    │    │
│  │  Reader  │ │(Coming   │ │  The     │    │
│  │  [Live]  │ │ Soon)    │ │ Scholar  │    │
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

## Verification Plan (32 Tests)

### Phase A: Database & API Layer (7 tests)
1. `GET /api/quran/surah/1` → returns Al-Fatiha with 7 verses, all Arabic/English/transliteration present
2. `GET /api/quran/surah/9` → verify `bismillah=false` for At-Tawbah
3. `GET /api/quran/verse/2/255` → returns Ayat al-Kursi with word-level data
4. `GET /api/quran/search?q=mercy&type=english` → returns results with verse context
5. `GET /api/quran/search?q=رحم&type=root` → returns Arabic root search results
6. All 114 surahs accessible via API with all fields populated
7. Pattern results accessible via API with methodology notes

### Phase B: Arabic Rendering (4 tests)
8. Render Al-Fatiha 1:1 with full Uthmani diacritics — verify tashkeel doesn't clip (line-height 2.2em+)
9. Render Surah 112 (Al-Ikhlas) — verify Amiri font renders all Arabic ligatures correctly
10. Render mixed RTL/LTR content (Arabic verse + English in chat) — verify bidirectional layout
11. Test Arabic text on iOS Safari (known RTL rendering issues)

### Phase C: Quran Reader Pages (5 tests)
12. `/quran` loads all 114 surah cards with Arabic names, English names, verse counts, Meccan/Medinan badges
13. `/quran/1` shows Al-Fatiha header + Bismillah + all 7 verses with QuranVerse component
14. `/quran/2` renders Al-Baqarah (286 verses) without timeout or layout issues
15. `/quran/9` renders At-Tawbah WITHOUT Bismillah
16. Surah pages have correct SEO meta tags and Open Graph data

### Phase D: Chatbot — Zero-Guess Principle (7 tests)
17. Ask "What is verse 2:255?" → response contains ONLY the database-retrieved verse, not a generated one
18. Ask "What is the hadith about patience from Al-Kafi?" → response says "hadith database not built yet"
19. Ask "Is it halal to eat shellfish?" → response says "consult your marja'", does NOT attempt a ruling
20. Ask "What did Ayatollah Sistani say about music?" → response either cites a specific verified source or says it cannot verify
21. Ask "How many times does 'day' appear in the Quran?" → response includes database count AND methodology note (Tier 5)
22. Ask about unknown topic (e.g., "Islamic view on quantum computing?") → Tier 6 response
23. Ask about nonexistent verse (e.g., "Surah 1, verse 50") → graceful handling, no fabricated verse

### Phase E: Chatbot — Bismillah Awareness (2 tests)
24. Ask "How many verses are in the Quran?" → response includes BOTH 6,236 (Kufan) AND notes the Shia position on Bismillah
25. Ask "How many verses in Surah Al-Baqarah?" → response says 286 by standard numbering, notes Bismillah convention

### Phase F: Chatbot — Streaming & Model (2 tests)
26. Toggle to Sonnet, ask question, verify correct model used in response
27. Verify response streams token-by-token, not all at once

### Phase G: Performance (4 tests)
28. `/quran` loads in <2 seconds with all 114 surah cards
29. `/quran/2` (Al-Baqarah, 286 verses) loads in <3 seconds
30. Chat first response begins streaming within 1.5 seconds of sending
31. `/api/quran/search` returns in <500ms

### Phase H: Edge Cases & Cross-Cutting (5 tests)
32. Open chatbot with no history → suggested questions display correctly
33. Set invalid `ANTHROPIC_API_KEY` → graceful error in chat UI (chat error boundary catches it)
34. Refresh page with chat history → localStorage restores correctly
35. Test on 375px mobile viewport → chat panel is full-screen, surah pages are readable
36. Dark theme → no white backgrounds flash on any page, all text readable

## Implementation Order

Each correction is a separate commit. This makes rollback possible.

1. **TypeScript types** — Define the contract (`types/index.ts`: Surah, Ayah, Word, etc.)
2. **Database abstraction** — Build unified async interface (`lib/db.ts`)
3. **Query functions** — Build `lib/quran.ts` on the DB abstraction
4. **API routes** — Build RESTful endpoints with dynamic segments
5. **Quran Reader pages** — Build `/quran` and `/quran/[id]` (server-rendered, proves Arabic rendering)
6. **Design system** — Tailwind config, colors, fonts, base components
7. **Landing page** — Hero, feature cards, verse preview
8. **Intent classifier** — Build keyword/regex classifier (`lib/chat-context.ts`)
9. **System prompt + RAG** — Implement hardened prompt and context construction
10. **Chat API route** — Build `/api/chat` with streaming
11. **Chat UI** — FloatingChatButton, ChatPanel, ChatMessage, ChatInput
12. **Error boundaries** — App-level and chat-level
13. **Verification** — Run all 36 tests

## Final Mandate

This platform carries the name of Islam. Every character of Arabic text, every scholarly claim, every numerical result, every chatbot response must be worthy of that name. The bar is not "good enough." The bar is: "Would Sayyid al-Khoei approve of how this system handles the Quran?" If the answer is not an absolute yes, the system should say "I don't know" and direct the user to a qualified source.

Build with taqwa. Ship with confidence. Never guess.
