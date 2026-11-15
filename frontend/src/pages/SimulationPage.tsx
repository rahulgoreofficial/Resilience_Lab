import React, { useState, useEffect, useRef } from 'react';
import { 
  PlayCircle, 
  RotateCcw, 
  AlertTriangle, 
  Activity, 
  ExternalLink
} from 'lucide-react';
import type { Network, NetworkTopologyResponse } from '../types/network';
import type { 
  SimulationResults, 
  SimulationEvent 
} from '../types/simulation';
import { SimulationForms } from '../components/simulation/SimulationForms';
import { SimulationResultsView } from '../components/simulation/SimulationResultsView';
import { CytoscapeGraph } from '../components/topology/CytoscapeGraph';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { 
  runNodeFailureSimulation, 
  runEdgeFailureSimulation, 
  runMultipleFailureSimulation, 
  runRandomFailureSimulation, 
  runTargetedFailureSimulation, 
  runCascadingFailureSimulation,
  getSimulationEvents
} from '../services/simulationService';

export interface SimulationPageProps {
  selectedNetwork: Network | null;
  topology: NetworkTopologyResponse | null;
  onNavigateToTopology: () => void;
  onSimulationCompleted?: (results: SimulationResults) => void;
  preselectedNodeId?: string | null;
}

export const SimulationPage: React.FC<SimulationPageProps> = ({
  selectedNetwork,
  topology,
  onNavigateToTopology,
  onSimulationCompleted,
  preselectedNodeId
}) => {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [events, setEvents] = useState<SimulationEvent[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // WebSocket Ref for real-time progress
  const wsRef = useRef<WebSocket | null>(null);

  const subscribeToSimulationWs = (simulationId: string) => {
    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsPort = window.location.port ? `:${window.location.port}` : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? ':8000' : '');
      const wsUrl = `${wsProtocol}//${window.location.hostname}${wsPort}/ws/simulations/${simulationId}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event) {
            setEvents((prev) => [...prev, data]);
          }
        } catch {
          // ignore parsing error
        }
      };

      ws.onerror = () => {
        // Fallback gracefully without throwing
      };
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleRunNodeFailure = async (failedNodeIds: string[]) => {
    if (!selectedNetwork) return;
    setIsRunning(true);
    setErrorMessage(null);
    setEvents([]);
    try {
      const res = await runNodeFailureSimulation(selectedNetwork.id, {
        failed_node_ids: failedNodeIds
      });
      setResults(res);
      onSimulationCompleted?.(res);
      if (res.simulation_id) {
        subscribeToSimulationWs(res.simulation_id);
        const evs = await getSimulationEvents(res.simulation_id).catch(() => []);
        if (evs.length > 0) setEvents(evs);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Node failure simulation failed.');
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    if (preselectedNodeId && selectedNetwork) {
      handleRunNodeFailure([preselectedNodeId]);
    }
  }, [preselectedNodeId, selectedNetwork?.id]);

  const handleRunEdgeFailure = async (failedEdges: Array<[string, string]>) => {
    if (!selectedNetwork) return;
    setIsRunning(true);
    setErrorMessage(null);
    setEvents([]);
    try {
      const res = await runEdgeFailureSimulation(selectedNetwork.id, {
        failed_edges: failedEdges
      });
      setResults(res);
      onSimulationCompleted?.(res);
      if (res.simulation_id) {
        subscribeToSimulationWs(res.simulation_id);
        const evs = await getSimulationEvents(res.simulation_id).catch(() => []);
        if (evs.length > 0) setEvents(evs);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Edge failure simulation failed.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunMultipleFailure = async (failedNodeIds: string[], failedEdges: Array<[string, string]>) => {
    if (!selectedNetwork) return;
    setIsRunning(true);
    setErrorMessage(null);
    setEvents([]);
    try {
      const res = await runMultipleFailureSimulation(selectedNetwork.id, {
        failed_node_ids: failedNodeIds,
        failed_edges: failedEdges
      });
      setResults(res);
      onSimulationCompleted?.(res);
      if (res.simulation_id) {
        subscribeToSimulationWs(res.simulation_id);
        const evs = await getSimulationEvents(res.simulation_id).catch(() => []);
        if (evs.length > 0) setEvents(evs);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Multiple failure simulation failed.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunRandomFailure = async (count: number, numTrials: number, seed: number) => {
    if (!selectedNetwork) return;
    setIsRunning(true);
    setErrorMessage(null);
    setEvents([]);
    try {
      const res = await runRandomFailureSimulation(selectedNetwork.id, {
        failure_target: 'nodes',
        failure_count: count,
        num_trials: numTrials,
        random_seed: seed
      });
      setResults(res);
      onSimulationCompleted?.(res);
      if (res.simulation_id) {
        subscribeToSimulationWs(res.simulation_id);
        const evs = await getSimulationEvents(res.simulation_id).catch(() => []);
        if (evs.length > 0) setEvents(evs);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Random failure simulation failed.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunTargetedFailure = async (
    strategy: 'degree' | 'articulation_points' | 'impact',
    count: number,
    adaptive: boolean
  ) => {
    if (!selectedNetwork) return;
    setIsRunning(true);
    setErrorMessage(null);
    setEvents([]);
    try {
      const res = await runTargetedFailureSimulation(selectedNetwork.id, {
        strategy,
        failure_count: count,
        adaptive
      });
      setResults(res);
      onSimulationCompleted?.(res);
      if (res.simulation_id) {
        subscribeToSimulationWs(res.simulation_id);
        const evs = await getSimulationEvents(res.simulation_id).catch(() => []);
        if (evs.length > 0) setEvents(evs);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Targeted failure simulation failed.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunCascadingFailure = async (
    initialFailedNodes: string[],
    overloadThreshold: number,
    maxRounds: number
  ) => {
    if (!selectedNetwork) return;
    setIsRunning(true);
    setErrorMessage(null);
    setEvents([]);
    try {
      const res = await runCascadingFailureSimulation(selectedNetwork.id, {
        initial_failed_nodes: initialFailedNodes,
        overload_threshold: overloadThreshold,
        max_simulation_rounds: maxRounds
      });
      setResults(res);
      onSimulationCompleted?.(res);
      if (res.simulation_id) {
        subscribeToSimulationWs(res.simulation_id);
        const evs = await getSimulationEvents(res.simulation_id).catch(() => []);
        if (evs.length > 0) setEvents(evs);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Cascading failure simulation failed.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setEvents([]);
    setErrorMessage(null);
  };

  if (!selectedNetwork) {
    return (
      <div className="p-12 text-center bg-white/95 dark:bg-[#0D1220]/95 border border-slate-200/90 dark:border-[#253149] rounded-3xl shadow-xl max-w-4xl mx-auto my-12 text-[#171923] dark:text-[#F5F7FF]">
        <PlayCircle className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-[#171923] dark:text-[#F5F7FF]">No Active Network Selected</h3>
        <p className="text-sm text-[#737B8C] dark:text-[#929CB3] mt-1.5">Please select an infrastructure network to run failure simulations.</p>
      </div>
    );
  }

  const failedNodeIds = results?.failed_nodes || [];
  const failedEdgeIds = results?.failed_edges?.map((e) => (Array.isArray(e) ? `${e[0]}-${e[1]}` : e)) || [];

  return (
    <div className="space-y-6 pb-10">
      {/* ─── Premium Page Header ─── */}
      <div className="bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl p-5 shadow-xs flex flex-wrap items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-lg font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">Failure Simulation Laboratory</h2>
            <Badge variant="brand">Computational Solver</Badge>
          </div>
          <p className="text-xs text-[#737B8C] dark:text-[#929CB3] mt-0.5">
            Execute deterministic component failures, adversarial attacks and cascading overload propagation on <span className="font-semibold text-slate-900 dark:text-[#F5F7FF] font-mono-code">{selectedNetwork.name}</span>.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {results && (
            <Button
              variant="outline"
              size="sm"
              icon={<RotateCcw className="w-3.5 h-3.5" />}
              onClick={handleReset}
            >
              Reset Simulation
            </Button>
          )}
          <Button
            variant="dark"
            size="sm"
            icon={<ExternalLink className="w-3.5 h-3.5 text-[#22D3EE]" />}
            onClick={onNavigateToTopology}
          >
            Explore Full Topology
          </Button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 bg-rose-50/90 dark:bg-rose-950/30 border border-rose-200/90 dark:border-rose-500/40 rounded-2xl text-xs text-[#FF784F] dark:text-[#FF5364] flex items-center justify-between shadow-2xs transition-colors">
          <div className="flex items-center gap-2.5 font-medium">
            <AlertTriangle className="w-4 h-4 shrink-0 text-[#FF784F]" />
            <span>Simulation Execution Error: {errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="underline cursor-pointer font-semibold">Dismiss</button>
        </div>
      )}

      {/* ─── Two-Column Workspace (35% Left Config / 65% Right Network Canvas) ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Left Column: Simulation Configuration (approx 35% -> lg:col-span-5) */}
        <div className="lg:col-span-5 flex flex-col">
          <SimulationForms
            topology={topology}
            onRunNodeFailure={handleRunNodeFailure}
            onRunEdgeFailure={handleRunEdgeFailure}
            onRunMultipleFailure={handleRunMultipleFailure}
            onRunRandomFailure={handleRunRandomFailure}
            onRunTargetedFailure={handleRunTargetedFailure}
            onRunCascadingFailure={handleRunCascadingFailure}
            onReset={handleReset}
            isLoading={isRunning}
          />
        </div>

        {/* Right Column: Large Interactive Network Canvas (approx 65% -> lg:col-span-7) */}
        <div className="lg:col-span-7 flex flex-col">
          <div className="bg-gradient-to-br from-[#080B14] via-[#0D1220] to-[#121A2B] border border-slate-800 dark:border-[#253149] rounded-3xl overflow-hidden shadow-2xl flex-1 flex flex-col min-h-[580px] relative">
            <div className="px-5 py-3.5 border-b border-slate-800/80 bg-slate-900/60 flex items-center justify-between text-xs font-mono-code z-10 backdrop-blur-md">
              <span className="text-slate-300 font-semibold flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#22D3EE]" />
                Live Network State & Disruption Surface
              </span>
              <span className="text-[11px] text-slate-400">
                {failedNodeIds.length} failed · {topology?.elements.nodes.length || 0} total vertices
              </span>
            </div>

            {/* Canvas */}
            <div className="flex-1 w-full relative">
              <CytoscapeGraph
                topology={topology}
                layoutName="cose"
                failedNodeIds={failedNodeIds}
                failedEdgeIds={failedEdgeIds}
                className="w-full h-full"
              />

              {/* Floating Canvas Legend */}
              <div className="absolute bottom-3 left-3 bg-slate-900/85 backdrop-blur-md border border-slate-700/80 rounded-xl p-2.5 text-[10px] text-slate-300 font-mono-code shadow-md pointer-events-none z-10 flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#20D6A0] inline-block" />
                  <span>Healthy</span>
                </div>
                <div className="flex items-center gap-1.5 text-rose-400">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#FF5364] border border-dashed border-white inline-block" />
                  <span>Inactivated / Overloaded</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ─── Large Results Presentation Section (Below Workspace) ─── */}
      <div className="space-y-4 pt-2">
        <SimulationResultsView
          results={results}
          events={events}
          isLoading={isRunning}
        />
      </div>
    </div>
  );
};
