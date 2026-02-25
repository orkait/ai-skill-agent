# React Flow v12 — Quickstart Examples

Code examples for common React Flow patterns. See `SKILL.md` for rules and decision guide.

---

## 1. Minimal Controlled Flow

```tsx
import { useCallback } from 'react';
import {
  ReactFlow, ReactFlowProvider,
  Background, BackgroundVariant,
  Controls, MiniMap,
  addEdge,
  type Node, type Edge, type Connection,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useFlowStore } from './store/flowStore';

const nodeTypes = { /* custom: CustomNode */ };
const edgeTypes = { /* custom: CustomEdge */ };

export function FlowCanvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, addEdge: add } = useFlowStore();

  const onConnect = useCallback(
    (connection: Connection) => add(connection),
    [add]
  );

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        colorMode="light"
        defaultEdgeOptions={{ animated: true, type: 'smoothstep' }}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

export default function App() {
  return (
    <ReactFlowProvider>
      <FlowCanvas />
    </ReactFlowProvider>
  );
}
```

---

## 2. Zustand Flow Store (Standard Pattern)

See `assets/store-template.ts` for the full boilerplate. Core shape:

```ts
import { create } from 'zustand';
import {
  applyNodeChanges, applyEdgeChanges, addEdge,
  type Node, type Edge, type OnNodesChange,
  type OnEdgesChange, type Connection,
} from '@xyflow/react';

type FlowState = {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  addEdge: (connection: Connection) => void;
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
};

export const useFlowStore = create<FlowState>()((set) => ({
  nodes: [],
  edges: [],
  onNodesChange: (changes) =>
    set((s) => ({ nodes: applyNodeChanges(changes, s.nodes) })),
  onEdgesChange: (changes) =>
    set((s) => ({ edges: applyEdgeChanges(changes, s.edges) })),
  addEdge: (connection) =>
    set((s) => ({ edges: addEdge(connection, s.edges) })),
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
}));
```

**Undo/redo** with `zundo`: wrap create with `temporal()` — see `references/core/patterns.md §2`.

---

## 3. Custom Node Pattern

```tsx
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { cn } from '@/lib/utils';

type MyNodeData = { label: string; status?: 'idle' | 'running' | 'done' | 'error' };

export function MyNode({ data, selected }: NodeProps<Node<MyNodeData>>) {
  return (
    <div className={cn(
      'rounded-lg border bg-card p-3 shadow-sm min-w-[160px]',
      selected && 'ring-2 ring-primary'
    )}>
      <Handle type="target" position={Position.Left} />
      <p className="text-sm font-medium">{data.label}</p>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
```

**Register in nodeTypes** (memoize outside component or in module scope):
```ts
const nodeTypes = { myNode: MyNode };
```

See `references/core/custom-nodes.md` for: multiple handles, handle IDs, resize, toolbar, status indicators.

---

## 4. Common Imperative Operations

```ts
const { getNode, getEdge, setNodes, setEdges,
        addNodes, addEdges, deleteElements,
        fitView, zoomIn, zoomOut,
        screenToFlowPosition, getViewport, setViewport,
        getNodesBounds, toObject, viewportInitialized } = useReactFlow();

// Convert screen position to flow coordinates (drag-and-drop)
const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });

// Add a node programmatically
addNodes({ id: nanoid(), type: 'myNode', position, data: { label: 'New' } });

// Delete elements (async)
await deleteElements({ nodes: [{ id: 'n1' }], edges: [{ id: 'e1' }] });

// Export / save
const flowJson = toObject(); // { nodes, edges, viewport }

// Layout recalculation (after programmatic handle changes)
updateNodeInternals('nodeId');
```

---

## 5. Connection Validation

```tsx
import { type IsValidConnection } from '@xyflow/react';

const isValidConnection: IsValidConnection = useCallback((connection) => {
  const { source, target } = connection;
  if (source === target) return false;
  const sourceNode = getNode(source);
  const targetNode = getNode(target);
  return sourceNode?.data?.outputType === targetNode?.data?.inputType;
}, [getNode]);

<ReactFlow isValidConnection={isValidConnection} ... />
```

---

## 6. Drag-and-Drop onto Canvas

```tsx
// Sidebar item
<div draggable onDragStart={(e) => e.dataTransfer.setData('application/reactflow', 'myNode')}>
  Drag me
</div>

// Canvas drop handler
const onDrop = useCallback((e: React.DragEvent) => {
  e.preventDefault();
  const type = e.dataTransfer.getData('application/reactflow');
  if (!type) return;
  const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });
  addNodes({ id: nanoid(), type, position, data: { label: type } });
}, [screenToFlowPosition, addNodes]);

<ReactFlow onDrop={onDrop} onDragOver={(e) => e.preventDefault()} ... />
```

---

## 7. Layout with Dagre

```bash
npm install @dagrejs/dagre
npm install -D @types/dagre
```

```ts
import dagre from '@dagrejs/dagre';
import type { Node, Edge } from '@xyflow/react';

export function getLayoutedElements(nodes: Node[], edges: Edge[], direction = 'LR') {
  const g = new dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: direction, ranksep: 80, nodesep: 40 });

  nodes.forEach((n) => {
    g.setNode(n.id, {
      width: n.measured?.width ?? 160,
      height: n.measured?.height ?? 60,
    });
  });
  edges.forEach((e) => g.setEdge(e.source, e.target));
  dagre.layout(g);

  return {
    nodes: nodes.map((n) => {
      const { x, y } = g.node(n.id);
      return { ...n, position: { x: x - (n.measured?.width ?? 160) / 2, y: y - (n.measured?.height ?? 60) / 2 } };
    }),
    edges,
  };
}
```

---

## 8. Save & Restore

```ts
// Save
const save = () => {
  const flow = toObject();
  localStorage.setItem('flow', JSON.stringify(flow));
};

// Restore
const restore = () => {
  const flow = JSON.parse(localStorage.getItem('flow') || 'null');
  if (!flow) return;
  setNodes(flow.nodes || []);
  setEdges(flow.edges || []);
  setViewport(flow.viewport);
};
```

---

## 9. Accessibility & Color Mode

```tsx
<ReactFlow
  colorMode="system"         // auto light/dark based on OS
  ariaLabelConfig={{
    nodes: 'Flow nodes',
    edges: 'Flow edges',
  }}
  ...
/>
```
