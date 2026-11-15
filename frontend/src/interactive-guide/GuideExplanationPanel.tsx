/**
 * GuideExplanationPanel - Right-side panel with text explanation, glossary, quiz.
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, BookOpen, HelpCircle, CheckCircle2, XCircle } from 'lucide-react';
import { CHAPTER_GLOSSARIES, CHAPTER_QUIZZES } from './guideConstants';
import type { GuideChapterId, GlossaryItem } from './guideTypes';

interface GlossaryProps { items: GlossaryItem[] }
function GlossarySection({ items }: GlossaryProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-[#E2E8F0] dark:border-[#253149] rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 bg-[#F8FAFC] dark:bg-[#121A2B] text-sm font-semibold text-[#1E293B] dark:text-[#F5F7FF] cursor-pointer hover:bg-[#F1F5F9] dark:hover:bg-[#182238] transition-colors"
      >
        <span className="flex items-center gap-2"><BookOpen className="w-4 h-4 text-[#F2653A]" /> Glossary</span>
        {open ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>
      {open && (
        <div className="divide-y divide-[#F1F5F9] dark:divide-[#253149] bg-white dark:bg-[#0D1220]">
          {items.map((item) => (
            <div key={item.term} className="px-4 py-3">
              <p className="text-sm font-semibold text-[#171B26] dark:text-[#F5F7FF]">{item.term}</p>
              <p className="text-xs text-[#475569] dark:text-[#929CB3] mt-0.5">{item.simple}</p>
              <p className="text-xs text-[#94A3B8] dark:text-[#69758E] mt-0.5 font-mono">{item.technical}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface QuizProps { chapterId: GuideChapterId }
function QuizSection({ chapterId }: QuizProps) {
  const quiz = CHAPTER_QUIZZES[chapterId];
  const [selected, setSelected] = useState<number | null>(null);
  const [open, setOpen] = useState(false);

  if (!quiz) return null;
  const answered = selected !== null;
  const correct = selected === quiz.correctIndex;

  return (
    <div className="border border-[#E2E8F0] dark:border-[#253149] rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 bg-[#F8FAFC] dark:bg-[#121A2B] text-sm font-semibold text-[#1E293B] dark:text-[#F5F7FF] cursor-pointer hover:bg-[#F1F5F9] dark:hover:bg-[#182238] transition-colors"
      >
        <span className="flex items-center gap-2"><HelpCircle className="w-4 h-4 text-[#7C3AED] dark:text-[#9B7BFF]" /> Knowledge Check</span>
        {open ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>
      {open && (
        <div className="px-4 py-3 space-y-3 bg-white dark:bg-[#0D1220]">
          <p className="text-sm font-medium text-[#1E293B] dark:text-[#F5F7FF]">{quiz.question}</p>
          <div className="space-y-2">
            {quiz.options.map((opt, idx) => {
              let cls = 'border border-[#E2E8F0] dark:border-[#253149] bg-white dark:bg-[#121A2B] hover:bg-[#F8FAFC] dark:hover:bg-[#182238] text-[#475569] dark:text-[#929CB3]';
              if (answered) {
                if (idx === quiz.correctIndex) cls = 'border border-[#22C55E] bg-[#F0FDF4] dark:bg-emerald-950/40 text-[#166534] dark:text-emerald-300';
                else if (idx === selected) cls = 'border border-[#EF4444] bg-[#FEF2F2] dark:bg-rose-950/40 text-[#991B1B] dark:text-rose-300';
                else cls = 'border border-[#E2E8F0] dark:border-[#253149] bg-white dark:bg-[#121A2B] text-[#94A3B8] opacity-60';
              }
              return (
                <button
                  key={idx}
                  disabled={answered}
                  onClick={() => setSelected(idx)}
                  className={`w-full text-left text-xs px-3 py-2 rounded-lg cursor-pointer transition-all ${cls}`}
                >
                  <span className="font-semibold mr-2">{String.fromCharCode(65 + idx)}.</span>
                  {opt}
                </button>
              );
            })}
          </div>
          {answered && (
            <div className={`flex items-start gap-2 text-xs p-3 rounded-lg ${correct ? 'bg-[#F0FDF4] dark:bg-emerald-950/40 text-[#166534] dark:text-emerald-300' : 'bg-[#FEF2F2] dark:bg-rose-950/40 text-[#991B1B] dark:text-rose-300'}`}>
              {correct ? <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" /> : <XCircle className="w-4 h-4 mt-0.5 shrink-0" />}
              <p>{quiz.explanation}</p>
            </div>
          )}
          {answered && (
            <button
              onClick={() => { setSelected(null); setOpen(false); setTimeout(() => setOpen(true), 50); }}
              className="text-xs text-[#7C3AED] dark:text-[#9B7BFF] underline cursor-pointer"
            >
              Try again
            </button>
          )}
        </div>
      )}
    </div>
  );
}

interface GuideExplanationPanelProps {
  chapterId: GuideChapterId;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export const GuideExplanationPanel: React.FC<GuideExplanationPanelProps> = ({
  chapterId, title, subtitle, children,
}) => {
  const glossary = CHAPTER_GLOSSARIES[chapterId] ?? [];

  return (
    <div className="flex flex-col gap-4 overflow-y-auto max-h-full pr-1">
      <div>
        <h2 className="text-lg font-extrabold text-[#171B26] dark:text-[#F5F7FF] tracking-tight">{title}</h2>
        <p className="text-sm text-[#747C8B] dark:text-[#929CB3] mt-0.5">{subtitle}</p>
      </div>

      <div className="space-y-3 text-sm text-[#334155] dark:text-[#929CB3] leading-relaxed">
        {children}
      </div>

      <GlossarySection items={glossary} />
      <QuizSection chapterId={chapterId} />
    </div>
  );
};

