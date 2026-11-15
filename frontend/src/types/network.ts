/**
 * Network Infrastructure & Cytoscape Data Types.
 */

export type NodeType = 'router' | 'switch' | 'server' | 'database' | 'firewall' | 'gateway';

export interface NodeModel {
  id?: number;
  network_id?: string;
  node_id: string;
  node_type: NodeType;
  importance: number;
  capacity: number;
  current_load: number;
  failure_probability: number;
  is_critical: boolean;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface EdgeModel {
  id?: number;
  network_id?: string;
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  weight: number;
  latency: number;
  capacity: number;
  reliability: number;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface Network {
  id: string;
  name: string;
  description?: string;
  network_type: string;
  version: number;
  node_count: number;
  edge_count: number;
  created_at: string;
  updated_at: string;
}

export interface CytoscapeNodeData {
  id: string;
  label: string;
  node_type: NodeType;
  importance: number;
  capacity: number;
  current_load: number;
  failure_probability: number;
  is_critical: boolean;
  status?: 'healthy' | 'critical' | 'failed' | 'disconnected' | 'selected';
  metadata?: Record<string, unknown>;
}

export interface CytoscapeEdgeData {
  id: string;
  source: string;
  target: string;
  weight: number;
  latency: number;
  capacity: number;
  reliability: number;
  status?: 'healthy' | 'bridge' | 'failed' | 'active_path';
  metadata?: Record<string, unknown>;
}

export interface CytoscapeElement {
  data: CytoscapeNodeData | CytoscapeEdgeData;
  classes?: string;
}

export interface NetworkTopologyResponse {
  network_id: string;
  name: string;
  version: number;
  elements: {
    nodes: Array<{ data: CytoscapeNodeData }>;
    edges: Array<{ data: CytoscapeEdgeData }>;
  };
  nodes: NodeModel[];
  edges: EdgeModel[];
}

export interface NetworkCreateInput {
  name: string;
  description?: string;
  network_type?: string;
  metadata?: Record<string, unknown>;
}

export interface NetworkUpdateInput {
  name?: string;
  description?: string;
  expected_version: number;
}

export interface NodeCreateInput {
  node_id: string;
  node_type: NodeType;
  importance?: number;
  capacity?: number;
  current_load?: number;
  failure_probability?: number;
  is_critical?: boolean;
  metadata?: Record<string, unknown>;
}

export interface EdgeCreateInput {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  weight?: number;
  latency?: number;
  capacity?: number;
  reliability?: number;
  metadata?: Record<string, unknown>;
}

