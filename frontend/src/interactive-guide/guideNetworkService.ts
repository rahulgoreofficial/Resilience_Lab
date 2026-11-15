/**
 * Guide Network Data Service
 * Loads or creates the guide's demo networks and calls real backend APIs.
 * Supports the Campus IT Infrastructure demonstration and Cascading Failure scenario.
 */

import { apiClient } from '../services/api';
import type { NetworkTopologyResponse } from '../types/network';
import type { ConnectivityAnalysis, NodeCriticalityItem } from '../types/analytics';
import type { SimulationResults } from '../types/simulation';
import type { CandidateLinkEvaluationResponse } from '../services/analyticsService';

export interface GuideNetworkInfo {
  networkId: string;
  name: string;
  topology: NetworkTopologyResponse;
  analysis: ConnectivityAnalysis;
}

/**
 * Loads or initializes the official 12-node Campus IT Infrastructure demonstration network.
 */
export async function ensureCampusNetwork(reset = false): Promise<GuideNetworkInfo> {
  const res = await apiClient.get<any>('/v1/networks/demonstrations/campus', {
    params: { reset }
  });
  const networkId: string = res.data.id;
  const name: string = res.data.name;

  const [topo, analysis] = await Promise.all([
    apiClient.get<NetworkTopologyResponse>(`/v1/networks/${networkId}/topology`),
    apiClient.get<ConnectivityAnalysis>(`/v1/networks/${networkId}/analysis`, {
      params: {
        entry_points: ['G1'],
        critical_services: ['LS1', 'LS2', 'AS1', 'LMS']
      }
    }),
  ]);

  return { networkId, name, topology: topo.data, analysis: analysis.data };
}

/**
 * Loads or initializes the 5-node Controlled Cascading Failure demonstration network.
 */
export async function ensureCascadingNetwork(reset = false): Promise<GuideNetworkInfo> {
  const res = await apiClient.get<any>('/v1/networks/demonstrations/cascading', {
    params: { reset }
  });
  const networkId: string = res.data.id;
  const name: string = res.data.name;

  const [topo, analysis] = await Promise.all([
    apiClient.get<NetworkTopologyResponse>(`/v1/networks/${networkId}/topology`),
    apiClient.get<ConnectivityAnalysis>(`/v1/networks/${networkId}/analysis`),
  ]);

  return { networkId, name, topology: topo.data, analysis: analysis.data };
}

/**
 * Returns an existing guide network or creates a new one.
 */
export async function ensureGuideNetwork(): Promise<GuideNetworkInfo> {
  // Default to campus demonstration network
  return ensureCampusNetwork(false);
}

export async function getTopology(networkId: string): Promise<NetworkTopologyResponse> {
  const res = await apiClient.get<NetworkTopologyResponse>(`/v1/networks/${networkId}/topology`);
  return res.data;
}

export async function getAnalysis(networkId: string, entryPoints?: string[], criticalServices?: string[]): Promise<ConnectivityAnalysis> {
  const res = await apiClient.get<ConnectivityAnalysis>(`/v1/networks/${networkId}/analysis`, {
    params: {
      entry_points: entryPoints,
      critical_services: criticalServices
    }
  });
  return res.data;
}

export async function getNodeCriticality(networkId: string): Promise<NodeCriticalityItem[]> {
  const res = await apiClient.get<{ top_nodes: NodeCriticalityItem[] } | NodeCriticalityItem[]>(
    `/v1/networks/${networkId}/criticality`,
    { params: { target: 'nodes' } }
  );
  if (Array.isArray(res.data)) return res.data;
  if (res.data && Array.isArray((res.data as { top_nodes: NodeCriticalityItem[] }).top_nodes)) {
    return (res.data as { top_nodes: NodeCriticalityItem[] }).top_nodes;
  }
  return [];
}

export async function runNodeFailure(
  networkId: string,
  failedNodeIds: string[],
  criticalServices?: string[]
): Promise<SimulationResults> {
  const payload = { failed_node_ids: failedNodeIds, critical_services: criticalServices };
  const res = await apiClient.post<SimulationResults>(
    '/v1/simulations/node-failure',
    payload,
    { params: { network_id: networkId } }
  );
  return res.data;
}

export async function runEdgeFailure(
  networkId: string,
  failedEdges: any[],
  entryPoints?: string[],
  criticalServices?: string[]
): Promise<SimulationResults> {
  const payload = {
    failed_edges: failedEdges,
    entry_points: entryPoints,
    critical_services: criticalServices
  };
  const res = await apiClient.post<SimulationResults>(
    '/v1/simulations/edge-failure',
    payload,
    { params: { network_id: networkId } }
  );
  return res.data;
}

export async function runCascadingFailure(
  networkId: string,
  initialFailedNodes: string[],
  overloadThreshold = 1.0,
  maxRounds = 6,
  trafficDemands?: any[]
): Promise<SimulationResults> {
  const payload = {
    initial_failed_nodes: initialFailedNodes,
    overload_threshold: overloadThreshold,
    max_simulation_rounds: maxRounds,
    traffic_demands: trafficDemands || [{ source: 'CL1', target: 'SRV_APP', demand: 300.0 }]
  };
  const res = await apiClient.post<SimulationResults>(
    '/v1/simulations/cascading',
    payload,
    { params: { network_id: networkId } }
  );
  return res.data;
}

export async function addBackupEdge(
  networkId: string,
  edgeId: string,
  sourceId: string,
  targetId: string,
  label = 'Backup Redundant Trunk'
): Promise<void> {
  await apiClient.post(`/v1/networks/${networkId}/edges`, {
    edge_id: edgeId,
    source_node_id: sourceId,
    target_node_id: targetId,
    weight: 1.0,
    latency: 3.5,
    capacity: 500,
    reliability: 0.99,
    metadata: { label, backup: true }
  });
}

export async function deleteEdge(networkId: string, edgeId: string): Promise<void> {
  await apiClient.delete(`/v1/networks/${networkId}/edges/${edgeId}`);
}

export async function fetchCandidateLinks(
  networkId: string,
  targetBridgeId?: string,
  targetSource?: string,
  targetDest?: string
): Promise<CandidateLinkEvaluationResponse> {
  const res = await apiClient.post<CandidateLinkEvaluationResponse>(
    `/v1/networks/${networkId}/candidate-links`,
    {
      target_bridge_id: targetBridgeId,
      target_failure_source: targetSource,
      target_failure_target: targetDest,
      entry_points: ['G1'],
      critical_services: ['LS1', 'LS2', 'AS1', 'LMS'],
      max_recommendations: 10
    }
  );
  return res.data;
}
