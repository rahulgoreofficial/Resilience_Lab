/**
 * Guide Constants - Shared chapter definitions, glossary, quiz data.
 */

import type { GuideChapter, GlossaryItem, QuizQuestion, PresentationStep } from './guideTypes';

export const CHAPTERS: GuideChapter[] = [
  { id: 1, title: 'Understanding a Network',      subtitle: 'What are nodes and what do they do?',            icon: '🌐', color: '#2563EB' },
  { id: 2, title: 'Understanding Connections',    subtitle: 'Edges, paths, and the graph G = (V, E)',         icon: '🔗', color: '#7C3AED' },
  { id: 3, title: 'Finding Critical Components',  subtitle: 'Articulation points and bridges',                icon: '⚠️', color: '#D97706' },
  { id: 4, title: 'Simulating Network Failures',  subtitle: 'What happens when something breaks?',            icon: '💥', color: '#DC2626' },
  { id: 5, title: 'Cascading Failures',           subtitle: 'How one failure can cause more failures',        icon: '🌊', color: '#9333EA' },
  { id: 6, title: 'Improving Resilience',         subtitle: 'Adding backup paths to protect the network',     icon: '🛡️', color: '#059669' },
];

export const CHAPTER_GLOSSARIES: Record<number, GlossaryItem[]> = {
  1: [
    { term: 'Node', simple: 'A device in the network (like a router or server).', technical: 'A vertex in graph G = (V, E) representing a network entity.' },
    { term: 'Router', simple: 'Directs traffic, like a traffic officer at a junction.', technical: 'A layer-3 device that forwards packets between networks.' },
    { term: 'Server', simple: 'A computer that provides a service to others.', technical: 'A host providing application or data services to clients.' },
    { term: 'Firewall', simple: 'A security guard that blocks unwanted visitors.', technical: 'A network security device that monitors and controls incoming/outgoing traffic.' },
  ],
  2: [
    { term: 'Edge', simple: 'A cable or wireless connection between two devices.', technical: 'A pair (u, v) ∈ E in graph G = (V, E) representing a link.' },
    { term: 'Degree', simple: 'How many connections a device has.', technical: 'The number of edges incident to a vertex: deg(v) = |N(v)|.' },
    { term: 'Graph', simple: 'A diagram of dots (devices) connected by lines (cables).', technical: 'G = (V, E) where V is the set of vertices and E ⊆ V × V is the edge set.' },
    { term: 'Adjacency', simple: 'Two devices that are directly connected.', technical: 'Two vertices u, v are adjacent if (u,v) ∈ E.' },
  ],
  3: [
    { term: 'Articulation Point', simple: 'A device whose failure splits the network into disconnected parts.', technical: 'A vertex v in a connected graph G where G − {v} has more connected components than G.' },
    { term: 'Bridge', simple: 'A connection whose removal splits the network into disconnected parts.', technical: 'An edge e in a connected graph G where G − {e} is disconnected.' },
    { term: 'Connected Component', simple: 'A group of devices that can still talk to each other.', technical: 'A maximal subgraph in which any two vertices are connected by paths.' },
    { term: 'Cut Vertex', simple: 'Same as articulation point — removing it breaks the network.', technical: 'A vertex whose removal increases the number of connected components.' },
  ],
  4: [
    { term: 'Node Failure', simple: 'A device stops working and gets removed from the network.', technical: 'Deletion of vertex v from G, yielding subgraph G − {v}.' },
    { term: 'Isolated Node', simple: 'A device that has no working connections left.', technical: 'A vertex with degree 0 after failure propagation.' },
    { term: 'Service Resilience', simple: 'The percentage of critical services still reachable.', technical: 'Ratio of reachable critical services to total critical services post-failure.' },
    { term: 'LCC', simple: 'The largest group still connected after a failure.', technical: 'Largest Connected Component — the largest maximal subgraph that remains connected.' },
  ],
  5: [
    { term: 'Cascading Failure', simple: 'When one failure causes other devices to overload and also fail.', technical: 'A sequential failure process where each round redistributes load and triggers new failures.' },
    { term: 'Overload', simple: 'A device gets too much traffic and shuts down.', technical: 'A node or edge state where current_load > capacity × threshold.' },
    { term: 'Propagation', simple: 'The spread of failures through the network.', technical: 'The sequential triggering of additional failures across rounds of simulation.' },
  ],
  6: [
    { term: 'Redundancy', simple: 'Having a backup connection so failure of one path does not disconnect the network.', technical: 'Edge-disjoint or vertex-disjoint paths providing alternative routes.' },
    { term: 'Resilience', simple: 'How well a network survives failures.', technical: 'Quantified by LCC ratio, pairwise connectivity, and service reachability post-failure.' },
    { term: 'Alternative Path', simple: 'A different route traffic can take if one route breaks.', technical: 'A path in G not using the failed element — found by re-running BFS/Dijkstra.' },
  ],
};

