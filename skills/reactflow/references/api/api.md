# React Flow v12 API Reference

## Table of Contents
1. [ReactFlow Component Props](#1-reactflow-component-props)
2. [Components](#2-components)
3. [Hooks](#3-hooks)
4. [Utility Functions](#4-utility-functions)
5. [Types](#5-key-types)

---

## 1. ReactFlow Component Props

### Common Props
| Prop | Type | Default | Notes |
|------|------|---------|-------|
| `nodes` | `Node[]` | `[]` | Controlled nodes array |
| `edges` | `Edge[]` | `[]` | Controlled edges array |
| `defaultNodes` | `Node[]` | — | Uncontrolled initial nodes |
| `defaultEdges` | `Edge[]` | — | Uncontrolled initial edges |
| `nodeTypes` | `NodeTypes` | built-ins | Custom node type map |
| `edgeTypes` | `EdgeTypes` | built-ins | Custom edge type map |
| `onNodesChange` | `OnNodesChange` | — | Apply node changes |
| `onEdgesChange` | `OnEdgesChange` | — | Apply edge changes |
| `onConnect` | `OnConnect` | — | Handle new connection |
| `onInit` | `OnInit` | — | Called after initial render |
| `nodeOrigin` | `[number, number]` | `[0,0]` | Node placement origin |
| `colorMode` | `'light'\|'dark'\|'system'` | `'light'` | CSS color scheme |
| `fitView` | `boolean` | false | Fit on mount |
| `fitViewOptions` | `FitViewOptions` | — | Padding, nodes filter |
| `defaultEdgeOptions` | `DefaultEdgeOptions` | — | Default edge props |
| `proOptions` | `ProOptions` | — | `{ hideAttribution: true }` |
| `debug` | `boolean` | false | Log events to console |

### Viewport Props
| Prop | Type | Default |
|------|------|---------|
| `defaultViewport` | `Viewport` | `{x:0, y:0, zoom:1}` |
| `minZoom` | `number` | `0.5` |
| `maxZoom` | `number` | `2` |
| `translateExtent` | `CoordinateExtent` | infinite |
| `nodeExtent` | `CoordinateExtent` | infinite |
| `snapToGrid` | `boolean` | false |
| `snapGrid` | `[number, number]` | `[15, 15]` |
| `panOnScrollSpeed` | `number` | `0.5` | Pan speed multiplier when `panOnScroll=true` |
| `panOnScrollMode` | `PanOnScrollMode` | `'free'` | `'free'\|'horizontal'\|'vertical'` |
| `viewport` | `Viewport` | — | Controlled viewport (needs `onViewportChange`) |
| `onViewportChange` | `(v: Viewport) => void` | — | Handler for controlled viewport |

### Edge Props
| Prop | Type | Default |
|------|------|---------|
| `edgesReconnectable` | `boolean` | true |
| `reconnectRadius` | `number` | `10` |
| `defaultMarkerColor` | `string` | `#b1b1b7` |

### Connection Line Props
| Prop | Type | Default | Notes |
|------|------|---------|-------|
| `connectionLineComponent` | `ConnectionLineComponent<NodeType>` | built-in | Custom SVG connection line component |
| `connectionLineStyle` | `CSSProperties` | — | Style for default connection line |
| `connectionLineContainerStyle` | `CSSProperties` | — | Style for the SVG container |
| `connectionLineType` | `ConnectionLineType` | `'default'` | `'default'(bezier)\|'straight'\|'step'\|'smoothstep'\|'simplebezier'` |
| `connectionRadius` | `number` | `20` | Drop within this radius of a handle to auto-connect |
| `connectionDragThreshold` | `number` | `1` | Pixels mouse must move before connection drag starts |

### Interaction Props
| Prop | Type | Default |
|------|------|---------|
| `nodesDraggable` | `boolean` | true |
| `nodesConnectable` | `boolean` | true |
| `elementsSelectable` | `boolean` | true |
| `panOnDrag` | `boolean\|number[]` | true |
| `panOnScroll` | `boolean` | false |
| `zoomOnScroll` | `boolean` | true |
| `zoomOnDoubleClick` | `boolean` | true |
| `selectNodesOnDrag` | `boolean` | true |
| `selectionMode` | `SelectionMode` | `'full'` |
| `connectionMode` | `ConnectionMode` | `'strict'` |
| `isValidConnection` | `IsValidConnection` | — |
| `onBeforeDelete` | `OnBeforeDelete` | — |
| `autoPanOnConnect` | `boolean` | true |
| `autoPanOnNodeDrag` | `boolean` | true |
| `preventScrolling` | `boolean` | true |
| `nodesFocusable` | `boolean` | true | Keyboard focus on nodes (a11y) |
| `edgesFocusable` | `boolean` | true | Keyboard focus on edges (a11y) |
| `elevateNodesOnSelect` | `boolean` | true | Raise z-index of selected nodes |
| `elevateEdgesOnSelect` | `boolean` | false | Raise z-index of connected edges when node selected |
| `selectionOnDrag` | `boolean` | false | Draw selection box without holding `selectionKeyCode` |
| `connectOnClick` | `boolean` | true | Click handle to start, click another to finish connection |
| `onlyRenderVisibleElements` | `boolean` | false | Skip rendering off-screen nodes/edges (perf) |
| `disableKeyboardA11y` | `boolean` | false | Disable arrow-key navigation and keyboard a11y |
| `nodeDragThreshold` | `number` | `1` | Pixels mouse must move before node drag event fires |
| `autoPanSpeed` | `number` | `15` | Speed for auto-pan when dragging near viewport edge |

### Key Event Props
```
onNodeClick, onNodeDoubleClick, onNodeMouseEnter, onNodeMouseLeave
onNodeDragStart, onNodeDrag, onNodeDragStop
onEdgeClick, onEdgeDoubleClick, onEdgeMouseEnter, onEdgeMouseLeave
onConnect, onConnectStart, onConnectEnd
onReconnect                                     // (oldEdge, newConnection) => void
onReconnectStart                                // (event: ReactMouseEvent, edge, handleType: HandleType) => void
onReconnectEnd                                  // (event: MouseEvent|TouchEvent, edge, handleType, connectionState: FinalConnectionState) => void
onNodesDelete, onEdgesDelete, onDelete
onMove, onMoveStart, onMoveEnd
onPaneClick, onPaneContextMenu
onSelectionChange, onSelectionDragStart, onSelectionDrag, onSelectionDragStop
onBeforeDelete                                  // return false to cancel deletion
```

---

## 2. Components

### `<Background />`
```tsx
<Background
  variant={BackgroundVariant.Dots | Lines | Cross}
  gap={20}           // grid gap in px
  size={1}           // dot/line size
  color="#aaa"
  className="..."
/>
```

### `<Controls />`
```tsx
<Controls
  position="bottom-left"
  showZoom={true}
  showFitView={true}
  showInteractive={true}
  orientation="vertical | horizontal"
/>
```

### `<MiniMap />`
```tsx
<MiniMap
  nodeColor={(node) => '#eee'}
  nodeStrokeColor="#999"
  nodeClassName="..."
  maskColor="rgba(0,0,0,0.1)"
  pannable={true}
  zoomable={true}
  position="bottom-right"
/>
```

### `<Panel />`
```tsx
// Absolutely positioned panel over the canvas
<Panel position="top-left | top-center | top-right | bottom-left | bottom-center | bottom-right | center-left | center-right">
  <button>Action</button>
</Panel>
```

### `<Handle />`
```tsx
<Handle
  type="source | target"
  position={Position.Left | Right | Top | Bottom}
  id="handle-id"           // required for multiple handles
  isConnectable={true}
  isConnectableStart={true}
  isConnectableEnd={true}
  style={{ background: '#555' }}
  className="..."
  onConnect={(connections) => {}}
/>
```

### `<NodeResizer />`
```tsx
<NodeResizer
  minWidth={100}
  minHeight={50}
  isVisible={selected}
  lineClassName="border-blue-400"
  handleClassName="h-3 w-3 bg-white border-2 border-blue-400"
/>
```

### `<NodeToolbar />`
```tsx
<NodeToolbar isVisible={selected} position={Position.Top}>
  <button>Delete</button>
</NodeToolbar>
```

### `<EdgeLabelRenderer />`
```tsx
// Render HTML labels on edges (portals out of SVG)
<EdgeLabelRenderer>
  <div
    style={{ transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)` }}
    className="nodrag nopan absolute"
  >
    Label
  </div>
</EdgeLabelRenderer>
```

### `<EdgeToolbar />`
```tsx
<EdgeToolbar
  x={labelX} y={labelY}
  isVisible={selected}
  alignX="center"    // 'left' | 'center' | 'right' — default 'center'
  alignY="center"    // 'top' | 'center' | 'bottom' — default 'center'
>
  <button>Delete</button>
</EdgeToolbar>
```

### `<BaseEdge />`
```tsx
<BaseEdge
  path={edgePath}          // SVG path string
  labelX={labelX}
  labelY={labelY}
  label="Edge Label"
  markerEnd={markerEnd}
  interactionWidth={20}
/>
```

### `<ViewportPortal />`
Renders children inside the viewport (moves with pan/zoom).

---

## 3. Hooks

All hooks must be used inside `<ReactFlow>` or `<ReactFlowProvider>`.

### `useReactFlow()`
Primary imperative API:
```ts
const {
  // Getters
  getNode,                  // returns user node (no internals)
  getInternalNode,          // returns InternalNode (includes measured, positionAbsolute, handles)
  getNodes, getEdge, getEdges,
  getNodesBounds,           // getNodesBounds(nodes) → Rect
  getIntersectingNodes,     // (nodeOrRect, partially?, nodes?) → Node[]
  isNodeIntersecting,       // (nodeOrRect, area: Rect, partially?) → boolean
  getHandleConnections,     // ({ type, id, nodeId }) → HandleConnection[] — @deprecated, prefer getNodeConnections
  getNodeConnections,       // ({ type?, handleId?, nodeId }) → NodeConnection[] — imperative useNodeConnections
  // Setters (trigger re-render)
  setNodes, setEdges,
  addNodes, addEdges,
  updateNode,               // (id, nodeOrUpdater, { replace: false }) — merges by default
  updateNodeData,           // (id, dataOrUpdater, { replace: false }) — merges into node.data
  updateEdge,               // (id, edgeOrUpdater, { replace: false })
  updateEdgeData,           // (id, dataOrUpdater, { replace: false }) — merges into edge.data
  deleteElements,           // returns Promise<{ deletedNodes, deletedEdges }>
  // Viewport
  getViewport, setViewport,
  fitView, fitBounds,
  zoomIn, zoomOut, zoomTo,
  // Coordinate conversion
  screenToFlowPosition,     // replaces project() from v11
  flowToScreenPosition,
  // Misc
  toObject,                 // serialize to JSON
  viewportInitialized,      // true once viewport is mounted and pan/zoom initialized
} = useReactFlow();
```

### `useNodesState(initialNodes)` / `useEdgesState(initialEdges)`
```ts
const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
```

### `useNodes()` / `useEdges()`
Subscribe to current nodes/edges array (re-renders on any change).

### `useNodesData(nodeIds: string | string[])`
Subscribe to specific node data only — more performant than `useNodes()`.
```ts
const nodeData = useNodesData('node-1');
// or
const multiData = useNodesData(['node-1', 'node-2']);
```

### `useNodeId()`
Get the ID of the current node from inside a custom node component.
```ts
const nodeId = useNodeId(); // string | null
```

### `useConnection()`
Returns the active connection state while dragging:
```ts
const connection = useConnection();
// ConnectionState: { inProgress: boolean, isValid: boolean|null, fromHandle, fromNode,
//                    toHandle, toNode, pointer, from, to, fromPosition, toPosition }
// isValid is non-null only when isValidConnection is provided to <ReactFlow>
// When inProgress=false all fields except inProgress are null
```

### `useHandleConnections({ type, nodeId?, id? })`
Get connections on a specific handle:
```ts
const connections = useHandleConnections({ type: 'target', id: 'my-handle' });
```

### `useNodeConnections({ type })`
Get all connections on current node (use inside custom node):
```ts
const connections = useNodeConnections({ type: 'source' });
```

### `useInternalNode(id)`
Access internal node (includes `measured`, `internals`):
```ts
const node = useInternalNode('node-1');
const { width, height } = node?.measured ?? {};
```

### `useUpdateNodeInternals()`
Trigger handle bounds recalculation:
```ts
const updateNodeInternals = useUpdateNodeInternals();
updateNodeInternals('node-id');             // one
updateNodeInternals(['id1', 'id2']);        // many
```

### `useViewport()`
```ts
const { x, y, zoom } = useViewport();
```

### `useOnViewportChange({ onStart, onChange, onEnd })`
```ts
useOnViewportChange({
  onStart: (viewport) => console.log(viewport),
  onChange: (viewport) => {},
  onEnd: (viewport) => {},
});
```

### `useOnSelectionChange({ onChange })`
```ts
useOnSelectionChange({
  onChange: ({ nodes, edges }) => console.log(nodes, edges),
});
```

### `useKeyPress(keyCode)`
```ts
const isPressed = useKeyPress('Shift');
const isMeta = useKeyPress(['Meta', 'Control']);
```

### `useNodesInitialized()`
Returns true when all nodes have been measured:
```ts
const initialized = useNodesInitialized();
```

### `useStore(selector)` / `useStoreApi()`
Low-level Zustand store access — use sparingly:
```ts
const nodeCount = useStore((s) => s.nodes.length);
const store = useStoreApi(); // imperative access
```

---

## 4. Utility Functions

### Edge Path Generators
```ts
// Bezier (default)
const [path, labelX, labelY, offsetX, offsetY] = getBezierPath({
  sourceX, sourceY, sourcePosition,
  targetX, targetY, targetPosition,
  curvature?: number,      // default 0.25
});

// Smooth Step
const [path, labelX, labelY] = getSmoothStepPath({
  sourceX, sourceY, sourcePosition,
  targetX, targetY, targetPosition,
  borderRadius?: number,   // default 5
  offset?: number,
});

// Step
const [path, labelX, labelY] = getStepPath({ ... });

// Straight
const [path, labelX, labelY] = getStraightPath({ sourceX, sourceY, targetX, targetY });

// Simple Bezier
const [path, labelX, labelY] = getSimpleBezierPath({ ... });
```

### Node/Edge Manipulation
```ts
// Apply changes from onNodesChange / onEdgesChange
applyNodeChanges(changes, nodes): Node[]
applyEdgeChanges(changes, edges): Edge[]

// Add edge safely (prevents duplicates)
addEdge(connection, edges): Edge[]

// Reconnect an existing edge
reconnectEdge(oldEdge, newConnection, edges): Edge[]
```

### Graph Traversal
```ts
getIncomers(node, nodes, edges): Node[]
getOutgoers(node, nodes, edges): Node[]
getConnectedEdges(nodes, edges): Edge[]
```

### Bounds & Viewport
```ts
// Get bounding box of nodes — accepts Node[], InternalNode[], string[] (ids), or mixed
getNodesBounds(nodes: (Node | InternalNode | string)[]): Rect

// Calculate viewport to fit given bounds
getViewportForBounds(
  bounds: Rect,
  width: number,
  height: number,
  minZoom: number,
  maxZoom: number,
  padding?: number
): Viewport
```

### Type Guards
```ts
isNode(element): boolean
isEdge(element): boolean
```

---

## 5. Key Types

### Node
```ts
type Node<T = Record<string, unknown>> = {
  id: string;
  type?: string;
  position: { x: number; y: number };
  data: T;
  // Optional sizing (v12: define upfront for SSR)
  width?: number;
  height?: number;
  // Optional
  style?: CSSProperties;
  className?: string;
  selected?: boolean;
  draggable?: boolean;
  connectable?: boolean;
  deletable?: boolean;
  selectable?: boolean;
  hidden?: boolean;
  parentId?: string;        // for sub-flows
  extent?: 'parent' | CoordinateExtent;
  expandParent?: boolean;
  sourcePosition?: Position;
  targetPosition?: Position;
  zIndex?: number;
  origin?: [number, number];
  handles?: NodeHandle[];   // v12 SSR handles
  // Set by library
  measured?: { width?: number; height?: number };
};
```

### Edge
```ts
type Edge<T = Record<string, unknown>> = {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string | null;
  targetHandle?: string | null;
  type?: string;             // 'default'|'straight'|'step'|'smoothstep'|'simplebezier'
  data?: T;
  animated?: boolean;
  selected?: boolean;
  hidden?: boolean;
  deletable?: boolean;
  selectable?: boolean;
  focusable?: boolean;
  reconnectable?: boolean | HandleType;
  style?: CSSProperties;
  className?: string;
  label?: ReactNode;
  labelStyle?: CSSProperties;
  markerStart?: EdgeMarkerType;
  markerEnd?: EdgeMarkerType;
  zIndex?: number;
};
```

### NodeProps (custom node component)
```ts
type NodeProps<NodeType extends Node = Node> = {
  id: string;
  type: string;
  data: NodeType['data'];
  selected: boolean;
  dragging: boolean;
  isConnectable: boolean;
  positionAbsoluteX: number;
  positionAbsoluteY: number;
  width?: number;
  height?: number;
  // ...
};
```

### EdgeProps (custom edge component)
```ts
type EdgeProps<EdgeType extends Edge = Edge> = {
  id: string;
  source: string;
  target: string;
  sourceX: number; sourceY: number;
  targetX: number; targetY: number;
  sourcePosition: Position;
  targetPosition: Position;
  data?: EdgeType['data'];
  selected?: boolean;
  animated?: boolean;
  markerStart?: string;
  markerEnd?: string;
  style?: CSSProperties;
  // ...
};
```

### Connection
```ts
type Connection = {
  source: string;
  target: string;
  sourceHandle: string | null;
  targetHandle: string | null;
};
```

### Viewport
```ts
type Viewport = { x: number; y: number; zoom: number };
```

### Position (enum)
```ts
enum Position { Left = 'left', Top = 'top', Right = 'right', Bottom = 'bottom' }
```

### ConnectionLineComponentProps
```ts
// Props passed to your connectionLineComponent SVG element
type ConnectionLineComponentProps<NodeType extends Node = Node> = {
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
  fromPosition: Position;
  toPosition: Position;
  /** 'valid'|'invalid' only when isValidConnection is set; otherwise null */
  connectionStatus: 'valid' | 'invalid' | null;
  fromNode: InternalNode<NodeType>;       // always defined
  toNode: InternalNode<NodeType> | null;  // null while dragging in empty space
  fromHandle: Handle;
  toHandle: Handle | null;
  pointer: XYPosition;                    // current mouse in flow coords
  connectionLineStyle?: CSSProperties;
  connectionLineType: ConnectionLineType;
};
```

### OnReconnect
```ts
type OnReconnect<E extends Edge = Edge> = (oldEdge: E, newConnection: Connection) => void;

// onReconnectStart: (event: ReactMouseEvent, edge: E, handleType: HandleType) => void
// onReconnectEnd:   (event: MouseEvent|TouchEvent, edge: E, handleType: HandleType, connectionState: FinalConnectionState) => void
// Wire up:
<ReactFlow
  onReconnect={(oldEdge, newConn) => setEdges((eds) => reconnectEdge(oldEdge, newConn, eds))}
  onReconnectStart={(event, edge, handleType) => { /* drag started */ }}
  onReconnectEnd={(event, edge, handleType, connectionState) => { /* connectionState.isValid */ }}
/>
```

### OnBeforeDelete
```ts
// Returns Promise (always async). Return false to cancel, or { nodes, edges } to filter what deletes.
type OnBeforeDelete<N extends Node = Node, E extends Edge = Edge> = (
  params: { nodes: N[]; edges: E[] }
) => Promise<boolean | { nodes: N[]; edges: E[] }>;
```

### ZIndexMode (v12)
```ts
type ZIndexMode = 'auto' | 'basic' | 'manual';
// 'basic'  (default) — raises z-index for selections only
// 'auto'             — raises z-index for selections AND sub-flows (recommended with parentId nodes)
// 'manual'           — no automatic z-index management
<ReactFlow zIndexMode="auto" ... />
```

### MarkerType
```ts
enum MarkerType { Arrow = 'arrow', ArrowClosed = 'arrowclosed' }
```

### Edge marker usage
```ts
edge.markerEnd = { type: MarkerType.ArrowClosed, color: '#555', width: 20, height: 20 };
// or string ref:
edge.markerEnd = 'url(#my-custom-marker)';
```
