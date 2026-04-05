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
  const colonMatch = message.match(/(\d+):(\d+)/);
  if (colonMatch) return { surah: parseInt(colonMatch[1]), verse: parseInt(colonMatch[2]) };
  const verboseMatch = message.match(/surah\s+(\d+).*verse\s+(\d+)/i);
  if (verboseMatch) return { surah: parseInt(verboseMatch[1]), verse: parseInt(verboseMatch[2]) };
  return null;
}

function extractSearchTerm(message: string): string {
  const wordMatch = message.match(/word\s+["']?(\w+)["']?/i);
  if (wordMatch) return wordMatch[1];
  const aboutMatch = message.match(/(?:about|on|regarding)\s+(\w+)/i);
  if (aboutMatch) return aboutMatch[1];
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
        context = `[Database Query: search for "${term}" in English translations]\n`;
        context += `Found ${results.length} verses containing "${term}".\n\n`;
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
        const numMatch = message.match(/surah\s+(\d+)/i);
        const surahId: number | null = numMatch ? parseInt(numMatch[1]) : null;
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
  if (messages.length > 10) return true;
  if (/\b(theolog|comparative|shia.*sunni|sunni.*shia|debate|scholarly dispute)\b/i.test(currentMessage)) return true;
  if (/\b(pattern|numerical|mathematical|abjad|statistical)\b/i.test(currentMessage)) return true;
  if (/\b(detail|scholarly|in-?depth|thorough)\b/i.test(currentMessage)) return true;
  return false;
}
