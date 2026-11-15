/**
 * FacultyPresentationMode - Guided walkthrough with step captions, camera cues, and controls.
 */

import React, { useState, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Pause, Play, X, Monitor } from 'lucide-react';
import { PRESENTATION_STEPS } from './guideConstants';
import type { PresentationStep, GuideChapterId } from './guideTypes';

interface Props {
  onClose: () => void;
  onStepChange: (step: PresentationStep) => void;
  onNavigateChapter: (id: GuideChapterId) => void;
}

export const FacultyPresentationMode: React.FC<Props> = ({ onClose, onStepChange, onNavigateChapter }) => {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [isPaused, setIsPaused] = useState(true);

  const step = PRESENTATION_STEPS[currentIdx];

  const goTo = useCallback((idx: number) => {
    const next = PRESENTATION_STEPS[idx];
    if (!next) return;
    setCurrentIdx(idx);
    onStepChange(next);
    onNavigateChapter(next.chapter);
  }, [onStepChange, onNavigateChapter]);

  const prev = () => goTo(Math.max(0, currentIdx - 1));
  const next = () => goTo(Math.min(PRESENTATION_STEPS.length - 1, currentIdx + 1));

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center pb-6 pointer-events-none">
      <div className="bg-[#0B1120] border border-[#1E293B] rounded-xl shadow-2xl p-4 w-[600px] mx-4 pointer-events-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Monitor className="w-4 h-4 text-[#F2653A]" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">Faculty Demonstration Mode</span>
          </div>
          <button onClick={onClose} className="text-[#64748B] hover:text-white cursor-pointer transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-[#1E293B] rounded-full h-1 mb-3">
          <div
            className="h-1 bg-[#F2653A] rounded-full transition-all duration-300"
            style={{ width: `${((currentIdx + 1) / PRESENTATION_STEPS.length) * 100}%` }}
          />
        </div>

        {/* Step info */}
        <div className="mb-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] text-[#475569] font-mono">
              Step {currentIdx + 1} of {PRESENTATION_STEPS.length}
            </span>
            <span className="text-[11px] text-[#F2653A] font-semibold">Chapter {step.chapter}</span>
          </div>
          <p className="text-white font-bold text-sm">{step.title}</p>
          <p className="text-[#94A3B8] text-xs mt-0.5 leading-relaxed">{step.caption}</p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={prev}
            disabled={currentIdx === 0}
            className="flex items-center gap-1 text-xs text-[#94A3B8] hover:text-white disabled:opacity-30 cursor-pointer transition-colors px-3 py-1.5 rounded border border-[#1E293B] hover:border-[#334155]"
          >
            <ChevronLeft className="w-3.5 h-3.5" /> Previous
          </button>

          <button
            onClick={() => setIsPaused(!isPaused)}
            className="flex items-center gap-1 text-xs text-[#94A3B8] hover:text-white cursor-pointer transition-colors px-3 py-1.5 rounded border border-[#1E293B] hover:border-[#334155]"
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
            {isPaused ? 'Resume' : 'Pause'}
          </button>

          <button
            onClick={next}
            disabled={currentIdx === PRESENTATION_STEPS.length - 1}
            className="flex-1 flex items-center justify-center gap-1 text-xs bg-[#F2653A] text-white px-3 py-1.5 rounded hover:bg-[#E0552A] disabled:opacity-30 cursor-pointer transition-colors"
          >
            {currentIdx === PRESENTATION_STEPS.length - 1 ? 'Finish' : 'Next'} <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Chapter dots */}
        <div className="flex items-center justify-center gap-1 mt-3">
          {PRESENTATION_STEPS.map((s, i) => (
            <button
              key={s.id}
              onClick={() => goTo(i)}
              title={s.title}
              className={`rounded-full transition-all cursor-pointer ${
                i === currentIdx ? 'w-4 h-2 bg-[#F2653A]' : 'w-2 h-2 bg-[#334155] hover:bg-[#475569]'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

