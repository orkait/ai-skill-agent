---
name: reactflow
description: >-
  Build flow-based SaaS UIs using React Flow v12 (@xyflow/react). Use this skill
  whenever the user mentions nodes, edges, flow diagrams, workflow builders,
  pipeline editors, DAGs, canvas UIs, node-based editors, or anything involving
  draggable/connectable components. Also trigger for state management with Zustand
  in a flow context, custom node/edge types, handle connections, layout algorithms
  (dagre/elk), undo/redo in flows, and drag-and-drop onto a canvas.
  Stack: React + Tailwind + shadcn/ui + lucide-icons + Zustand. Free tier only.
metadata:
  author: claude
  version: "1.1.0"
  stack: "@xyflow/react ^12, zustand, tailwindcss, shadcn/ui, lucide-react"
  license: MIT
triggers:
  - react flow
  - nodes and edges
  - flow diagram
  - workflow builder
  - pipeline editor
  - DAG editor
  - canvas UI
  - node-based editor
  - draggable nodes
  - xyflow
  - flow canvas
  - custom nodes
  - zustand flow store
references:
  - references/api/api.md
  - references/patterns/enterprise.md
  - references/patterns/enterprise-advanced.md
  - references/examples/custom-nodes.md
  - references/examples/quickstart.md
activation:
  mode: fuzzy
  triggers:
    - react flow
    - nodes and edges
    - flow diagram
    - workflow builder
    - pipeline editor
    - DAG editor
  priority: high
compatibility: "@xyflow/react ^12"
---

# React Flow v12 — Enterprise SaaS Skill

Build production-grade flow-based UIs with `@xyflow/react` v12.
**Stack: React + Tailwind + shadcn/ui + lucide-icons + Zustand. Free tier only.**

> Reference files:
> - `references/api/api.md` — Full v12 API cheatsheet (components, hooks, utils, types)
> - `references/patterns/enterprise.md` — Enterprise patterns §1-§12 (store design, undo/redo, drag-drop, layout)
> - `references/patterns/enterprise-advanced.md` — Enterprise patterns §13-§16 (subflows, reconnect, connection line)
> - `references/examples/custom-nodes.md` — Custom node & edge cookbook
> - `assets/base-node.tsx` — Base custom node component
> - `references/examples/quickstart.md` — Minimal flow, store pattern, node/edge examples

---

## 1. Setup & Installation

```bash
npm install @xyflow/react zustand
# Already in stack: react, tailwindcss, shadcn/ui, lucide-react
```

**Required CSS** — import once at app root:
```ts
import '@xyflow/react/dist/style.css';
```

**Tailwind integration** — add to `tailwind.config.js`:
```js
content: ['./src/**/*.{ts,tsx}', './node_modules/@xyflow/react/**/*.js']
```

**Key v12 changes from v11:**
- Package: `reactflow` → `@xyflow/react` (named exports, no default)
- Measured dimensions: `node.measured.width` / `node.measured.height` (not `node.width`)
- Rename: `nodeInternals` → `nodeLookup`, `project()` → `screenToFlowPosition()`
- `getEdge()`/`getNode()` return `undefined` not `null` when not found

---

## 2. Key Hooks Quick Reference

| Hook | Use case |
|------|----------|
| `useReactFlow()` | `getNode`, `getEdge`, `setNodes`, `fitView`, `screenToFlowPosition` |
| `useNodesState()` / `useEdgesState()` | Local state (no Zustand needed) |
| `useNodes()` / `useEdges()` | Subscribe to all nodes/edges |
| `useNodesData(ids)` | Subscribe to specific node data (avoids re-renders) |
| `useConnection()` | Active connection line state (`inProgress`, `isValid`, `fromHandle`...) |
| `useNodeId()` | Get current node's ID from inside a custom node |
| `useHandleConnections({type, nodeId, id})` | Connections on a specific handle |
| `useNodeConnections({type})` | All connections on current node |
| `useViewport()` | Current viewport {x, y, zoom} |
| `useUpdateNodeInternals()` | Call after changing handles programmatically |
| `useInternalNode(id)` | InternalNode with `internals.positionAbsolute`, `measured` |
| `useNodesInitialized()` | True once all nodes have been measured |

---

## 3. Critical Rules

- Always wrap in `<ReactFlowProvider>` when using hooks outside `<ReactFlow>`
- Define `nodeTypes` / `edgeTypes` **outside** components (or `useMemo`) — never inline
- Use `memo()` on custom node/edge components
- `node.measured.width/height` — read-only, set by library after render
- `InternalNode.internals.positionAbsolute` — absolute canvas coords (not `positionAbsoluteX/Y` on `NodeProps`)
- `deleteElements()` is async → returns `Promise<{deletedNodes, deletedEdges}>`
- `onBeforeDelete` must return a `Promise` (always async)
- Use `zIndexMode="auto"` on `<ReactFlow>` when using `parentId` sub-flows
- `connectionStatus` in `ConnectionLineComponentProps` is only non-null when `isValidConnection` is provided
- Remove attribution: `<ReactFlow proOptions={{ hideAttribution: true }} />`

---

## Quick Decision Guide

| Need | Solution |
|------|----------|
| Simple local state | `useNodesState` + `useEdgesState` |
| Shared state across components | Zustand store (see `assets/store-template.ts`) |
| Undo/redo | `zundo` temporal middleware |
| Auto-layout | `@dagrejs/dagre` or `elkjs` |
| Auto-layout on first render | `useNodesInitialized` + layout in `useEffect` (patterns §16) |
| Multiple handle types | Named handles with `id` prop |
| Resize nodes | `<NodeResizer />` component |
| Context menu | `onNodeContextMenu` + shadcn `DropdownMenu` |
| Minimap custom colors | `nodeColor` / `nodeStrokeColor` on `<MiniMap />` |
| Prevent cycles | `isValidConnection` + `getIncomers` |
| SSR/SSG | Set `width`/`height` on nodes; use `ReactFlowProvider` |
| Group / sub-flow containment | `parentId` + `extent: 'parent'` + `zIndexMode="auto"` (patterns §13) |
| Reconnect existing edge | `reconnectEdge` + `onReconnect` (patterns §14) |
| Custom drag connection line | `connectionLineComponent` prop (patterns §15) |
| Confirm valid drop target visually | `useConnection()` inside nodes — `inProgress`, `isValid` |
| Source-only / target-only nodes | Built-in `type: 'input'`/`type: 'output'`, or custom (custom-nodes §11) |
| Cancel deletion | `onBeforeDelete` — return `Promise<false>` |
| Update node without full re-render | `updateNodeData(id, partialData)` from `useReactFlow()` |
| Floating edges | `useInternalNode` + `internals.positionAbsolute` (custom-nodes §9) |

See `references/patterns/enterprise.md` for enterprise patterns §1-§12.
See `references/patterns/enterprise-advanced.md` for patterns §13-§16.
See `references/examples/quickstart.md` for code examples (minimal flow, store, drag-drop, layout).
