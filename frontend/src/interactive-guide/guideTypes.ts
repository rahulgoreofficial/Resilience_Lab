/**
 * Interactive 3D Network Lab - Type Definitions
 * Used across all guide chapters and components.
 */

import type { CytoscapeNodeData, CytoscapeEdgeData } from '../types/network';
import type { ConnectivityAnalysis } from '../types/analytics';
import type { SimulationResults } from '../types/simulation';

export type GuideChapterId = 1 | 2 | 3 | 4 | 5 | 6;

export interface GuideChapter {
  id: GuideChapterId;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
}

export interface NodeState {
  id: string;
  status: 'healthy' | 'critical' | 'failed' | 'disconnected' | 'selected' | 'highlighted';
  isBridge?: boolean;
  isArticulationPoint?: boolean;
}

export interface EdgeState {
  id: string;
  status: 'healthy' | 'bridge' | 'failed' | 'active_path' | 'highlighted';
}

export interface GuideNetworkState {
  nodes: CytoscapeNodeData[];
  edges: CytoscapeEdgeData[];
  nodeStates: Map<string, NodeState>;
  edgeStates: Map<string, EdgeState>;
  analysis: ConnectivityAnalysis | null;
  simulationResult: SimulationResults | null;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface GlossaryItem {
  term: string;
  simple: string;
  technical: string;
}

export interface PresentationStep {
  id: number;
  title: string;
  caption: string;
  chapter: GuideChapterId;
  cameraTarget?: [number, number, number];
  highlightNodes?: string[];
  highlightEdges?: string[];
  autoAction?: 'none' | 'show_articulation' | 'show_bridges' | 'show_components';
}

