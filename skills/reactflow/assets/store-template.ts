// assets/store-template.ts
// Complete Zustand flow store for enterprise SaaS
// Stack: @xyflow/react v12 + zustand + zundo (undo/redo)
//
// Install: npm install @xyflow/react zustand zundo nanoid

import { create } from 'zustand';
import { temporal } from 'zundo';
import { shallow } from 'zustand/shallow';
import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type Node,
  type NodeChange,
  type OnEdgesChange,
  type OnNodesChange,
  type Viewport,
} from '@xyflow/react';
import { nanoid } from 'nanoid';

// ──────────────────────────────────────────────
// Types
// ──────────────────────────────────────────────

export type FlowNode = Node<{
  label: string;
  [key: string]: unknown;
}>;

export type FlowEdge = Edge<{
  label?: string;
  [key: string]: unknown;
}>;

export type FlowState = {
  // Core data
  nodes: FlowNode[];
  edges: FlowEdge[];
  // Viewport (not tracked in undo history)
  viewport: Viewport;

  // React Flow handlers
  onNodesChange: OnNodesChange<FlowNode>;
  onEdgesChange: OnEdgesChange<FlowEdge>;
  onConnect: (connection: Connection) => void;

  // Node operations
  addNode: (type: string, position: { x: number; y: number }, data?: Partial<FlowNode['data']>) => string;
  updateNodeData: (id: string, data: Partial<FlowNode['data']>) => void;
  removeNode: (id: string) => void;
  setNodes: (nodes: FlowNode[]) => void;

  // Edge operations
  removeEdge: (id: string) => void;
  setEdges: (edges: FlowEdge[]) => void;

  // Bulk operations
  clearFlow: () => void;
  loadFlow: (nodes: FlowNode[], edges: FlowEdge[], viewport?: Viewport) => void;

  // Viewport
  setViewport: (viewport: Viewport) => void;

  // Selection helpers
  getSelectedNodes: () => FlowNode[];
  getSelectedEdges: () => FlowEdge[];
};

// ──────────────────────────────────────────────
// Initial state
// ──────────────────────────────────────────────

const INITIAL_NODES: FlowNode[] = [];
const INITIAL_EDGES: FlowEdge[] = [];
const INITIAL_VIEWPORT: Viewport = { x: 0, y: 0, zoom: 1 };

// ──────────────────────────────────────────────
// Store
// ──────────────────────────────────────────────

export const useFlowStore = create<FlowState>()(
  temporal(
    (set, get) => ({
      nodes: INITIAL_NODES,
      edges: INITIAL_EDGES,
      viewport: INITIAL_VIEWPORT,

      // ── React Flow change handlers ──
      onNodesChange: (changes: NodeChange<FlowNode>[]) =>
        set((s) => ({ nodes: applyNodeChanges(changes, s.nodes) })),

      onEdgesChange: (changes: EdgeChange<FlowEdge>[]) =>
        set((s) => ({ edges: applyEdgeChanges(changes, s.edges) })),

      onConnect: (connection: Connection) =>
        set((s) => ({
          edges: addEdge(
            {
              ...connection,
              id: nanoid(),
              type: 'smoothstep',
              animated: false,
            },
            s.edges,
          ),
        })),

      // ── Node operations ──
      addNode: (type, position, data = {}) => {
        const id = nanoid();
        set((s) => ({
          nodes: [
            ...s.nodes,
            {
              id,
              type,
              position,
              data: { label: `${type} node`, ...data },
            },
          ],
        }));
        return id;
      },

      updateNodeData: (id, data) =>
        set((s) => ({
          nodes: s.nodes.map((n) =>
            n.id === id ? { ...n, data: { ...n.data, ...data } } : n,
          ),
        })),

      removeNode: (id) =>
        set((s) => ({
          nodes: s.nodes.filter((n) => n.id !== id),
          edges: s.edges.filter((e) => e.source !== id && e.target !== id),
        })),

      setNodes: (nodes) => set({ nodes }),

      // ── Edge operations ──
      removeEdge: (id) =>
        set((s) => ({ edges: s.edges.filter((e) => e.id !== id) })),

      setEdges: (edges) => set({ edges }),

      // ── Bulk ──
      clearFlow: () =>
        set({ nodes: INITIAL_NODES, edges: INITIAL_EDGES }),

      loadFlow: (nodes, edges, viewport) =>
        set({ nodes, edges, viewport: viewport ?? INITIAL_VIEWPORT }),

      // ── Viewport (not in undo history — set directly) ──
      setViewport: (viewport) => set({ viewport }),

      // ── Selection helpers ──
      getSelectedNodes: () => get().nodes.filter((n) => n.selected),
      getSelectedEdges: () => get().edges.filter((e) => e.selected),
    }),

    {
      // Only track nodes/edges in undo history, not viewport or handlers
      partialize: (state) =>
        Object.fromEntries(
          Object.entries(state).filter(([key]) =>
            ['nodes', 'edges'].includes(key),
          ),
        ),
      equality: (a, b) => shallow(a, b),
      limit: 50,
    },
  ),
);

// ──────────────────────────────────────────────
// Undo/Redo hook
// ──────────────────────────────────────────────

export function useFlowHistory() {
  const { undo, redo, pastStates, futureStates, clear } =
    useFlowStore.temporal.getState();

  return {
    undo,
    redo,
    clear,
    canUndo: pastStates.length > 0,
    canRedo: futureStates.length > 0,
    historySize: pastStates.length,
  };
}

// ──────────────────────────────────────────────
// Stable selectors (use these to avoid re-renders)
// ──────────────────────────────────────────────

export const selectNodes = (s: FlowState) => s.nodes;
export const selectEdges = (s: FlowState) => s.edges;
export const selectViewport = (s: FlowState) => s.viewport;
export const selectOnNodesChange = (s: FlowState) => s.onNodesChange;
export const selectOnEdgesChange = (s: FlowState) => s.onEdgesChange;
export const selectOnConnect = (s: FlowState) => s.onConnect;

// ──────────────────────────────────────────────
// FlowCanvas usage example:
// ──────────────────────────────────────────────
//
// import { ReactFlow, ReactFlowProvider } from '@xyflow/react';
// import '@xyflow/react/dist/style.css';
// import {
//   useFlowStore,
//   selectNodes, selectEdges,
//   selectOnNodesChange, selectOnEdgesChange, selectOnConnect,
// } from './flowStore';
//
// function FlowCanvas() {
//   const nodes = useFlowStore(selectNodes);
//   const edges = useFlowStore(selectEdges);
//   const onNodesChange = useFlowStore(selectOnNodesChange);
//   const onEdgesChange = useFlowStore(selectOnEdgesChange);
//   const onConnect = useFlowStore(selectOnConnect);
//
//   return (
//     <ReactFlow
//       nodes={nodes}
//       edges={edges}
//       onNodesChange={onNodesChange}
//       onEdgesChange={onEdgesChange}
//       onConnect={onConnect}
//       proOptions={{ hideAttribution: true }}
//       fitView
//     />
//   );
// }
//
// export default function App() {
//   return (
//     <ReactFlowProvider>
//       <FlowCanvas />
//     </ReactFlowProvider>
//   );
// }
