---
name: reactflow-v12
description: >-
  Build and maintain flow-based UIs with React Flow v12 using @xyflow/react (FREE version).
  Use for node editors, workflow builders, pipeline designers, DAG editors, visual builders,
  custom nodes/edges, viewport control, serialization, and production React Flow architecture.
triggers:
  - react flow
  - "@xyflow/react"
  - node editor
  - workflow builder
  - pipeline builder
  - dag editor
  - visual flow
  - custom nodes
  - custom edges
  - flow serialization
references:
  - references/migration/v11-to-v12-imports-and-breaking-changes.md
  - references/architecture/production-zustand-store-and-shell.md
  - references/examples/custom-nodes-edges-and-core-workflows.md
  - references/api/reactflow-component-and-components.md
  - references/hooks/reactflow-hooks.md
  - references/types/reactflow-types-and-utilities.md
  - references/patterns/editor-interactions.md
  - references/patterns/layout-grouping-and-validation.md
  - references/patterns/persistence-theming-testing-and-collab.md
metadata:
  package: "@xyflow/react"
  compatibility:
    reactflow: ">=12.0.0 <13.0.0"
    coverage: "Free version only (no Pro-only APIs/patterns)"
  stack:
    - React
    - Zustand
    - Tailwind CSS
    - shadcn/ui
    - Lucide Icons
  source_ref: "C:/skills/@ref"
  skill_version: "1.0.0"
activation:
  mode: fuzzy
  triggers:
    - react flow
    - xyflow
    - flow canvas
    - workflow editor
    - node graph UI
  priority: high
---

# React Flow v12 Skill (Progressive Disclosure)

Use this skill for production React Flow v12 work. Keep `SKILL.md` for invariants only. Load reference files only as needed.

## Critical Setup Rules

1. Install and import v12 only: use `@xyflow/react` (not `reactflow`).
2. Use named imports only: `import { ReactFlow, ... } from '@xyflow/react'` (no default `ReactFlow` import).
3. Import styles from `@xyflow/react/dist/style.css` (or `@xyflow/react/dist/base.css` for custom theming).
4. Treat this skill as `@xyflow/react` v12-only (`>=12.0.0 <13.0.0`). If the project is v11, load the migration reference first.
5. Use immutable node/edge updates only. Do not mutate node or edge objects in place.

## Non-Negotiable v12 Breaking Changes

1. Package rename: `reactflow` -> `@xyflow/react`.
2. `ReactFlow` is a named export, not a default export.
3. Read measured dimensions from `node.measured?.width` / `node.measured?.height`.
4. `node.width` / `node.height` are for fixed dimensions, not measured dimensions.
5. Use `parentId` (not `parentNode`).
6. Use `onReconnect`, `reconnectEdge`, and `edgesReconnectable` (not `onEdgeUpdate`, `updateEdge`, `edgesUpdatable`).
7. Use `positionAbsoluteX` / `positionAbsoluteY` in custom node props (not `xPos` / `yPos`).
8. Use `nodeLookup` in internal store selectors (not `nodeInternals`).
9. Use `screenToFlowPosition` (not `project`) for screen-to-canvas coordinates.
10. Call `getNodesBounds(nodes, { nodeOrigin })` with an options object.
11. Model custom nodes as a typed union (`type AppNode = ...`) for TypeScript safety.

## Required Architecture Mandates (Production SaaS)

1. Use a dedicated Zustand store for production state (`nodes`, `edges`, and flow actions). Avoid `useNodesState` / `useEdgesState` except for prototypes.
2. Wrap the editor with `ReactFlowProvider` whenever hooks are used outside the `<ReactFlow />` subtree.
3. Define `nodeTypes`, `edgeTypes`, and `defaultEdgeOptions` outside React components to avoid re-render loops.
4. Memoize all custom node and edge components.
5. Keep event handlers passed to `<ReactFlow />` stable (`useCallback` or equivalent stable references).
6. Centralize serialization (`toObject`, restore, viewport restore) in store/actions or dedicated modules.

## Performance Landmines

1. Do not use `useNodes()` / `useEdges()` inside custom nodes; they trigger broad re-renders.
2. Prefer `useNodesData`, `useHandleConnections`, or `useStore` selectors for targeted subscriptions.
3. Avoid broad Zustand subscriptions in render; select only needed slices.
4. For large graphs, batch state updates and keep node/edge registries stable.
5. Run layout only after nodes are measured when the algorithm depends on dimensions.

## Security and Data Integrity Invariants

1. Treat serialized flow JSON from clients as untrusted input; validate node/edge schemas server-side before persistence.
2. Do not assume client-provided IDs are safe or unique across tenants; normalize or regenerate IDs in backend workflows.
3. Enforce authorization on flow read/write endpoints independently of front-end visibility controls.

## Reference Loading Guide

1. Migration/import fixes: `references/migration/v11-to-v12-imports-and-breaking-changes.md`
2. Production store/editor shell structure: `references/architecture/production-zustand-store-and-shell.md`
3. Custom nodes/edges and core workflows: `references/examples/custom-nodes-edges-and-core-workflows.md`
4. API props and built-in components: `references/api/reactflow-component-and-components.md`
5. Hooks: `references/hooks/reactflow-hooks.md`
6. Types and utilities: `references/types/reactflow-types-and-utilities.md`
7. Editor interaction patterns (undo/redo, copy/paste, context menus): `references/patterns/editor-interactions.md`
8. Layout/grouping/validation: `references/patterns/layout-grouping-and-validation.md`
9. Persistence/theming/testing/collaboration: `references/patterns/persistence-theming-testing-and-collab.md`
