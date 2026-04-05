# Islamic Hive Mind — Sub-Project 1: Foundation + AI Chatbot

## Context

The Islamic Hive Mind data layer (Phase 1) is complete: 114 surahs, 6,236 ayat, 77,429 words, 325,665 letters in a SQLite database with full Arabic, English, transliteration, morphology, and Abjad values. No web code exists yet.

This sub-project builds the Next.js app shell, database API layer, design system, and AI chatbot. Stories and Discoveries sections will be built as separate sub-projects afterward.

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
│   │   │       ├── surah/route.ts    ← GET: surah metadata + verses
│   │   │       ├── verse/route.ts    ← GET: single verse with all fields
│   │   │       └── search/route.ts   ← GET: search by word, root, or English text
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx         ← Slide-out chat panel (used on every page)
│   │   │   ├── ChatMessage.tsx       ← Single message bubble (user or assistant)
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
│   │       └── LoadingDots.tsx       ← Typing indicator for chat
│   ├── lib/
│   │   ├── db.ts                     ← Database abstraction (better-sqlite3 dev / Turso prod)
│   │   ├── quran.ts                  ← Quran query functions (getSurah, getVerse, searchRoot, etc.)
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
│   └── .env.local                    ← ANTHROPIC_API_KEY, DATABASE_URL
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

## Database Layer

### Abstraction (`lib/db.ts`)

```typescript
// Environment-based driver selection
// DEV:  better-sqlite3 reading from ../db/hive-mind.db
// PROD: @libsql/client connecting to Turso URL

export function getDb(): Database {
  if (process.env.TURSO_DATABASE_URL) {
    return createTursoClient(...)
  }
  return new BetterSqlite3(path.join(process.cwd(), '../db/hive-mind.db'))
}
```

Both drivers expose the same interface: `prepare(sql).all(params)` / `.get(params)` / `.run(params)`.

### Query Functions (`lib/quran.ts`)

```typescript
getSurah(id: number): Surah                    // Full surah metadata
getSurahVerses(id: number): Ayah[]              // All verses of a surah
getVerse(surah: number, verse: number): Ayah    // Single verse with all fields
searchByRoot(root: string): SearchResult[]      // All words with this root
searchByEnglish(query: string): SearchResult[]  // FTS on English text
getWordFrequency(root: string): FrequencyResult // Root frequency + sample verses
getSurahStats(): SurahStats[]                   // All surah statistics
getPatterns(): Pattern[]                        // Verified patterns
```

### API Routes

| Route | Method | Purpose | Response |
|-------|--------|---------|----------|
| `/api/quran/surah?id=1` | GET | Surah metadata + verses | `{ surah: Surah, verses: Ayah[] }` |
| `/api/quran/verse?surah=2&verse=255` | GET | Single verse | `{ verse: Ayah, words: Word[] }` |
| `/api/quran/search?q=mercy&type=english` | GET | Search corpus | `{ results: SearchResult[] }` |
| `/api/chat` | POST | Chatbot (streaming) | SSE stream |

## AI Chatbot — "The Scholar"

### System Prompt

```
You are The Scholar — an AI assistant for the Islamic Hive Mind knowledge base. 
You speak with warmth, wisdom, and scholarly precision, grounded in the Shia 
Islamic tradition while being respectful of all perspectives.

PERSONALITY:
- Warm and approachable — like a patient teacher speaking to a curious student
- Scholarly but not dry — cite sources naturally, not pedantically
- Honest about limitations — say "scholars differ on this" when they do
- Shia-primary — present the Shia perspective first, note Sunni differences where relevant
- Never fabricate — if you don't have data, say so

CAPABILITIES (powered by the Quran database):
- Look up any verse by surah and verse number
- Search for words by Arabic root or English meaning
- Show word frequencies and distributions
- Explain pattern analysis results
- Tell stories from the Quran with verse references

WHEN CITING QURAN VERSES:
- Always show: Arabic text, transliteration, and English translation
- Format: "Surah Name (Chapter:Verse)"
- Use the data provided in the context block below

CONTEXT FROM DATABASE:
{database_context}

CONVERSATION HISTORY:
{history}

USER QUESTION:
{question}
```

### RAG Pipeline (`lib/chat-context.ts`)

