import { apiClient } from './api';
import type {
  ConnectivityAnalysis,
  NodeCriticalityItem,
  EdgeCriticalityItem,
  ResilienceReportResponse,
  ScenarioComparisonResponse
} from '../types/analytics';

export const analyzeNetwork = async (networkId: string): Promise<ConnectivityAnalysis> => {
  const response = await apiClient.get<ConnectivityAnalysis>(`/v1/networks/${networkId}/analysis`);
  return response.data;
};

export const fetchNodeCriticality = async (networkId: string): Promise<NodeCriticalityItem[]> => {
  const response = await apiClient.get<{ top_nodes: NodeCriticalityItem[] } | NodeCriticalityItem[]>(
    `/v1/networks/${networkId}/criticality`,
    { params: { target: 'nodes' } }
  );
  if (Array.isArray(response.data)) return response.data;
  if (response.data && Array.isArray((response.data as { top_nodes: NodeCriticalityItem[] }).top_nodes)) {
    return (response.data as { top_nodes: NodeCriticalityItem[] }).top_nodes;
  }
  return [];
};

export const fetchEdgeCriticality = async (networkId: string): Promise<EdgeCriticalityItem[]> => {
  const response = await apiClient.get<{ top_edges: EdgeCriticalityItem[] } | EdgeCriticalityItem[]>(
    `/v1/networks/${networkId}/criticality`,
    { params: { target: 'edges' } }
  );
  if (Array.isArray(response.data)) return response.data;
  if (response.data && Array.isArray((response.data as { top_edges: EdgeCriticalityItem[] }).top_edges)) {
    return (response.data as { top_edges: EdgeCriticalityItem[] }).top_edges;
  }
  return [];
};

export const compareScenarios = async (
  networkId: string,
  scenarios: Array<{ name: string; failed_node_ids?: string[]; failed_edges?: Array<[string, string]> }>
): Promise<ScenarioComparisonResponse> => {
  const response = await apiClient.post<ScenarioComparisonResponse>(
    `/v1/networks/${networkId}/comparisons`,
    { scenarios }
  );
  return response.data;
};

export const generateResilienceReport = async (networkId: string): Promise<ResilienceReportResponse> => {
  const response = await apiClient.get<ResilienceReportResponse>(`/v1/networks/${networkId}/report`);
  return response.data;
};

export const computeShortestPath = async (
  networkId: string,
  source: string,
  target?: string
): Promise<{ source: string; target?: string; path?: string[]; distance?: number; all_distances?: Record<string, number> }> => {
  const response = await apiClient.post(
    `/v1/networks/${networkId}/connectivity`,
    { source, target }
  ).catch(async () => {
    // Fallback to legacy Dijkstra endpoint if needed
    const topo = await apiClient.get(`/v1/networks/${networkId}/topology`);
    const graphData = {
      name: topo.data.name,
      directed: false,
      multigraph: false,
      nodes: topo.data.nodes,
      edges: topo.data.edges.map((e: { edge_id: string; source_node_id: string; target_node_id: string; weight: number }) => ({
        edge_id: e.edge_id,
        source: e.source_node_id,
        target: e.target_node_id,
        weight: e.weight
      }))
    };
    const res = await apiClient.post('/algorithms/shortest-path', {
      graph: graphData,
      source,
      target
    });
    return res.data;
  });
  return response.data;
};

export interface CandidateLinkItem {
  source: string;
  target: string;
  edge_id: string;
  source_type: string;
  target_type: string;
  delta_lcc_percent: number;
  delta_pairwise_percent: number;
  delta_critical_services: number;
  resulting_components: number;
  resulting_lcc_ratio: number;
  resulting_pairwise: number;
  bridges_eliminated: number;
  estimated_cost: number;
  benefit_score: number;
  cost_benefit_ratio: number;
  rationale: string;
  engineering_caveat: string;
}

export interface CandidateLinkEvaluationResponse {
  target_disrupted_edge: string;
  target_endpoints: string[];
  baseline_failure_metrics: {
    components: number;
    lcc_ratio: number;
    pairwise_connectivity: number;
    reachable_critical_services: number;
    total_critical_services: number;
  };
  total_candidates_evaluated: number;
  recommendations: CandidateLinkItem[];
  caveats: string[];
}

export const evaluateCandidateLinks = async (
  networkId: string,
  options?: {
    graph?: any;
    target_bridge_id?: string;
    target_failure_source?: string;
    target_failure_target?: string;
    max_recommendations?: number;
  }
): Promise<CandidateLinkEvaluationResponse> => {
  const response = await apiClient.post<CandidateLinkEvaluationResponse>(
    `/v1/networks/${networkId}/candidate-links`,
    options || {}
  );
  return response.data;
};
