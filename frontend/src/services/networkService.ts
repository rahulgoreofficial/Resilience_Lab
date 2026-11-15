import { apiClient } from './api';
import type { 
  Network, 
  NetworkTopologyResponse, 
  NetworkCreateInput, 
  NetworkUpdateInput,
  NodeModel,
  NodeCreateInput,
  EdgeModel,
  EdgeCreateInput
} from '../types/network';
import type { PaginatedResponse } from '../types/api';

export const listNetworks = async (skip = 0, limit = 50): Promise<PaginatedResponse<Network>> => {
  const response = await apiClient.get<PaginatedResponse<Network>>('/v1/networks', {
    params: { skip, limit }
  });
  return response.data;
};

export const getNetwork = async (networkId: string): Promise<Network> => {
  const response = await apiClient.get<Network>(`/v1/networks/${networkId}`);
  return response.data;
};

export const createNetwork = async (payload: NetworkCreateInput): Promise<Network> => {
  const response = await apiClient.post<Network>('/v1/networks', payload);
  return response.data;
};

export const updateNetwork = async (networkId: string, payload: NetworkUpdateInput): Promise<Network> => {
  const response = await apiClient.put<Network>(`/v1/networks/${networkId}`, payload);
  return response.data;
};

export const deleteNetwork = async (networkId: string): Promise<void> => {
  await apiClient.delete(`/v1/networks/${networkId}`);
};

export const getNetworkTopology = async (networkId: string): Promise<NetworkTopologyResponse> => {
  const response = await apiClient.get<NetworkTopologyResponse>(`/v1/networks/${networkId}/topology`);
  return response.data;
};

export const exportNetwork = async (networkId: string): Promise<Record<string, unknown>> => {
  const response = await apiClient.get<Record<string, unknown>>(`/v1/networks/${networkId}/export`);
  return response.data;
};

export const importNetwork = async (payload: { name: string; description?: string; data: Record<string, unknown> }): Promise<Network> => {
  const response = await apiClient.post<Network>('/v1/networks/import', payload);
  return response.data;
};

// Node operations
export const listNodes = async (networkId: string): Promise<NodeModel[]> => {
  const response = await apiClient.get<NodeModel[]>(`/v1/networks/${networkId}/nodes`);
  return response.data;
};

export const addNode = async (networkId: string, payload: NodeCreateInput): Promise<NodeModel> => {
  const response = await apiClient.post<NodeModel>(`/v1/networks/${networkId}/nodes`, payload);
  return response.data;
};

export const deleteNode = async (networkId: string, nodeId: string): Promise<void> => {
  await apiClient.delete(`/v1/networks/${networkId}/nodes/${nodeId}`);
};

// Edge operations
export const listEdges = async (networkId: string): Promise<EdgeModel[]> => {
  const response = await apiClient.get<EdgeModel[]>(`/v1/networks/${networkId}/edges`);
  return response.data;
};

export const addEdge = async (networkId: string, payload: EdgeCreateInput): Promise<EdgeModel> => {
  const response = await apiClient.post<EdgeModel>(`/v1/networks/${networkId}/edges`, payload);
  return response.data;
};

export const deleteEdge = async (networkId: string, edgeId: string): Promise<void> => {
  await apiClient.delete(`/v1/networks/${networkId}/edges/${edgeId}`);
};

