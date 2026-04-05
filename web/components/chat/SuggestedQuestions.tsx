const QUESTIONS = [
  "What does the Quran say about patience?",
  "Tell me about Surah Al-Fatiha verse by verse",
  "How many times does the word 'mercy' appear in the Quran?",
  "What is Surah Al-Ikhlas about?",
  "What is the significance of the number 19 in the Quran?",
  "Show me verses about justice",
];

export default function SuggestedQuestions({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="p-4">
      <p className="text-text-secondary text-xs mb-3">Try asking:</p>
      <div className="flex flex-wrap gap-2">
        {QUESTIONS.map((q) => (
          <button key={q} onClick={() => onSelect(q)}
            className="text-xs px-3 py-2 rounded-full border border-accent-gold/30 text-accent-gold hover:bg-accent-gold/10 transition-colors text-left">
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