**Step 1: Intent Classification**

Analyze the user's message to determine query type:
- `verse_lookup` — asking about a specific verse → fetch from ayat
- `word_query` — asking about a word/concept → search words table by root or English
- `pattern_query` — asking about numerical patterns → fetch from patterns table
- `surah_info` — asking about a surah → fetch surah metadata
- `story_request` — asking for a narrative → fetch relevant verses
- `general_islamic` — general question → provide minimal DB context, rely on Claude's knowledge

**Step 2: Database Query**

Based on intent, run targeted queries:
- For `verse_lookup`: `getVerse(surah, verse)` → full Arabic + English + transliteration
- For `word_query`: `searchByRoot(root)` → frequency + 5 sample verses
- For `pattern_query`: `getPatterns()` → relevant verified patterns
- For `surah_info`: `getSurah(id)` + first 3 verses + last verse

**Step 3: Context Construction**

Build a context block (max ~2000 tokens) with the retrieved data formatted as structured text. Include raw Arabic, English translation, and transliteration for any verses.

**Step 4: Model Selection**

- Default: Claude Haiku (`claude-haiku-4-5-20251001`)
- Auto-escalate to Sonnet (`claude-sonnet-4-6`) when:
  - Conversation exceeds 5 turns
  - User asks about theological disputes or comparative religion
  - Query involves pattern analysis or mathematical content
  - User explicitly requests "detailed" or "scholarly" response
- Manual toggle available in chat UI (small icon button)

**Step 5: Stream to Client**

Use the Anthropic SDK with streaming enabled. Pipe the stream to the client via the Vercel AI SDK's `StreamingTextResponse` or standard SSE.

### Chat UI

**Floating Button:**
- Bottom-right corner, fixed position
- Gold Islamic geometric icon (octagonal star or arabesque)
- Subtle pulse animation when idle
- Click → slide-out panel from right (480px wide on desktop, full-screen on mobile)

**Chat Panel:**
- Dark background (`--bg-chat`)
- Header: "The Scholar" with subtitle "Ask me anything about the Quran & Islam"
- Model indicator: small badge showing "Haiku" or "Sonnet"
- Message area: scrollable, auto-scroll to bottom on new messages
- User messages: right-aligned, gold accent bubble
- Assistant messages: left-aligned, dark card with cream text
- Quran verses within messages: rendered with `<QuranVerse>` component (Arabic large, English below)
- Typing indicator: three pulsing gold dots
- Input: dark input field with gold send button, placeholder "Ask about the Quran..."

**Suggested Questions (shown when chat is empty):**
- "What does the Quran say about patience?"
- "Tell me the story of Prophet Yusuf"
- "How many times does 'mercy' appear?"
- "What happened at Karbala?"
- "What is the significance of the number 19?"
- "Explain Surah Al-Fatiha verse by verse"

**Full-Page Experience (`/ask`):**
- Same chat interface but centered, wider (800px), with more vertical space
- Sidebar with conversation history (localStorage)
- Markdown rendering in assistant messages (headers, lists, bold, code blocks)

### Chat State Management

```typescript
// hooks/useChat.ts
- messages: ChatMessage[]            (persisted to localStorage)
- isLoading: boolean
- model: 'haiku' | 'sonnet'
- sendMessage(content: string): void (POST to /api/chat, handle stream)
- clearChat(): void
- toggleModel(): void
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
│  Random beautiful verse displayed in          │
│  Arabic (Amiri) + English + transliteration  │
│  [Refresh] for a new verse                   │
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

1. **Database API:** Hit each endpoint in the browser, verify JSON responses match DB content
2. **QuranVerse component:** Render Al-Fatiha 1:1 — verify Arabic displays correctly in Amiri font, RTL, with English and transliteration below
3. **Chatbot basic flow:** Ask "What is Surah Al-Fatiha?" → verify streaming response with verse citations
4. **Chatbot RAG:** Ask "How many times does mercy appear?" → verify DB query runs and count is included in response
5. **Model switching:** Toggle to Sonnet, ask a question, verify response comes from the correct model
6. **Mobile responsive:** Test chat panel on 375px viewport
7. **Dark theme:** Verify all text is readable, no white backgrounds flash
8. **localStorage:** Send messages, refresh page, verify history persists
