/**
 * Simulation Lifecycle, Configuration, Results & Event Types.
 */

export type SimulationType = 
  | 'node_failure' 
  | 'edge_failure' 
  | 'multiple_failure' 
  | 'random' 
  | 'targeted' 
  | 'cascading';

export type SimulationStatus = 
  | 'queued' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'interrupted';

export interface SimulationRecord {
  id: string;
  network_id: string;
  snapshot_id?: string;
  simulation_type: SimulationType;
  status: SimulationStatus;
  configuration: Record<string, unknown>;
  random_seed?: number;
  results?: SimulationResults;
  error_summary?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface SimulationEvent {
  sequence_number: number;
  event_type: string;
  event_data: Record<string, unknown>;
  created_at: string;
}

export interface SimulationResults {
  simulation_id?: string;
  simulation_type?: string;
  failed_nodes?: string[];
  failed_edges?: Array<[string, string] | string>;
  isolated_nodes?: string[];
  initial_components?: number;
  final_components?: number;
  initial_lcc_size?: number;
  final_lcc_size?: number;
  lcc_ratio?: number;
  initial_pairwise_connectivity?: number;
  final_pairwise_connectivity?: number;
  pairwise_connectivity_ratio?: number;
  service_resilience?: number;
  weighted_service_resilience?: number;
  traffic_loss_ratio?: number;
  cascade_rounds?: number;
  events?: Array<{
    event: string;
    round?: number;
    failed_nodes?: string[];
    failed_edges?: string[];
    [key: string]: unknown;
  }>;
  [key: string]: unknown;
}

export interface NodeFailurePayload {
  failed_node_ids: string[];
  entry_points?: string[];
  critical_services?: string[];
}

export interface EdgeFailurePayload {
  failed_edges: Array<[string, string]>;
  entry_points?: string[];
  critical_services?: string[];
}

export interface MultipleFailurePayload {
  failed_node_ids: string[];
  failed_edges: Array<[string, string]>;
  entry_points?: string[];
  critical_services?: string[];
}

export interface RandomFailurePayload {
  failure_target?: 'nodes' | 'edges' | 'both';
  failure_count?: number;
  failure_percentage?: number;
  num_trials?: number;
  random_seed?: number;
  selection_method?: 'uniform' | 'weighted';
  entry_points?: string[];
  critical_services?: string[];
}

export interface TargetedFailurePayload {
  strategy: 'degree' | 'articulation_points' | 'impact';
  failure_count?: number;
  failure_percentage?: number;
  adaptive?: boolean;
  entry_points?: string[];
  critical_services?: string[];
}

export interface CascadingFailurePayload {
  initial_failed_nodes?: string[];
  initial_failed_edges?: Array<[string, string]>;
  traffic_demands?: Array<{ source: string; target: string; demand: number }>;
  overload_threshold?: number;
  max_simulation_rounds?: number;
  entry_points?: string[];
  critical_services?: string[];
}

