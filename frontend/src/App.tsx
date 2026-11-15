import React, { useState, useEffect, useCallback } from 'react';
import type { ActivePage } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { TopologyPage } from './pages/TopologyPage';
import { SimulationPage } from './pages/SimulationPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { HistoryPage } from './pages/HistoryPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { DesignStudioPage } from './pages/DesignStudioPage';
import { InteractiveGuide } from './interactive-guide/InteractiveGuide';
import { CreateNetworkModal } from './components/modals/CreateNetworkModal';
import { ImportNetworkModal } from './components/modals/ImportNetworkModal';
import { AddNodeModal } from './components/modals/AddNodeModal';
import { AddEdgeModal } from './components/modals/AddEdgeModal';
import { ReportModal } from './components/modals/ReportModal';

import type { Network, NetworkTopologyResponse, NetworkCreateInput, NodeCreateInput, EdgeCreateInput } from './types/network';
import type { ConnectivityAnalysis } from './types/analytics';
import type { SimulationRecord } from './types/simulation';
import type { SystemHealth, DatabaseHealth } from './types/api';

import { 
  listNetworks, 
  getNetworkTopology, 
  createNetwork, 
  importNetwork,
  addNode, 
  deleteNode, 
  addEdge, 
  deleteEdge 
} from './services/networkService';
import { analyzeNetwork, generateResilienceReport } from './services/analyticsService';
import { listSimulations } from './services/simulationService';
import { fetchHealth, fetchDatabaseHealth } from './services/api';

