/**
 * Resilience Analytics, Criticality Profiling & Scenario Comparison Types.
 */

export interface ConnectivityAnalysis {
  node_count: number;
  edge_count: number;
  density: number;
  connected_components_count: number;
  largest_component_size: number;
  lcc_ratio: number;
  articulation_points: string[];
  bridges: Array<[string, string]>;
  is_connected: boolean;
  algebraic_connectivity?: number;
}

export interface NodeCriticalityItem {
  node_id: string;
  degree: number;
  is_articulation_point: boolean;
  initial_connectivity: number;
  post_failure_connectivity: number;
  connectivity_drop: number;
  criticality_score: number;
  rank: number;
  betweenness?: number;
}

export interface EdgeCriticalityItem {
  edge_id: string;
  source: string;
  target: string;
  is_bridge: boolean;
  weight: number;
  initial_connectivity: number;
  post_failure_connectivity: number;
  connectivity_drop: number;
  criticality_score: number;
  rank: number;
  betweenness?: number;
}

export interface ResilienceReportResponse {
  markdown_report: string;
  network_name: string;
  generated_at: string;
}

export interface ScenarioComparisonResponse {
  scenarios: Array<{
    name: string;
    failed_elements: string[];
    lcc_size: number;
    lcc_ratio: number;
    pairwise_connectivity: number;
    service_resilience: number;
    connected_components?: number;
  }>;
  comparative_summary: string;
}

