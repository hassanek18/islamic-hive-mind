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
  data: string | null;
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
  | 'dua_request'
  | 'general_islamic';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  model?: 'haiku' | 'sonnet';
}