export const CHAPTER_QUIZZES: Record<number, QuizQuestion> = {
  1: {
    question: 'What does a router do in a computer network?',
    options: [
      'Stores your files permanently',
      'Directs network traffic between different parts of the network',
      'Provides electricity to other devices',
      'Connects only two computers together',
    ],
    correctIndex: 1,
    explanation: 'A router is like a traffic officer — it decides which direction data packets should travel to reach their destination.',
  },
  2: {
    question: 'In the graph G = (V, E), what does E represent?',
    options: [
      'The set of all network devices (nodes)',
      'The energy consumed by the network',
      'The set of all connections (edges) between devices',
      'The efficiency rating of the network',
    ],
    correctIndex: 2,
    explanation: 'E is the edge set — it contains all the connections (links) between pairs of network devices.',
  },
  3: {
    question: 'What happens when an articulation point is removed from a network?',
    options: [
      'The network becomes stronger',
      'Nothing changes — all devices stay connected',
      'The network splits into disconnected groups that cannot communicate',
      'All routers automatically restart',
    ],
    correctIndex: 2,
    explanation: 'An articulation point is a single device whose removal disconnects the network. This is why identifying and protecting them is critical.',
  },
  4: {
    question: 'When a node fails, which nodes are most affected?',
    options: [
      'Nodes far away from the failed device',
      'Nodes that were only connected through the failed device',
      'Nodes with the highest capacity',
      'Nodes that were already offline',
    ],
    correctIndex: 1,
    explanation: 'Nodes that depended on the failed device as their only path are immediately disconnected and cannot communicate with the rest of the network.',
  },
  5: {
    question: 'What causes a cascading failure?',
    options: [
      'A power surge that destroys all devices simultaneously',
      'One failure causes other devices to become overloaded, triggering further failures',
      'A software update applied to all devices at once',
      'Heavy rain damaging the network cables',
    ],
    correctIndex: 1,
    explanation: 'In a cascade, the initial failure causes traffic to reroute. If the remaining devices cannot handle the extra load, they too fail — spreading the failure further.',
  },
  6: {
    question: 'How does adding a backup connection improve network resilience?',
    options: [
      'It makes all devices faster',
      'It provides an alternative path so the network stays connected even if one link fails',
      'It prevents all future hardware failures',
      'It reduces the number of nodes in the network',
    ],
    correctIndex: 1,
    explanation: 'A backup connection gives traffic an alternative route. Even if the primary link fails, data can still flow through the backup path, keeping the network connected.',
  },
};

export const PRESENTATION_STEPS: PresentationStep[] = [
  { 
    id: 1,  
    title: '1. Campus Network Introduction', 
    caption: 'We model a 12-node College Campus IT Network connecting the Internet Gateway (G1), Edge Router, Core Switch, Academic Labs, Library, Administration, and Data Center.', 
    chapter: 1, 
    autoAction: 'none' 
  },
  { 
    id: 2,  
    title: '2. Network Topology Analysis', 
    caption: 'Mathematically formulated as an attributed graph G = (V, E) with |V| = 12 nodes and |E| = 11 edges. Because |E| = |V| - 1 and it is connected, the baseline topology is a tree.', 
    chapter: 2, 
    autoAction: 'none' 
  },
  { 
    id: 3,  
    title: '3. Critical Bridge Identification', 
    caption: 'Tarjan\'s linear-time DFS reveals that all 11 edges are bridges. The C1-L1 link connecting the Core Switch to the Academic Laboratory is a critical single point of failure.', 
    chapter: 3, 
    autoAction: 'show_bridges' 
  },
  { 
    id: 4,  
    title: '4. Communication-Link Failure', 
    caption: 'Simulating physical severance of link C1-L1. The graph immediately partitions into two disconnected components: {L1, LS1} (size 2) and the rest of campus (size 10).', 
    chapter: 4, 
    autoAction: 'none' 
  },
  { 
    id: 5,  
    title: '5. Affected Service Analysis', 
    caption: 'Critical Laboratory Server LS1 is isolated from Gateway G1. Giant component drops to 83.33%, Pairwise connectivity drops to 69.70%, and service reachability drops to 75%.', 
    chapter: 4, 
    autoAction: 'show_components' 
  },
  { 
    id: 6,  
    title: '6. Backup-Link Creation', 
    caption: 'Infrastructure Hardening: Adding candidate redundant link L1-B1 creates a 3-cycle C1-L1-B1-C1, eliminating the bridge vulnerability and establishing 2-edge-connectivity.', 
    chapter: 6, 
    autoAction: 'none' 
  },
  { 
    id: 7,  
    title: '7. Repeated Failure Under Hardening', 
    caption: 'Simulating the identical C1-L1 severance on the improved network. The network remains 100% connected, and all 4 critical services remain fully accessible.', 
    chapter: 6, 
    autoAction: 'none' 
  },
  { 
    id: 8,  
    title: '8. Before/After Mathematical Comparison', 
    caption: 'Original vs Hardened comparison proves 100% LCC retention. Traffic dynamically reroutes via alternative path: G1 → R1 → C1 → B1 → L1 → LS1.', 
    chapter: 6, 
    autoAction: 'none' 
  },
  { 
    id: 9,  
    title: '9. Cascading Failure Demonstration', 
    caption: 'Controlled overload scenario: failing Primary Router PR1 shifts 300 client traffic onto Backup Router BR1, exceeding its 350 capacity and triggering cascade collapse.', 
    chapter: 5, 
    autoAction: 'none' 
  },
  { 
    id: 10, 
    title: '10. Mathematical Conclusion', 
    caption: 'Discrete Mathematics provides formal proofs of resilience. Graph theory transforms subjective network cabling into verifiable engineering equations.', 
    chapter: 6, 
    autoAction: 'none' 
  },
];

