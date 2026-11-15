import { apiClient } from './api';
import type {
  SimulationRecord,
  SimulationEvent,
  SimulationResults,
  NodeFailurePayload,
  EdgeFailurePayload,
  MultipleFailurePayload,
  RandomFailurePayload,
  TargetedFailurePayload,
  CascadingFailurePayload
} from '../types/simulation';
import type { PaginatedResponse } from '../types/api';

export const runNodeFailureSimulation = async (
  networkId: string,
  payload: NodeFailurePayload
): Promise<SimulationResults> => {
  const response = await apiClient.post<SimulationResults>(
    '/v1/simulations/node-failure',
    payload,
    { params: { network_id: networkId } }
  );
  return response.data;
};

export const runEdgeFailureSimulation = async (
  networkId: string,
  payload: EdgeFailurePayload
): Promise<SimulationResults> => {
  const response = await apiClient.post<SimulationResults>(
    '/v1/simulations/edge-failure',
    payload,
    { params: { network_id: networkId } }
  );
  return response.data;
};

export const runMultipleFailureSimulation = async (
  networkId: string,
  payload: MultipleFailurePayload
): Promise<SimulationResults> => {
  const response = await apiClient.post<SimulationResults>(
    '/v1/simulations/multiple-failure',
    payload,
    { params: { network_id: networkId } }
  );
  return response.data;
};

export const runRandomFailureSimulation = async (
  networkId: string,
  payload: RandomFailurePayload
): Promise<SimulationResults> => {
  const response = await apiClient.post<SimulationResults>(
    '/v1/simulations/random',
    payload,
    { params: { network_id: networkId } }
  );
  return response.data;
};

export const runTargetedFailureSimulation = async (
  networkId: string,
  payload: TargetedFailurePayload
): Promise<SimulationResults> => {
  const response = await apiClient.post<SimulationResults>(
    '/v1/simulations/targeted',
    payload,
    { params: { network_id: networkId } }
  );
  return response.data;
};

export const runCascadingFailureSimulation = async (
  networkId: string,
  payload: CascadingFailurePayload
): Promise<SimulationResults> => {
  const response = await apiClient.post<SimulationResults>(
    '/v1/simulations/cascading',
    payload,
    { params: { network_id: networkId } }
  );
  return response.data;
};

export const listSimulations = async (
  networkId?: string,
  skip = 0,
  limit = 50
): Promise<PaginatedResponse<SimulationRecord>> => {
  const params: Record<string, unknown> = { skip, limit };
  if (networkId) params.network_id = networkId;
  const response = await apiClient.get<PaginatedResponse<SimulationRecord>>('/v1/simulations', { params });
  return response.data;
};

export const getSimulation = async (simulationId: string): Promise<SimulationRecord> => {
  const response = await apiClient.get<SimulationRecord>(`/v1/simulations/${simulationId}`);
  return response.data;
};

export const getSimulationEvents = async (simulationId: string): Promise<SimulationEvent[]> => {
  const response = await apiClient.get<SimulationEvent[]>(`/v1/simulations/${simulationId}/events`);
  return response.data;
};

