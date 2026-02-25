# React Flow v12 — Enterprise Patterns

## Table of Contents
1. [Zustand Store Architecture](#1-zustand-store-architecture)
2. [Undo/Redo with zundo](#2-undoredo-with-zundo)
3. [Drag-and-Drop Sidebar](#3-drag-and-drop-sidebar)
4. [Auto-Layout (Dagre / ELK)](#4-auto-layout)
5. [Context Menu](#5-context-menu)
6. [Copy/Paste](#6-copypaste)
7. [Save & Restore](#7-save--restore)
8. [Prevent Cycles (DAG Validation)](#8-prevent-cycles)
9. [Keyboard Shortcuts](#9-keyboard-shortcuts)
10. [Performance](#10-performance)
11. [Dark Mode with Tailwind](#11-dark-mode)
12. [SSR/SSG Setup](#12-ssrsg)
13. [SubFlows (Parent/Child Nodes)](#13-subflows)
14. [Edge Reconnection](#14-edge-reconnection)
15. [Custom Connection Line](#15-custom-connection-line)
16. [Auto-Layout on Mount (useNodesInitialized)](#16-auto-layout-on-mount)

---

## 1. Zustand Store Architecture

For enterprise flows, split concerns into separate slices:

```ts
// store/slices/nodeSlice.ts
import { type StateCreator } from 'zustand';
import { applyNodeChanges, type Node, type OnNodesChange } from '@xyflow/react';

export type NodeSlice = {
  nodes: Node[];
  onNodesChange: OnNodesChange;
  setNodes: (nodes: Node[]) => void;
  addNode: (node: Node) => void;
  updateNodeData: (id: string, data: Partial<Node['data']>) => void;
  removeNode: (id: string) => void;
};

export const createNodeSlice: StateCreator<NodeSlice> = (set, get) => ({
  nodes: [],
  onNodesChange: (changes) =>
    set((s) => ({ nodes: applyNodeChanges(changes, s.nodes) })),
  setNodes: (nodes) => set({ nodes }),
  addNode: (node) => set((s) => ({ nodes: [...s.nodes, node] })),
  updateNodeData: (id, data) =>
    set((s) => ({
      nodes: s.nodes.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, ...data } } : n
      ),
    })),
  removeNode: (id) =>
    set((s) => ({ nodes: s.nodes.filter((n) => n.id !== id) })),
});
```

```ts
// store/flowStore.ts
import { create } from 'zustand';
import { createNodeSlice, type NodeSlice } from './slices/nodeSlice';
import { createEdgeSlice, type EdgeSlice } from './slices/edgeSlice';

type FlowStore = NodeSlice & EdgeSlice;

export const useFlowStore = create<FlowStore>()((...args) => ({
  ...createNodeSlice(...args),
  ...createEdgeSlice(...args),
}));
```

**Selector pattern** to minimize re-renders:
```ts
// Stable selectors — define outside component
const selectNodes = (s: FlowStore) => s.nodes;
const selectOnNodesChange = (s: FlowStore) => s.onNodesChange;

function FlowCanvas() {
  const nodes = useFlowStore(selectNodes);
  const onNodesChange = useFlowStore(selectOnNodesChange);
  // ...
}
```

---

## 2. Undo/Redo with zundo

```bash
npm install zundo
```

```ts
import { create } from 'zustand';
import { temporal } from 'zundo';
import { useStoreWithEqualityFn } from 'zustand/traditional';
import { shallow } from 'zustand/shallow';

export const useFlowStore = create<FlowStore>()(
  temporal(
    (set) => ({
      nodes: [],
      edges: [],
      // ...slices
    }),
    {
      // Only track nodes/edges in history (not UI state)
      partialize: (state) => ({ nodes: state.nodes, edges: state.edges }),
      equality: (a, b) => shallow(a, b),
      limit: 50,  // max history entries
    }
  )
);

// Undo/redo hook
export function useFlowHistory() {
  const { undo, redo, futureStates, pastStates, clear } =
    useFlowStore.temporal.getState();
  const canUndo = pastStates.length > 0;
  const canRedo = futureStates.length > 0;
  return { undo, redo, canUndo, canRedo, clear };
}

// Usage with keyboard shortcuts
function UndoRedoControls() {
  const { undo, redo, canUndo, canRedo } = useFlowHistory();
  
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey && canUndo) undo();
      if ((e.metaKey || e.ctrlKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey)) && canRedo) redo();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [undo, redo, canUndo, canRedo]);

  return (
    <div className="flex gap-1">
      <Button variant="ghost" size="icon" onClick={undo} disabled={!canUndo}>
        <Undo2 className="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onClick={redo} disabled={!canRedo}>
        <Redo2 className="h-4 w-4" />
      </Button>
    </div>
  );
}
```

---

## 3. Drag-and-Drop Sidebar

```tsx
// components/Sidebar.tsx
type NodeTypeItem = { type: string; label: string; icon: LucideIcon };

export function Sidebar({ items }: { items: NodeTypeItem[] }) {
  return (
    <aside className="w-56 border-r bg-background p-3 flex flex-col gap-2">
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
        Nodes
      </p>
      {items.map((item) => (
        <SidebarItem key={item.type} item={item} />
      ))}
    </aside>
  );
}

function SidebarItem({ item }: { item: NodeTypeItem }) {
  const onDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('application/reactflow', item.type);
    e.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div
      draggable
      onDragStart={onDragStart}
      className="flex items-center gap-2 p-2 rounded-md border bg-card text-sm cursor-grab hover:bg-accent transition-colors"
    >
      <item.icon className="h-4 w-4 text-muted-foreground" />
      {item.label}
    </div>
  );
}

// components/FlowCanvas.tsx — drop handler
function FlowCanvas() {
  const { screenToFlowPosition, addNodes } = useReactFlow();
  const idRef = useRef(0);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const type = e.dataTransfer.getData('application/reactflow');
      if (!type) return;
      const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });
      addNodes({
        id: `${type}-${++idRef.current}`,
        type,
        position,
        data: { label: `${type} ${idRef.current}` },
      });
    },
    [screenToFlowPosition, addNodes]
  );

  return (
    <ReactFlow onDrop={onDrop} onDragOver={onDragOver} ... />
  );
}
```

---

## 4. Auto-Layout

### Dagre (fast, tree/graph layouts)
```bash
npm install @dagrejs/dagre
npm install -D @types/dagre
```

```ts
// lib/layout/dagre.ts
import Dagre from '@dagrejs/dagre';
import type { Node, Edge } from '@xyflow/react';

type Direction = 'TB' | 'LR' | 'BT' | 'RL';

export function dagreLayout(
  nodes: Node[],
  edges: Edge[],
  direction: Direction = 'LR'
) {
  const g = new Dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: direction, ranksep: 80, nodesep: 40, edgesep: 20 });

  for (const node of nodes) {
    g.setNode(node.id, {
      width: node.measured?.width ?? node.width ?? 160,
      height: node.measured?.height ?? node.height ?? 60,
    });
  }
  for (const edge of edges) {
    g.setEdge(edge.source, edge.target);
  }

  Dagre.layout(g);

  return {
    nodes: nodes.map((node) => {
      const { x, y } = g.node(node.id);
      const w = node.measured?.width ?? node.width ?? 160;
      const h = node.measured?.height ?? node.height ?? 60;
      return { ...node, position: { x: x - w / 2, y: y - h / 2 } };
    }),
    edges,
  };
}
```

```tsx
// Usage in component
function LayoutButton() {
  const { getNodes, getEdges, setNodes, fitView } = useReactFlow();
  
  const onLayout = useCallback(() => {
    const { nodes, edges } = dagreLayout(getNodes(), getEdges(), 'LR');
    setNodes(nodes);
    setTimeout(() => fitView({ padding: 0.2, duration: 300 }), 0);
  }, [getNodes, getEdges, setNodes, fitView]);

  return <Button onClick={onLayout}><LayoutDashboard className="h-4 w-4" /> Auto Layout</Button>;
}
```

### ELK (complex hierarchical layouts)
```bash
npm install elkjs
```

```ts
// lib/layout/elk.ts
import ELK, { type ElkNode } from 'elkjs/lib/elk.bundled.js';
import type { Node, Edge } from '@xyflow/react';

const elk = new ELK();

export async function elkLayout(nodes: Node[], edges: Edge[]) {
  const elkNodes: ElkNode = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': 'RIGHT',
      'elk.spacing.nodeNode': '60',
      'elk.layered.spacing.nodeNodeBetweenLayers': '80',
    },
    children: nodes.map((n) => ({
      id: n.id,
      width: n.measured?.width ?? 160,
      height: n.measured?.height ?? 60,
    })),
    edges: edges.map((e) => ({
      id: e.id,
      sources: [e.source],
      targets: [e.target],
    })),
  };

  const layout = await elk.layout(elkNodes);

  return nodes.map((node) => {
    const layoutNode = layout.children?.find((n) => n.id === node.id);
    return {
      ...node,
      position: { x: layoutNode?.x ?? 0, y: layoutNode?.y ?? 0 },
    };
  });
}
```

---

## 5. Context Menu

```tsx
// Using shadcn DropdownMenu
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

type ContextMenuState = { nodeId: string; x: number; y: number } | null;

function FlowWithContextMenu() {
  const [menu, setMenu] = useState<ContextMenuState>(null);
  const { deleteElements, addNodes, getNode } = useReactFlow();
  const ref = useRef<HTMLDivElement>(null);

  const onNodeContextMenu = useCallback(
    (e: React.MouseEvent, node: Node) => {
      e.preventDefault();
      const bounds = ref.current?.getBoundingClientRect();
      setMenu({
        nodeId: node.id,
        x: e.clientX - (bounds?.left ?? 0),
        y: e.clientY - (bounds?.top ?? 0),
      });
    },
    []
  );

  const onPaneClick = useCallback(() => setMenu(null), []);

  return (
    <div ref={ref} className="relative w-full h-full">
      <ReactFlow
        onNodeContextMenu={onNodeContextMenu}
        onPaneClick={onPaneClick}
        ...
      />
      {menu && (
        <div
          className="absolute z-50"
          style={{ left: menu.x, top: menu.y }}
        >
          <DropdownMenu open onOpenChange={() => setMenu(null)}>
            <DropdownMenuTrigger asChild>
              <span />
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem
                onClick={() => {
                  deleteElements({ nodes: [{ id: menu.nodeId }] });
                  setMenu(null);
                }}
              >
                <Trash2 className="h-4 w-4 mr-2" /> Delete Node
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => { /* duplicate */ setMenu(null); }}>
                <Copy className="h-4 w-4 mr-2" /> Duplicate
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
    </div>
  );
}
```

---

## 6. Copy/Paste

```ts
// lib/clipboard.ts
import { nanoid } from 'nanoid';
import type { Node, Edge } from '@xyflow/react';

const OFFSET = { x: 20, y: 20 };

export function copyElements(nodes: Node[], edges: Edge[]) {
  return { nodes, edges };
}

export function pasteElements(
  clipboard: { nodes: Node[]; edges: Edge[] },
  currentNodes: Node[]
) {
  const idMap = new Map<string, string>();
  const newNodes = clipboard.nodes.map((n) => {
    const newId = nanoid();
    idMap.set(n.id, newId);
    return {
      ...n,
      id: newId,
      selected: true,
      position: { x: n.position.x + OFFSET.x, y: n.position.y + OFFSET.y },
    };
  });

  const selectedIds = new Set(clipboard.nodes.map((n) => n.id));
  const newEdges = clipboard.edges
    .filter((e) => selectedIds.has(e.source) && selectedIds.has(e.target))
    .map((e) => ({
      ...e,
      id: nanoid(),
      source: idMap.get(e.source)!,
      target: idMap.get(e.target)!,
    }));

  return { nodes: newNodes, edges: newEdges };
}
```

---

## 7. Save & Restore

```ts
// lib/persistence.ts
import type { ReactFlowJsonObject } from '@xyflow/react';

const STORAGE_KEY = 'flow-state';

export const persist = {
  save(flow: ReactFlowJsonObject) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(flow));
  },
  load(): ReactFlowJsonObject | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  clear() {
    localStorage.removeItem(STORAGE_KEY);
  },
};
```

```tsx
// Toolbar with save/restore
function PersistenceControls() {
  const { toObject, setNodes, setEdges, setViewport } = useReactFlow();

  const onSave = () => persist.save(toObject());

  const onRestore = () => {
    const flow = persist.load();
    if (!flow) return;
    setNodes(flow.nodes ?? []);
    setEdges(flow.edges ?? []);
    if (flow.viewport) setViewport(flow.viewport);
  };

  return (
    <>
      <Button variant="outline" size="sm" onClick={onSave}>
        <Save className="h-4 w-4 mr-1" /> Save
      </Button>
      <Button variant="outline" size="sm" onClick={onRestore}>
        <FolderOpen className="h-4 w-4 mr-1" /> Restore
      </Button>
    </>
  );
}
```

---

## 8. Prevent Cycles

```ts
// lib/validation.ts
import { getIncomers, getOutgoers, type Node, type Edge } from '@xyflow/react';

export function hasCycle(
  connection: { source: string; target: string },
  nodes: Node[],
  edges: Edge[]
): boolean {
  const visited = new Set<string>();
  
  function dfs(nodeId: string): boolean {
    if (nodeId === connection.source) return true;
    if (visited.has(nodeId)) return false;
    visited.add(nodeId);
    return getIncomers({ id: nodeId } as Node, nodes, edges)
      .some((n) => dfs(n.id));
  }

  return dfs(connection.target);
}
```

```tsx
// In ReactFlow component
const isValidConnection: IsValidConnection = useCallback(
  (connection) => {
    const nodes = getNodes();
    const edges = getEdges();
    if (connection.source === connection.target) return false;  // no self-loops
    return !hasCycle(connection, nodes, edges);
  },
  [getNodes, getEdges]
);
```

---

## 9. Keyboard Shortcuts

```tsx
// Default React Flow shortcuts:
// Backspace/Delete — delete selected
// Ctrl+A — select all
// Escape — deselect all

// Custom shortcuts via useKeyPress:
function FlowShortcuts() {
  const deleteKey = useKeyPress(['Backspace', 'Delete']);
  const { getNodes, getEdges, deleteElements } = useReactFlow();

  // Custom: Ctrl+D to duplicate
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
        e.preventDefault();
        const selectedNodes = getNodes().filter((n) => n.selected);
        // paste logic...
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [getNodes]);

  return null;
}

// Or configure which keys delete:
<ReactFlow
  deleteKeyCode={['Backspace', 'Delete']}
  selectionKeyCode="Shift"
  multiSelectionKeyCode={['Meta', 'Control']}
  panActivationKeyCode="Space"
  zoomActivationKeyCode={['Meta', 'Control']}
/>
```

---

## 10. Performance

**Problem**: Large flows (200+ nodes) can become sluggish.

**Solutions:**

1. **Memoize nodeTypes and edgeTypes** — define outside component or with `useMemo`:
   ```ts
   // Module scope (best)
   const nodeTypes: NodeTypes = { custom: CustomNode };
   // or
   const nodeTypes = useMemo(() => ({ custom: CustomNode }), []);
   ```

2. **Memoize custom node components**:
   ```ts
   export const CustomNode = memo(({ data, selected }: NodeProps) => {
     return <div>...</div>;
   });
   ```

3. **Use `useNodesData` instead of `useNodes`** for subscriptions to specific nodes.

4. **`onlyRenderVisibleElements`** for very large graphs:
   ```tsx
   <ReactFlow onlyRenderVisibleElements />
   ```

5. **Debounce expensive operations** (layout, save):
   ```ts
   const debouncedSave = useDebouncedCallback(() => persist.save(toObject()), 1000);
   ```

6. **Avoid inline functions** in JSX for event handlers:
   ```tsx
   // ❌ Bad — creates new function on every render
   <ReactFlow onNodesChange={(c) => setNodes(applyNodeChanges(c, nodes))} />
   // ✅ Good — stable reference
   <ReactFlow onNodesChange={onNodesChange} />
   ```

---

## 11. Dark Mode

React Flow v12 supports `colorMode="dark"` natively. With Tailwind:

```tsx
// tailwind.config.js
module.exports = {
  darkMode: 'class',  // or 'media'
  // ...
};
```

```tsx
// In FlowCanvas
const { resolvedTheme } = useTheme(); // next-themes or similar

<ReactFlow
  colorMode={resolvedTheme === 'dark' ? 'dark' : 'light'}
  ...
/>
```

**Custom CSS variables** for colors:
```css
/* Override React Flow's CSS variables */
.react-flow {
  --xy-background-color: theme('colors.background');
  --xy-node-background-color: theme('colors.card');
  --xy-node-border-color: theme('colors.border');
  --xy-edge-stroke: theme('colors.muted-foreground');
  --xy-selection-background-color: theme('colors.primary / 0.1');
  --xy-selection-border-color: theme('colors.primary');
  --xy-controls-button-background-color: theme('colors.background');
  --xy-controls-button-border-color: theme('colors.border');
  --xy-minimap-background-color: theme('colors.muted');
}
```

---

## 12. SSR/SSG

For Next.js and other SSR frameworks:

```tsx
// Define dimensions on nodes upfront (avoids hydration mismatch)
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Node 1' },
    width: 160,     // hint for SSR
    height: 60,
  },
];

// Always wrap in ReactFlowProvider
export function FlowApp() {
  return (
    <ReactFlowProvider>
      <FlowCanvas />
    </ReactFlowProvider>
  );
}

// Dynamic import to avoid SSR issues with window
const FlowApp = dynamic(() => import('./FlowApp'), { ssr: false });
```

**Note**: React Flow does support SSR in v12 if you provide `width`, `height`, and `handles` on nodes. For complex apps, `ssr: false` is simpler.

---

