/**
 * GuideProgress - Chapter progress bar and chapter navigation pills.
 */

import React from 'react';
import { CHAPTERS } from './guideConstants';
import type { GuideChapterId } from './guideTypes';

interface GuideProgressProps {
  currentChapter: GuideChapterId;
  onNavigate: (id: GuideChapterId) => void;
}

export const GuideProgress: React.FC<GuideProgressProps> = ({ currentChapter, onNavigate }) => {
  return (
    <div className="flex items-center gap-1 flex-wrap">
      {CHAPTERS.map((ch, idx) => {
        const isActive = ch.id === currentChapter;
        const isDone = ch.id < currentChapter;
        return (
          <React.Fragment key={ch.id}>
            <button
              onClick={() => onNavigate(ch.id)}
              title={ch.title}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                isActive
                  ? 'bg-[#F2653A] text-white shadow-sm font-bold'
                  : isDone
                  ? 'bg-[#FEF2EE] dark:bg-orange-950/40 text-[#F2653A] border border-[#FECDB0] dark:border-orange-800/50'
                  : 'bg-[#F1F5F9] dark:bg-[#121A2B] text-[#64748B] dark:text-[#929CB3] hover:bg-[#E2E8F0] dark:hover:bg-[#182238] border border-transparent'
              }`}
            >
              <span>{ch.icon}</span>
              <span className="hidden sm:inline">{ch.title}</span>
              <span className="sm:hidden">{ch.id}</span>
            </button>
            {idx < CHAPTERS.length - 1 && (
              <div className={`h-0.5 w-4 rounded ${isDone ? 'bg-[#F2653A]' : 'bg-[#E2E8F0] dark:bg-[#253149]'}`} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

