# React Flow v12 — Enterprise Patterns (Advanced)

> Continued from enterprise.md (§1-§12)

## 13. SubFlows

Parent/child node containment — children are positioned relative to their parent and optionally constrained inside it.

```ts
// Parent node (use a custom type with NodeResizer for dynamic sizing)
const parentNode: Node = {
  id: 'group-1',
  type: 'group',    // your custom GroupNode component
  position: { x: 100, y: 100 },
  data: { label: 'Pipeline A' },
  style: { width: 400, height: 300 },
};

// Child nodes — position is relative to parent
const childA: Node = {
  id: 'child-a',
  type: 'base',
  position: { x: 40, y: 60 },    // offset within parent
  data: { label: 'Step 1' },
  parentId: 'group-1',
  extent: 'parent',               // constrain dragging inside parent bounds
};

const childB: Node = {
  id: 'child-b',
  type: 'base',
  position: { x: 220, y: 60 },
  data: { label: 'Step 2' },
  parentId: 'group-1',
  extent: 'parent',
  expandParent: true,             // parent resizes to fit child when dragged near edge
};
```

**Key rules:**
- Parent node must appear **before** children in the `nodes` array
- Edges between children work normally using their IDs
- `extent: 'parent'` constrains child dragging; omit to allow free movement outside
- `expandParent: true` auto-expands parent when a child is dragged to the edge
- Use `NodeResizer` on the parent for user-resizable groups (see `custom-nodes.md §5`)
- Set `zIndexMode="auto"` on `<ReactFlow>` so parent/child z-index is managed correctly in sub-flows (default `'basic'` only handles selections)

```tsx
// Programmatically add a child to a group on drop
const onDrop = useCallback((e: React.DragEvent) => {
  const type = e.dataTransfer.getData('application/reactflow');
  const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });

  // Check if dropped onto a group node
  const intersecting = getIntersectingNodes({ x: position.x, y: position.y, width: 1, height: 1 });
  const group = intersecting.find((n) => n.type === 'group');

  addNodes({
    id: nanoid(),
    type,
    position: group
      ? { x: position.x - group.position.x, y: position.y - group.position.y }
      : position,
    data: { label: type },
    ...(group ? { parentId: group.id, extent: 'parent' } : {}),
  });
}, [screenToFlowPosition, addNodes, getIntersectingNodes]);
```

---

## 14. Edge Reconnection

Allow users to drag an existing edge endpoint to reconnect it to a different handle.

```tsx
import { reconnectEdge, type Edge, type Connection, type HandleType, type FinalConnectionState } from '@xyflow/react';

// Controlled with useEdgesState
function FlowWithReconnect() {
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const edgeReconnectSuccessful = useRef(true);

  // Called when reconnect drag starts — track success to handle abort
  const onReconnectStart = useCallback(
    (_evt: React.MouseEvent, _edge: Edge, _handleType: HandleType) => {
      edgeReconnectSuccessful.current = false;
    },
    []
  );

  // Called when edge is dropped on a valid handle
  const onReconnect = useCallback(
    (oldEdge: Edge, newConnection: Connection) => {
      edgeReconnectSuccessful.current = true;
      setEdges((els) => reconnectEdge(oldEdge, newConnection, els));
    },
    []
  );

  // Called when reconnect drag ends — delete edge if dropped on invalid target
  const onReconnectEnd = useCallback(
    (_evt: MouseEvent | TouchEvent, edge: Edge, _handleType: HandleType, _connectionState: FinalConnectionState) => {
      if (!edgeReconnectSuccessful.current) {
        setEdges((eds) => eds.filter((e) => e.id !== edge.id));
      }
      edgeReconnectSuccessful.current = true;
    },
    []
  );

  return (
    <ReactFlow
      edges={edges}
      onEdgesChange={onEdgesChange}
      onReconnect={onReconnect}
      onReconnectStart={onReconnectStart}
      onReconnectEnd={onReconnectEnd}
      edgesReconnectable   // default true — set false to disable globally
    />
  );
}
```

**Per-edge control**: set `reconnectable: false` on individual edge objects to prevent specific edges from being reconnected.

---

## 15. Custom Connection Line

Override the line drawn while the user is dragging a new connection:

```tsx
import type { ConnectionLineComponentProps } from '@xyflow/react';
import { getStraightPath } from '@xyflow/react';

function CustomConnectionLine({
  fromX, fromY, toX, toY,
  fromPosition, toPosition,
  connectionStatus,
}: ConnectionLineComponentProps) {
  const [edgePath] = getStraightPath({ sourceX: fromX, sourceY: fromY, targetX: toX, targetY: toY });

  const color = connectionStatus === 'valid'
    ? 'hsl(var(--primary))'
    : connectionStatus === 'invalid'
    ? 'hsl(var(--destructive))'
    : 'hsl(var(--muted-foreground))';

  return (
    <g>
      <path
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeDasharray="5 3"
        d={edgePath}
      />
      {/* Endpoint dot */}
      <circle cx={toX} cy={toY} r={4} fill={color} />
    </g>
  );
}

// Register:
<ReactFlow connectionLineComponent={CustomConnectionLine} ... />
```

**`connectionStatus`** values:
- `null` — `isValidConnection` is NOT configured (always null without it)
- `'valid'` — hovering a handle that passes `isValidConnection`
- `'invalid'` — hovering a handle that fails `isValidConnection`

So to use `connectionStatus` for color feedback you **must** provide `isValidConnection` to `<ReactFlow>`.

Use `useConnection()` inside nodes to react to in-progress connections:
```ts
const { inProgress, fromHandle, toHandle } = useConnection();
// Highlight eligible handles while a connection is being dragged
```

---

## 16. Auto-Layout on Mount

Trigger Dagre/ELK layout once after all nodes have been measured (i.e., rendered into DOM):

```tsx
import { useNodesInitialized, useReactFlow } from '@xyflow/react';
import { useEffect } from 'react';
import { dagreLayout } from '@/lib/layout/dagre';

function AutoLayoutOnMount() {
  const initialized = useNodesInitialized();
  const { getNodes, getEdges, setNodes, fitView } = useReactFlow();
  const hasLayedOut = useRef(false);

  useEffect(() => {
    if (!initialized || hasLayedOut.current) return;
    hasLayedOut.current = true;                         // run once only

    const { nodes } = dagreLayout(getNodes(), getEdges(), 'LR');
    setNodes(nodes);
    setTimeout(() => fitView({ padding: 0.2, duration: 400 }), 0);
  }, [initialized]);

  return null;
}

// Mount inside <ReactFlow> or <ReactFlowProvider>:
<ReactFlow ...>
  <AutoLayoutOnMount />
  <Background />
  <Controls />
</ReactFlow>
```

**`useNodesInitialized` options:**
```ts
// Default: waits for all nodes to have measured dimensions
const initialized = useNodesInitialized();

// Include hidden nodes in the check:
const initialized = useNodesInitialized({ includeHiddenNodes: true });
```
