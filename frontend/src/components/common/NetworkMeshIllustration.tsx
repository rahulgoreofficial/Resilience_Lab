import React from 'react';

export const NetworkMeshIllustration: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`relative overflow-hidden select-none pointer-events-none flex items-center justify-center ${className}`}>
      {/* Ambient background glow blur discs */}
      <div className="absolute top-1/4 right-1/4 w-72 h-72 rounded-full bg-cyan-400/15 blur-3xl" />
      <div className="absolute bottom-1/4 left-1/4 w-80 h-80 rounded-full bg-indigo-500/20 blur-3xl" />
      <div className="absolute top-1/3 left-1/3 w-64 h-64 rounded-full bg-purple-500/15 blur-3xl" />

      <svg
        viewBox="0 0 680 460"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full relative z-10 animate-float"
      >
        <defs>
          {/* Glow Filters */}
          <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <filter id="coreGlow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>

          {/* Gradients */}
          <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366F1" stopOpacity="0.9" />
            <stop offset="55%" stopColor="#3B82F6" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#22D3EE" stopOpacity="0.9" />
          </linearGradient>

          <linearGradient id="violetCyan" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#22D3EE" stopOpacity="0.85" />
          </linearGradient>

          <linearGradient id="orangePulse" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#F2653A" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#EA580C" stopOpacity="0.3" />
          </linearGradient>

          <radialGradient id="centerRadial" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#22D3EE" stopOpacity="0.4" />
            <stop offset="60%" stopColor="#6366F1" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#080E1C" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Ambient Center Radial Glow */}
        <circle cx="340" cy="230" r="180" fill="url(#centerRadial)" />

        {/* 3D Wireframe Perspective Ellipses */}
        <g stroke="#334155" strokeWidth="0.75" opacity="0.4">
          <ellipse cx="340" cy="230" rx="270" ry="140" strokeDasharray="3 4" />
          <ellipse cx="340" cy="230" rx="200" ry="100" stroke="url(#violetCyan)" strokeWidth="1" opacity="0.6" strokeDasharray="5 3" />
          <ellipse cx="340" cy="230" rx="120" ry="60" stroke="#22D3EE" strokeWidth="1.2" opacity="0.7" />
        </g>

        {/* Diagonal Perspective Rays */}
        <g stroke="#1E293B" strokeWidth="0.75" opacity="0.5">
          <line x1="120" y1="80" x2="560" y2="380" strokeDasharray="4 4" />
          <line x1="120" y1="380" x2="560" y2="80" strokeDasharray="4 4" />
        </g>

        {/* Primary Mesh Links */}
        <g strokeLinecap="round">
          {/* Backbone Violet / Cyan Trunks */}
          <line x1="200" y1="160" x2="340" y2="110" stroke="url(#brandGrad)" strokeWidth="2.2" opacity="0.85" />
          <line x1="340" y1="110" x2="480" y2="160" stroke="url(#brandGrad)" strokeWidth="2.2" opacity="0.85" />
          <line x1="480" y1="160" x2="520" y2="280" stroke="url(#brandGrad)" strokeWidth="2" opacity="0.8" />
          <line x1="520" y1="280" x2="390" y2="340" stroke="url(#brandGrad)" strokeWidth="2" opacity="0.8" />
          <line x1="390" y1="340" x2="230" y2="320" stroke="url(#brandGrad)" strokeWidth="2" opacity="0.8" />
          <line x1="230" y1="320" x2="160" y2="240" stroke="url(#brandGrad)" strokeWidth="2" opacity="0.8" />
          <line x1="160" y1="240" x2="200" y2="160" stroke="url(#brandGrad)" strokeWidth="2.2" opacity="0.85" />

          {/* Central Hub Radial Struts */}
          <line x1="200" y1="160" x2="340" y2="230" stroke="#22D3EE" strokeWidth="1.5" opacity="0.75" />
          <line x1="340" y1="110" x2="340" y2="230" stroke="#3B82F6" strokeWidth="2.2" opacity="0.9" />
          <line x1="480" y1="160" x2="340" y2="230" stroke="#22D3EE" strokeWidth="1.5" opacity="0.75" />
          <line x1="520" y1="280" x2="340" y2="230" stroke="#6366F1" strokeWidth="1.5" opacity="0.7" />
          <line x1="390" y1="340" x2="340" y2="230" stroke="#3B82F6" strokeWidth="1.8" opacity="0.8" />
          <line x1="230" y1="320" x2="340" y2="230" stroke="#6366F1" strokeWidth="1.5" opacity="0.7" />
          <line x1="160" y1="240" x2="340" y2="230" stroke="#22D3EE" strokeWidth="1.5" opacity="0.75" />

          {/* Redundancy chords & cross-links */}
          <line x1="200" y1="160" x2="390" y2="340" stroke="#A78BFA" strokeWidth="1" strokeDasharray="3 3" opacity="0.5" />
          <line x1="480" y1="160" x2="230" y2="320" stroke="#A78BFA" strokeWidth="1" strokeDasharray="3 3" opacity="0.5" />
          <line x1="160" y1="240" x2="520" y2="280" stroke="#38BDF8" strokeWidth="1" strokeDasharray="4 3" opacity="0.45" />

          {/* Critical Single-Point Bridge Highlight in Brand Orange */}
          <line x1="340" y1="110" x2="340" y2="40" stroke="url(#orangePulse)" strokeWidth="2.5" opacity="0.95" />
        </g>

        {/* Central Orchestrator / Core Switch Node */}
        <g filter="url(#coreGlow)">
          <circle cx="340" cy="230" r="20" fill="#080E1C" stroke="#22D3EE" strokeWidth="2.5" />
          <circle cx="340" cy="230" r="10" fill="#3B82F6" opacity="0.8" />
          <circle cx="340" cy="230" r="4" fill="#FFFFFF" />
        </g>

        {/* Top Edge / Internet Gateway Node */}
        <g filter="url(#softGlow)">
          <circle cx="340" cy="40" r="13" fill="#080E1C" stroke="#F2653A" strokeWidth="2.5" />
          <circle cx="340" cy="40" r="5" fill="#F2653A" />
        </g>

        {/* Peripheral Nodes with High-Depth Rings */}
        {/* North-West Core Router */}
        <g filter="url(#softGlow)">
          <circle cx="200" cy="160" r="11" fill="#080E1C" stroke="#6366F1" strokeWidth="2" />
          <circle cx="200" cy="160" r="4" fill="#A78BFA" />
        </g>

        {/* North-East Core Router */}
        <g filter="url(#softGlow)">
          <circle cx="480" cy="160" r="11" fill="#080E1C" stroke="#3B82F6" strokeWidth="2" />
          <circle cx="480" cy="160" r="4" fill="#60A5FA" />
        </g>

        {/* West Switch */}
        <circle cx="160" cy="240" r="9" fill="#080E1C" stroke="#22D3EE" strokeWidth="1.8" />
        <circle cx="160" cy="240" r="3" fill="#22D3EE" />

        {/* South-West Server */}
        <circle cx="230" cy="320" r="8" fill="#080E1C" stroke="#10B981" strokeWidth="1.8" />
        <circle cx="230" cy="320" r="3" fill="#10B981" />

        {/* South Data Center */}
        <g filter="url(#softGlow)">
          <circle cx="390" cy="340" r="10" fill="#080E1C" stroke="#8B5CF6" strokeWidth="2" />
          <circle cx="390" cy="340" r="3.5" fill="#A78BFA" />
        </g>

        {/* East Distribution Switch */}
        <circle cx="520" cy="280" r="9" fill="#080E1C" stroke="#22D3EE" strokeWidth="1.8" />
        <circle cx="520" cy="280" r="3" fill="#22D3EE" />

        {/* North Aggregator */}
        <g filter="url(#softGlow)">
          <circle cx="340" cy="110" r="12" fill="#080E1C" stroke="#3B82F6" strokeWidth="2.2" />
          <circle cx="340" cy="110" r="4.5" fill="#38BDF8" />
        </g>

        {/* Animated Data Packets (Pulsing glowing dots) */}
        <circle cx="270" cy="195" r="2.5" fill="#22D3EE" filter="url(#softGlow)">
          <animate attributeName="cx" values="200;340;200" dur="4s" repeatCount="indefinite" />
          <animate attributeName="cy" values="160;230;160" dur="4s" repeatCount="indefinite" />
        </circle>
        <circle cx="410" cy="195" r="2.5" fill="#6366F1" filter="url(#softGlow)">
          <animate attributeName="cx" values="480;340;480" dur="3.5s" repeatCount="indefinite" />
          <animate attributeName="cy" values="160;230;160" dur="3.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="340" cy="75" r="2.5" fill="#F2653A" filter="url(#softGlow)">
          <animate attributeName="cy" values="40;110;40" dur="2.5s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  );
};