export const App: React.FC = () => {
  // Navigation & Page State (supports /interactive-guide route)
  const getInitialPage = (): ActivePage => {
    const path = window.location.pathname.toLowerCase();
    const hash = window.location.hash.toLowerCase();
    if (path.includes('interactive-guide') || hash.includes('interactive-guide') || hash.includes('guide')) {
      return 'guide';
    }
    return 'dashboard';
  };

  const [activePage, setActivePage] = useState<ActivePage>(getInitialPage);

  const handleNavigate = useCallback((page: ActivePage) => {
    setActivePage(page);
    setFocusedNodeId(null);
    if (page === 'guide') {
      window.history.pushState(null, '', '/interactive-guide');
    } else if (window.location.pathname.includes('interactive-guide')) {
      window.history.pushState(null, '', '/');
    }
  }, []);

  useEffect(() => {
    const onPopState = () => {
      const path = window.location.pathname.toLowerCase();
      if (path.includes('interactive-guide')) {
        setActivePage('guide');
      } else {
        setActivePage('dashboard');
      }
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  // Network State
  const [networks, setNetworks] = useState<Network[]>([]);
  const [selectedNetwork, setSelectedNetwork] = useState<Network | null>(null);
  const [topology, setTopology] = useState<NetworkTopologyResponse | null>(null);
  const [analysis, setAnalysis] = useState<ConnectivityAnalysis | null>(null);
  const [recentSimulations, setRecentSimulations] = useState<SimulationRecord[]>([]);

  // Health and System State
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [dbHealth, setDbHealth] = useState<DatabaseHealth | null>(null);

  // Cross-page navigation context state
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);
  const [preselectedSimNodeId, setPreselectedSimNodeId] = useState<string | null>(null);

  // Modals
  const [isCreateNetworkOpen, setIsCreateNetworkOpen] = useState(false);
  const [isImportNetworkOpen, setIsImportNetworkOpen] = useState(false);
  const [isAddNodeOpen, setIsAddNodeOpen] = useState(false);
  const [isAddEdgeOpen, setIsAddEdgeOpen] = useState(false);
  const [reportModal, setReportModal] = useState<{ isOpen: boolean; markdown: string; networkName: string }>({
    isOpen: false,
    markdown: '',
    networkName: ''
  });

  // Load networks list
  const loadNetworksList = useCallback(async () => {
    try {
      const res = await listNetworks(0, 100);
      setNetworks(res.items);
      if (res.items.length > 0 && !selectedNetwork) {
        setSelectedNetwork(res.items[0]);
      }
    } catch {
      // Handled gracefully
    }
  }, [selectedNetwork]);

  // Load network details: topology & analysis
  const loadNetworkDetails = useCallback(async (networkId: string) => {
    try {
      const [topo, an, sims] = await Promise.all([
        getNetworkTopology(networkId).catch(() => null),
        analyzeNetwork(networkId).catch(() => null),
        listSimulations(networkId, 0, 10).catch(() => ({ items: [] }))
      ]);
      setTopology(topo);
      setAnalysis(an);
      setRecentSimulations(sims.items);
    } catch {
      // Handled gracefully
    }
  }, []);

  // Initial App Mount: Health & Initial Network Fetch
  useEffect(() => {
    const initApp = async () => {
      try {
        const [h, db] = await Promise.all([
          fetchHealth().catch(() => null),
          fetchDatabaseHealth().catch(() => null),
        ]);
        setSystemHealth(h);
        setDbHealth(db);
        await loadNetworksList();
      } catch {
        // Handled via state
      }
    };
    initApp();
  }, [loadNetworksList]);

  // When selected network changes, load details
  useEffect(() => {
    if (selectedNetwork) {
      loadNetworkDetails(selectedNetwork.id);
    }
  }, [selectedNetwork?.id, loadNetworkDetails]);

  // Network Switch Handler
  const handleSelectNetwork = (net: Network) => {
    setSelectedNetwork(net);
    setFocusedNodeId(null);
  };

  // Create Network Handler
  const handleCreateNetwork = async (input: NetworkCreateInput) => {
    const newNet = await createNetwork(input);
    setNetworks((prev) => [newNet, ...prev]);
    setSelectedNetwork(newNet);
  };

  // Import Network Handler
  const handleImportNetwork = async (payload: { name: string; description?: string; network_type?: string; data: Record<string, unknown> }) => {
    const importedNet = await importNetwork(payload);
    setNetworks((prev) => [importedNet, ...prev]);
    setSelectedNetwork(importedNet);
    await loadNetworkDetails(importedNet.id);
  };

  // Node CRUD Handlers
  const handleAddNode = async (input: NodeCreateInput) => {
    if (!selectedNetwork) return;
    await addNode(selectedNetwork.id, input);
    await loadNetworkDetails(selectedNetwork.id);
  };

  const handleDeleteNode = async (nodeId: string) => {
    if (!selectedNetwork) return;
    await deleteNode(selectedNetwork.id, nodeId);
    await loadNetworkDetails(selectedNetwork.id);
  };

  // Edge CRUD Handlers
  const handleAddEdge = async (input: EdgeCreateInput) => {
    if (!selectedNetwork) return;
    await addEdge(selectedNetwork.id, input);
    await loadNetworkDetails(selectedNetwork.id);
  };

  const handleDeleteEdge = async (edgeId: string) => {
    if (!selectedNetwork) return;
    await deleteEdge(selectedNetwork.id, edgeId);
    await loadNetworkDetails(selectedNetwork.id);
  };

  // Cross-page navigation helpers
  const handleSelectNodeInTopology = (nodeId: string) => {
    setFocusedNodeId(nodeId);
    setActivePage('topology');
  };

  const handleSimulateNodeFromTopology = (nodeId: string) => {
    setPreselectedSimNodeId(nodeId);
    setActivePage('simulation');
  };

  const handleOpenGlobalReport = async () => {
    if (!selectedNetwork) return;
    try {
      const res = await generateResilienceReport(selectedNetwork.id);
      setReportModal({
        isOpen: true,
        markdown: res.markdown_report,
        networkName: selectedNetwork.name
      });
    } catch {
      alert('Unable to generate resilience audit report.');
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F8FC] dark:bg-[#080B14] text-[#171923] dark:text-[#F5F7FF] font-sans flex flex-col antialiased transition-colors duration-200">
      {/* Top Application Header */}
      <Header
        networks={networks}
        selectedNetwork={selectedNetwork}
        onSelectNetwork={handleSelectNetwork}
        onCreateNetworkClick={() => setIsCreateNetworkOpen(true)}
        onImportNetworkClick={() => setIsImportNetworkOpen(true)}
        onNavigateToGuide={() => handleNavigate('guide')}
        systemHealth={systemHealth}
        dbHealth={dbHealth}
      />

      {/* Main Full-Width Responsive Container */}
      <div className="flex-1 flex flex-col md:flex-row w-full px-4 sm:px-6 lg:px-8 xl:px-10 py-6 gap-6 min-w-0">
        {/* Left Navigation Sidebar */}
        <Sidebar
          activePage={activePage}
          onNavigate={handleNavigate}
          onOpenReport={handleOpenGlobalReport}
        />

        {/* Dynamic Center Page View */}
        <main className="flex-1 min-w-0">
          {activePage === 'dashboard' && (
            <DashboardPage
              selectedNetwork={selectedNetwork}
              analysis={analysis}
              recentSimulations={recentSimulations}
              onNavigateToTopology={() => setActivePage('topology')}
              onNavigateToSimulation={() => setActivePage('simulation')}
              onNavigateToAnalytics={() => setActivePage('analytics')}
              onCreateNetworkClick={() => setIsCreateNetworkOpen(true)}
              onImportNetworkClick={() => setIsImportNetworkOpen(true)}
              onSelectNodeInTopology={handleSelectNodeInTopology}
              onOpenReport={handleOpenGlobalReport}
            />
          )}

          {activePage === 'topology' && (
            <TopologyPage
              selectedNetwork={selectedNetwork}
              topology={topology}
              analysis={analysis}
              onRefreshTopology={() => selectedNetwork ? loadNetworkDetails(selectedNetwork.id) : Promise.resolve()}
              onSimulateNodeFailure={handleSimulateNodeFromTopology}
              onSimulateEdgeFailure={() => setActivePage('simulation')}
              onAddNodeClick={() => setIsAddNodeOpen(true)}
              onAddEdgeClick={() => setIsAddEdgeOpen(true)}
              onImportJsonClick={() => setIsImportNetworkOpen(true)}
              onDeleteNode={handleDeleteNode}
              onDeleteEdge={handleDeleteEdge}
              initialSelectedNodeId={focusedNodeId}
            />
          )}

          {activePage === 'simulation' && (
            <SimulationPage
              selectedNetwork={selectedNetwork}
              topology={topology}
              onNavigateToTopology={() => setActivePage('topology')}
              onSimulationCompleted={() => selectedNetwork && loadNetworkDetails(selectedNetwork.id)}
              preselectedNodeId={preselectedSimNodeId}
            />
          )}

          {activePage === 'analytics' && (
            <AnalyticsPage
              selectedNetwork={selectedNetwork}
              onOpenReportModal={(md, name) => setReportModal({ isOpen: true, markdown: md, networkName: name })}
              onSelectNodeInTopology={handleSelectNodeInTopology}
            />
          )}

          {activePage === 'history' && (
            <HistoryPage
              selectedNetwork={selectedNetwork}
              onNavigateToSimulation={() => setActivePage('simulation')}
            />
          )}

          {activePage === 'comparison' && (
            <ComparisonPage
              selectedNetwork={selectedNetwork}
              topology={topology}
            />
          )}

          {activePage === 'design-studio' && (
            <DesignStudioPage
              selectedNetwork={selectedNetwork}
              onSelectNetwork={setSelectedNetwork}
              onRefreshNetworks={loadNetworksList}
            />
          )}

          {activePage === 'guide' && (
            <InteractiveGuide
              onNavigateBack={() => handleNavigate('dashboard')}
            />
          )}
        </main>
      </div>

      {/* Global Modals */}
      <CreateNetworkModal
        isOpen={isCreateNetworkOpen}
        onClose={() => setIsCreateNetworkOpen(false)}
        onSubmit={handleCreateNetwork}
      />

      <ImportNetworkModal
        isOpen={isImportNetworkOpen}
        onClose={() => setIsImportNetworkOpen(false)}
        onImport={handleImportNetwork}
      />

      <AddNodeModal
        isOpen={isAddNodeOpen}
        onClose={() => setIsAddNodeOpen(false)}
        onSubmit={handleAddNode}
        existingNodeIds={topology?.elements.nodes.map((n) => n.data.id) || []}
      />

      <AddEdgeModal
        isOpen={isAddEdgeOpen}
        onClose={() => setIsAddEdgeOpen(false)}
        onSubmit={handleAddEdge}
        nodeIds={topology?.elements.nodes.map((n) => n.data.id) || []}
      />

      <ReportModal
        isOpen={reportModal.isOpen}
        onClose={() => setReportModal({ isOpen: false, markdown: '', networkName: '' })}
        reportMarkdown={reportModal.markdown}
        networkName={reportModal.networkName}
      />
    </div>
  );
};

export default App;
