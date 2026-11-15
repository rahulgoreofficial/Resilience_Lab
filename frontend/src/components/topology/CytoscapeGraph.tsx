import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import type {
  NetworkTopologyResponse,
  CytoscapeNodeData,
  CytoscapeEdgeData
} from '../../types/network';

export interface CytoscapeGraphProps {
  topology: NetworkTopologyResponse | null;
  layoutName?: 'cose' | 'concentric' | 'circle' | 'breadthfirst' | 'grid';
  selectedNodeId?: string | null;
  selectedEdgeId?: string | null;
  onSelectNode?: (nodeData: CytoscapeNodeData | null) => void;
  onSelectEdge?: (edgeData: CytoscapeEdgeData | null) => void;
  highlightedPath?: string[];
  failedNodeIds?: string[];
  failedEdgeIds?: string[];
  articulationPoints?: string[];
  bridgeEdgeIds?: string[];
  className?: string;
}

export const CytoscapeGraph: React.FC<CytoscapeGraphProps> = ({
  topology,
  layoutName = 'cose',
  selectedNodeId,
  selectedEdgeId,
  onSelectNode,
  onSelectEdge,
  highlightedPath = [],
  failedNodeIds = [],
  failedEdgeIds = [],
  articulationPoints = [],
  bridgeEdgeIds = [],
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || !topology) return;

    const elements: cytoscape.ElementDefinition[] = [];

    // Process nodes
    topology.elements.nodes.forEach((n) => {
      const data = n.data;
      const isFailed = failedNodeIds.includes(data.id);
      const isAP = articulationPoints.includes(data.id);
      const isSelected = selectedNodeId === data.id;
      const inPath = highlightedPath.includes(data.id);

      const classes: string[] = [data.node_type || 'server'];
      if (isFailed) classes.push('failed');
      else if (isAP) classes.push('articulation_point');
      if (isSelected) classes.push('selected');
      if (inPath) classes.push('path_highlight');

      elements.push({
        group: 'nodes',
        data: {
          id: data.id,
          label: data.label || data.id,
          node_type: data.node_type || 'server',
          importance: data.importance,
          capacity: data.capacity,
          current_load: data.current_load,
          failure_probability: data.failure_probability,
          is_critical: data.is_critical,
          raw: data
        },
        classes: classes.join(' ')
      });
    });

    // Process edges
    topology.elements.edges.forEach((e) => {
      const data = e.data;
      const isFailed = failedEdgeIds.includes(data.id);
      const isBridge = bridgeEdgeIds.includes(data.id);
      const isSelected = selectedEdgeId === data.id;

      let inPath = false;
      if (highlightedPath.length >= 2) {
        for (let i = 0; i < highlightedPath.length - 1; i++) {
          const u = highlightedPath[i];
          const v = highlightedPath[i + 1];
          if (
            (data.source === u && data.target === v) ||
            (data.source === v && data.target === u)
          ) {
            inPath = true;
            break;
          }
        }
      }

      const classes: string[] = [];
      if (isFailed) classes.push('edge_failed');
      else if (isBridge) classes.push('edge_bridge');
      if (isSelected) classes.push('edge_selected');
      if (inPath) classes.push('edge_path');

      elements.push({
        group: 'edges',
        data: {
          id: data.id,
          source: data.source,
          target: data.target,
          weight: data.weight,
          latency: data.latency,
          capacity: data.capacity,
          reliability: data.reliability,
          raw: data
        },
        classes: classes.join(' ')
      });
    });

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        // Base Node Style
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#E2E8F0',
            'font-size': '12px',
            'font-family': '"JetBrains Mono", Menlo, monospace',
            'font-weight': 'bold',
            'text-valign': 'bottom',
            'text-margin-y': 7,
            'background-color': '#080E1C',
            'border-width': 2.5,
            'border-color': '#475569',
            'width': 38,
            'height': 38,
            'transition-property': 'background-color, border-color, width, height, underlay-color, underlay-opacity',
            'transition-duration': 0.2
          }
        },
        // Component Archetypes
        {
          selector: 'node.router',
          style: {
            'shape': 'hexagon',
            'border-color': '#3B82F6',
            'border-width': 3
          }
        },
        {
          selector: 'node.switch',
          style: {
            'shape': 'round-rectangle',
            'border-color': '#22D3EE',
            'border-width': 2.5
          }
        },
        {
          selector: 'node.server',
          style: {
            'shape': 'ellipse',
            'border-color': '#10B981',
            'border-width': 2.5
          }
        },
        {
          selector: 'node.database',
          style: {
            'shape': 'barrel',
            'border-color': '#A855F7',
            'border-width': 2.5
          }
        },
        {
          selector: 'node.firewall',
          style: {
            'shape': 'diamond',
            'border-color': '#F59E0B',
            'border-width': 2.5
          }
        },
        {
          selector: 'node.gateway',
          style: {
            'shape': 'octagon',
            'border-color': '#F2653A',
            'border-width': 3.5,
            'width': 44,
            'height': 44
          }
        },
        // States
        {
          selector: 'node.articulation_point',
          style: {
            'border-color': '#F2653A',
            'border-width': 4,
            'underlay-color': '#F2653A',
            'underlay-padding': 6,
            'underlay-opacity': 0.35
          }
        },
        {
          selector: 'node.failed',
          style: {
            'background-color': '#450A0A',
            'border-color': '#EF4444',
            'border-width': 3.5,
            'border-style': 'dashed',
            'opacity': 0.55
          }
        },
        {
          selector: 'node.selected',
          style: {
            'border-color': '#FFFFFF',
            'border-width': 4,
            'underlay-color': '#22D3EE',
            'underlay-padding': 8,
            'underlay-opacity': 0.45,
            'width': 46,
            'height': 46
          }
        },
        {
          selector: 'node.path_highlight',
          style: {
            'border-color': '#22D3EE',
            'border-width': 4,
            'underlay-color': '#22D3EE',
            'underlay-padding': 6,
            'underlay-opacity': 0.4
          }
        },
        // Base Edge Style
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#334155',
            'curve-style': 'bezier',
            'opacity': 0.85,
            'transition-property': 'line-color, width, opacity',
            'transition-duration': 0.2
          }
        },
        {
          selector: 'edge.edge_bridge',
          style: {
            'line-color': '#F2653A',
            'line-style': 'dashed',
            'width': 3,
            'opacity': 0.95
          }
        },
        {
          selector: 'edge.edge_failed',
          style: {
            'line-color': '#EF4444',
            'line-style': 'dashed',
            'width': 2.5,
            'opacity': 0.35
          }
        },
        {
          selector: 'edge.edge_selected',
          style: {
            'line-color': '#FFFFFF',
            'width': 4,
            'opacity': 1
          }
        },
        {
          selector: 'edge.edge_path',
          style: {
            'line-color': '#22D3EE',
            'width': 4,
            'opacity': 1
          }
        }
      ],
      layout: {
        name: layoutName,
        animate: true,
        animationDuration: 400,
        padding: 50,
        ...(layoutName === 'cose' ? {
          nodeRepulsion: () => 6500,
          idealEdgeLength: () => 110,
          gravity: 0.25,
          numIter: 400
        } : {})
      }
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      onSelectNode?.(node.data('raw'));
    });

    cy.on('tap', 'edge', (evt) => {
      const edge = evt.target;
      onSelectEdge?.(edge.data('raw'));
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        onSelectNode?.(null);
        onSelectEdge?.(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [
    topology,
    layoutName,
    selectedNodeId,
    selectedEdgeId,
    highlightedPath,
    failedNodeIds,
    failedEdgeIds,
    articulationPoints,
    bridgeEdgeIds
  ]);

  return (
    <div className={`relative w-full h-full bg-tech-grid ${className}`}>
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
    </div>
  );
};
