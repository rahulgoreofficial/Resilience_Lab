import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import type { NodeCriticalityItem } from '../../types/analytics';
import { Card } from '../common/Card';
import { useTheme } from '../common/ThemeProvider';

export interface ResilienceChartsProps {
  criticalNodes: NodeCriticalityItem[];
  simulationData?: Array<{ fraction: string; randomLcc: number; targetedLcc: number }>;
  nodeTypeDistribution?: Array<{ name: string; count: number; color: string }>;
  cascadingProgression?: Array<{ round: string; activeNodes: number; unservedLoad: number }>;
}

export const ResilienceCharts: React.FC<ResilienceChartsProps> = ({
  criticalNodes,
  simulationData,
  nodeTypeDistribution,
  cascadingProgression
}) => {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  // Theme-aware color variables
  const gridStroke = isDark ? 'rgba(37, 49, 73, 0.6)' : 'rgba(226, 232, 240, 0.8)';
  const tickFill = isDark ? '#929CB3' : '#64748B';
  const tooltipStyle = {
    backgroundColor: isDark ? '#0D1220' : '#FFFFFF',
    borderColor: isDark ? '#253149' : '#E2E8F0',
    color: isDark ? '#F5F7FF' : '#171923',
    borderRadius: '14px',
    fontSize: '12px',
    fontFamily: 'monospace',
    boxShadow: isDark ? '0 12px 30px rgba(0,0,0,0.45)' : '0 8px 24px rgba(0,0,0,0.08)'
  };

  // Format top 8 critical nodes
  const chartData = criticalNodes.slice(0, 8).map((node) => ({
    node_id: node.node_id,
    drop: parseFloat(((node.connectivity_drop || 0) * 100).toFixed(1)),
    degree: node.degree,
    isAP: node.is_articulation_point
  }));

  // Percolation curve data
  const comparisonData = simulationData || [
    { fraction: '0%', randomLcc: 100, targetedLcc: 100 },
    { fraction: '10%', randomLcc: 96, targetedLcc: 78 },
    { fraction: '20%', randomLcc: 91, targetedLcc: 52 },
    { fraction: '30%', randomLcc: 83, targetedLcc: 28 },
    { fraction: '40%', randomLcc: 72, targetedLcc: 12 },
    { fraction: '50%', randomLcc: 58, targetedLcc: 4 },
  ];

  // Component archetype breakdown
  const archetypeData = nodeTypeDistribution || [
    { name: 'Routers', count: 2, color: '#4F8CFF' },
    { name: 'Switches', count: 4, color: '#22D3EE' },
    { name: 'Servers', count: 4, color: '#20D6A0' },
    { name: 'Databases', count: 1, color: '#9B7BFF' },
    { name: 'Gateways', count: 1, color: '#FF784F' },
  ];

  // Cascading failure overload progression
  const cascadeData = cascadingProgression || [
    { round: 'Round 0', activeNodes: 12, unservedLoad: 0 },
    { round: 'Round 1', activeNodes: 11, unservedLoad: 12 },
    { round: 'Round 2', activeNodes: 9, unservedLoad: 38 },
    { round: 'Round 3', activeNodes: 8, unservedLoad: 65 },
    { round: 'Stabilized', activeNodes: 8, unservedLoad: 68 },
  ];

  return (
    <div className="space-y-6">
      {/* Row 1: Top 2 Primary Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Node Criticality Ranking */}
        <Card
          header={
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">
                  Component Vulnerability Ranking (Δ Connectivity %)
                </h4>
                <p className="text-[11px] text-slate-400 dark:text-[#69758E] font-mono-code">Ranked by topological fragmentation drop</p>
              </div>
              <span className="text-[10px] text-indigo-600 dark:text-[#9B7BFF] bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200/80 dark:border-indigo-800/60 px-2 py-0.5 rounded-full font-mono-code font-semibold">
                Top Cut-Vertices
              </span>
            </div>
          }
        >
          <div className="h-72 w-full">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 15, right: 15, left: -15, bottom: 20 }}>
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366F1" stopOpacity="0.95" />
                      <stop offset="100%" stopColor="#4F8CFF" stopOpacity="0.75" />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                  <XAxis dataKey="node_id" tick={{ fill: tickFill, fontSize: 11, fontFamily: 'monospace' }} />
                  <YAxis unit="%" tick={{ fill: tickFill, fontSize: 11, fontFamily: 'monospace' }} />
                  <Tooltip
                    contentStyle={tooltipStyle}
                    formatter={(val: any) => [`${val}% drop`, 'Connectivity Impact']}
                  />
                  <Bar dataKey="drop" fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-xs text-slate-400">
                No criticality data loaded
              </div>
            )}
          </div>
        </Card>

        {/* Chart 2: Percolation Comparison (Random vs Targeted Attack) */}
        <Card
          header={
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">
                  Percolation: Random vs Targeted Attacks
                </h4>
                <p className="text-[11px] text-slate-400 dark:text-[#69758E] font-mono-code">LCC Giant Cluster Degradation Curves</p>
              </div>
              <span className="text-[10px] text-cyan-600 dark:text-[#22D3EE] bg-cyan-50 dark:bg-cyan-950/50 border border-cyan-200/80 dark:border-cyan-800/60 px-2 py-0.5 rounded-full font-mono-code font-semibold">
                Percolation Theory
              </span>
            </div>
          }
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={comparisonData} margin={{ top: 15, right: 20, left: -15, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                <XAxis dataKey="fraction" tick={{ fill: tickFill, fontSize: 11, fontFamily: 'monospace' }} />
                <YAxis unit="%" tick={{ fill: tickFill, fontSize: 11, fontFamily: 'monospace' }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace', paddingTop: '10px' }} />
                <Line
                  type="monotone"
                  dataKey="randomLcc"
                  name="Random Outages (Uniform)"
                  stroke="#22D3EE"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#22D3EE' }}
                />
                <Line
                  type="monotone"
                  dataKey="targetedLcc"
                  name="Targeted Hub Attacks (Adversarial)"
                  stroke="#FF784F"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#FF784F' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Row 2: Secondary Visualizers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 3: Cascading Failure Overload Progression */}
        <Card
          header={
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">
                  Cascading Overload Progression
                </h4>
                <p className="text-[11px] text-slate-400 dark:text-[#69758E] font-mono-code">Surviving nodes vs Unserved traffic overload</p>
              </div>
              <span className="text-[10px] text-amber-600 dark:text-[#F6BD60] bg-amber-50 dark:bg-amber-950/50 border border-amber-200/80 dark:border-amber-800/60 px-2 py-0.5 rounded-full font-mono-code font-semibold">
                Dynamic Flow Model
              </span>
            </div>
          }
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={cascadeData} margin={{ top: 15, right: 20, left: -15, bottom: 20 }}>
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F6BD60" stopOpacity="0.4" />
                    <stop offset="95%" stopColor="#F6BD60" stopOpacity="0.0" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                <XAxis dataKey="round" tick={{ fill: tickFill, fontSize: 11, fontFamily: 'monospace' }} />
                <YAxis tick={{ fill: tickFill, fontSize: 11, fontFamily: 'monospace' }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace', paddingTop: '10px' }} />
                <Area
                  type="monotone"
                  dataKey="unservedLoad"
                  name="Unserved Traffic Load (%)"
                  stroke="#F6BD60"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#areaGradient)"
                />
                <Line
                  type="monotone"
                  dataKey="activeNodes"
                  name="Surviving Online Nodes"
                  stroke="#20D6A0"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Chart 4: Network Archetype Distribution */}
        <Card
          header={
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">
                  Network Component Distribution
                </h4>
                <p className="text-[11px] text-slate-400 dark:text-[#69758E] font-mono-code">Functional archetype allocation</p>
              </div>
              <span className="text-[10px] text-emerald-600 dark:text-[#20D6A0] bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200/80 dark:border-emerald-800/60 px-2 py-0.5 rounded-full font-mono-code font-semibold">
                Topology Composition
              </span>
            </div>
          }
        >
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
                <Pie
                  data={archetypeData}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                >
                  {archetypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};
