# Custom Nodes & Edges Cookbook

## Table of Contents
1. [Base Custom Node](#1-base-custom-node)
2. [Node with Multiple Handles](#2-node-with-multiple-handles)
3. [Node with Status Indicator](#3-node-with-status-indicator)
4. [Node with NodeToolbar](#4-node-with-nodetoolbar)
5. [Resizable Node](#5-resizable-node)
6. [Group/Container Node](#6-groupcontainer-node)
7. [Custom Edge](#7-custom-edge)
8. [Edge with Delete Button](#8-edge-with-delete-button)
9. [Floating Edge](#9-floating-edge)
10. [Animated Edge](#10-animated-edge)

---

## 1. Base Custom Node

```tsx
// components/nodes/BaseNode.tsx
import { memo } from 'react';
import { Handle, Position, type NodeProps, type Node } from '@xyflow/react';
import { cn } from '@/lib/utils';

type BaseNodeData = {
  label: string;
  description?: string;
  icon?: React.ReactNode;
};

export const BaseNode = memo(function BaseNode({
  data,
  selected,
  isConnectable,
}: NodeProps<Node<BaseNodeData>>) {
  return (
    <div
      className={cn(
        'relative rounded-lg border bg-card shadow-sm',
        'min-w-[160px] max-w-[280px]',
        'transition-all duration-100',
        selected
          ? 'border-primary shadow-md ring-1 ring-primary/30'
          : 'border-border hover:border-muted-foreground'
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={isConnectable}
        className="!w-3 !h-3 !bg-muted-foreground hover:!bg-primary !border-2 !border-background"
      />

      <div className="flex items-center gap-2 px-3 py-2">
        {data.icon && (
          <span className="text-muted-foreground flex-shrink-0">{data.icon}</span>
        )}
        <div className="min-w-0">
          <p className="text-sm font-medium truncate">{data.label}</p>
          {data.description && (
            <p className="text-xs text-muted-foreground truncate">{data.description}</p>
          )}
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
        className="!w-3 !h-3 !bg-muted-foreground hover:!bg-primary !border-2 !border-background"
      />
    </div>
  );
});
```

---

## 2. Node with Multiple Handles

```tsx
// components/nodes/MultiHandleNode.tsx
import { Handle, Position, useHandleConnections, type NodeProps, type Node } from '@xyflow/react';

type MultiHandleData = {
  label: string;
  inputs: string[];   // e.g. ['data', 'config']
  outputs: string[];  // e.g. ['result', 'error']
};

export const MultiHandleNode = memo(function MultiHandleNode({
  data, selected, isConnectable,
}: NodeProps<Node<MultiHandleData>>) {
  const HANDLE_HEIGHT = 28;
  const headerHeight = 40;

  return (
    <div
      className={cn(
        'rounded-lg border bg-card shadow-sm',
        selected && 'ring-1 ring-primary border-primary'
      )}
      style={{
        minHeight: Math.max(data.inputs.length, data.outputs.length) * HANDLE_HEIGHT + headerHeight,
        width: 200,
      }}
    >
      {/* Header */}
      <div className="px-3 py-2 border-b">
        <p className="text-sm font-semibold">{data.label}</p>
      </div>

      {/* Body with handles */}
      <div className="relative flex justify-between px-2 py-2">
        {/* Inputs */}
        <div className="flex flex-col gap-1">
          {data.inputs.map((input, i) => (
            <div key={input} className="flex items-center gap-1 relative" style={{ height: HANDLE_HEIGHT }}>
              <Handle
                type="target"
                position={Position.Left}
                id={`input-${input}`}
                isConnectable={isConnectable}
                style={{ top: headerHeight + i * HANDLE_HEIGHT + HANDLE_HEIGHT / 2 }}
                className="!static !transform-none !w-2.5 !h-2.5 !relative !bg-blue-400"
              />
              <span className="text-xs text-muted-foreground">{input}</span>
            </div>
          ))}
        </div>

        {/* Outputs */}
        <div className="flex flex-col gap-1 items-end">
          {data.outputs.map((output, i) => (
            <div key={output} className="flex items-center gap-1 relative" style={{ height: HANDLE_HEIGHT }}>
              <span className="text-xs text-muted-foreground">{output}</span>
              <Handle
                type="source"
                position={Position.Right}
                id={`output-${output}`}
                isConnectable={isConnectable}
                style={{ top: headerHeight + i * HANDLE_HEIGHT + HANDLE_HEIGHT / 2 }}
                className="!static !transform-none !w-2.5 !h-2.5 !bg-green-400"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});
```

**Important**: When handle positions change dynamically, call:
```ts
const updateNodeInternals = useUpdateNodeInternals();
useEffect(() => { updateNodeInternals(id); }, [data.inputs, data.outputs]);
```

---

## 3. Node with Status Indicator

```tsx
const STATUS_CONFIG = {
  idle:    { color: 'bg-muted',    label: 'Idle',    icon: Circle },
  running: { color: 'bg-blue-500', label: 'Running', icon: Loader2 },
  done:    { color: 'bg-green-500',label: 'Done',    icon: CheckCircle2 },
  error:   { color: 'bg-red-500',  label: 'Error',   icon: XCircle },
} as const;

type Status = keyof typeof STATUS_CONFIG;

type StatusNodeData = { label: string; status: Status };

export const StatusNode = memo(function StatusNode({
  data, selected,
}: NodeProps<Node<StatusNodeData>>) {
  const { color, icon: StatusIcon } = STATUS_CONFIG[data.status ?? 'idle'];

  return (
    <div className={cn('rounded-lg border bg-card shadow-sm p-3 min-w-[180px]', selected && 'ring-1 ring-primary border-primary')}>
      <Handle type="target" position={Position.Left} />
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">{data.label}</p>
        <div className={cn('rounded-full p-0.5', color)}>
          <StatusIcon className={cn('h-3.5 w-3.5 text-white', data.status === 'running' && 'animate-spin')} />
        </div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
});
```

---

## 4. Node with NodeToolbar

```tsx
import { NodeToolbar, Position } from '@xyflow/react';
import { Trash2, Copy, Settings } from 'lucide-react';

export const ToolbarNode = memo(function ToolbarNode({
  id, data, selected,
}: NodeProps<Node<{ label: string }>>) {
  const { deleteElements } = useReactFlow();

  return (
    <>
      <NodeToolbar isVisible={selected} position={Position.Top} className="flex gap-1">
        <button
          className="p-1 rounded bg-background border shadow-sm hover:bg-destructive hover:text-destructive-foreground transition-colors"
          onClick={() => deleteElements({ nodes: [{ id }] })}
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
        <button className="p-1 rounded bg-background border shadow-sm hover:bg-accent transition-colors">
          <Copy className="h-3.5 w-3.5" />
        </button>
        <button className="p-1 rounded bg-background border shadow-sm hover:bg-accent transition-colors">
          <Settings className="h-3.5 w-3.5" />
        </button>
      </NodeToolbar>

      <div className={cn('rounded-lg border bg-card p-3 min-w-[160px]', selected && 'border-primary ring-1 ring-primary/20')}>
        <Handle type="target" position={Position.Left} />
        <p className="text-sm font-medium">{data.label}</p>
        <Handle type="source" position={Position.Right} />
      </div>
    </>
  );
});
```

---

## 5. Resizable Node

```tsx
import { NodeResizer } from '@xyflow/react';

type ResizableNodeData = { label: string };

export const ResizableNode = memo(function ResizableNode({
  data, selected,
}: NodeProps<Node<ResizableNodeData>>) {
  return (
    <div className={cn('w-full h-full rounded-lg border bg-card p-3', selected && 'border-primary ring-1 ring-primary/20')}>
      <NodeResizer
        isVisible={selected}
        minWidth={120}
        minHeight={50}
        lineClassName="!border-primary"
        handleClassName="!w-3 !h-3 !bg-background !border-2 !border-primary rounded-sm"
      />
      <Handle type="target" position={Position.Left} />
      <p className="text-sm font-medium">{data.label}</p>
      <Handle type="source" position={Position.Right} />
    </div>
  );
});
```

---

## 6. Group/Container Node

```tsx
// Parent node — children use parentId
export const GroupNode = memo(function GroupNode({
  data, selected,
}: NodeProps<Node<{ label: string }>>) {
  return (
    <div
      className={cn(
        'rounded-xl border-2 border-dashed bg-muted/30',
        selected ? 'border-primary' : 'border-muted-foreground/30'
      )}
      style={{ width: '100%', height: '100%' }}
    >
      {/* Group label in top-left */}
      <div className="px-3 py-1.5">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {data.label}
        </p>
      </div>
    </div>
  );
});

// Create a child node inside a group:
const childNode: Node = {
  id: 'child-1',
  type: 'base',
  position: { x: 40, y: 60 },  // relative to parent
  data: { label: 'Child Node' },
  parentId: 'group-1',
  extent: 'parent',            // constrain to parent bounds
};
```

---

## 7. Custom Edge

```tsx
import {
  BaseEdge, EdgeLabelRenderer,
  getBezierPath, type EdgeProps, type Edge,
} from '@xyflow/react';

type CustomEdgeData = { label?: string };

export function CustomEdge({
  id, sourceX, sourceY, targetX, targetY,
  sourcePosition, targetPosition,
  data, selected, markerEnd, style,
}: EdgeProps<Edge<CustomEdgeData>>) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition,
  });

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: selected ? 2.5 : 1.5,
          stroke: selected ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))',
        }}
      />
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            style={{
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            }}
            className="absolute px-2 py-0.5 rounded text-xs bg-background border shadow-sm nodrag nopan"
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
```

---

## 8. Edge with Delete Button

```tsx
export function DeletableEdge({
  id, sourceX, sourceY, targetX, targetY,
  sourcePosition, targetPosition, selected,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition,
  });
  const { deleteElements } = useReactFlow();

  return (
    <>
      <BaseEdge path={edgePath} />
      {selected && (
        <EdgeLabelRenderer>
          <button
            style={{
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            }}
            className="absolute w-5 h-5 flex items-center justify-center rounded-full bg-destructive text-destructive-foreground shadow-sm nodrag nopan hover:scale-110 transition-transform"
            onClick={() => deleteElements({ edges: [{ id }] })}
          >
            <X className="h-3 w-3" />
          </button>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
```

---

## 9. Floating Edge

For edges that connect to the nearest point on the node border:

```tsx
// lib/floating-edge.ts
import {
  type InternalNode, Position, type XYPosition,
  useInternalNode, getBezierPath, BaseEdge, type EdgeProps,
} from '@xyflow/react';

// InternalNode exposes internals.positionAbsolute (absolute canvas coords)
function getNodeCenter(node: InternalNode): XYPosition {
  return {
    x: node.internals.positionAbsolute.x + (node.measured?.width ?? 0) / 2,
    y: node.internals.positionAbsolute.y + (node.measured?.height ?? 0) / 2,
  };
}

function getEdgeParams(source: InternalNode, target: InternalNode) {
  const sc = getNodeCenter(source);
  const tc = getNodeCenter(target);
  const dx = tc.x - sc.x;
  const dy = tc.y - sc.y;
  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);

  // Simple: pick closest axis
  let sx = sc.x, sy = sc.y, tx = tc.x, ty = tc.y;
  let sp = Position.Right, tp = Position.Left;

  if (absDx > absDy) {
    if (dx > 0) { sx += (source.measured?.width ?? 0) / 2; tx -= (target.measured?.width ?? 0) / 2; sp = Position.Right; tp = Position.Left; }
    else { sx -= (source.measured?.width ?? 0) / 2; tx += (target.measured?.width ?? 0) / 2; sp = Position.Left; tp = Position.Right; }
  } else {
    if (dy > 0) { sy += (source.measured?.height ?? 0) / 2; ty -= (target.measured?.height ?? 0) / 2; sp = Position.Bottom; tp = Position.Top; }
    else { sy -= (source.measured?.height ?? 0) / 2; ty += (target.measured?.height ?? 0) / 2; sp = Position.Top; tp = Position.Bottom; }
  }

  return { sx, sy, tx, ty, sp, tp };
}

export function FloatingEdge({ id, source, target, markerEnd, style }: EdgeProps) {
  const sourceNode = useInternalNode(source);
  const targetNode = useInternalNode(target);
  if (!sourceNode || !targetNode) return null;

  const { sx, sy, tx, ty, sp, tp } = getEdgeParams(sourceNode, targetNode);
  const [path] = getBezierPath({ sourceX: sx, sourceY: sy, sourcePosition: sp, targetX: tx, targetY: ty, targetPosition: tp });

  return <BaseEdge id={id} path={path} markerEnd={markerEnd} style={style} />;
}
```

---

## 10. Animated Edge

```tsx
// CSS-animated SVG path
export function AnimatedEdge(props: EdgeProps) {
  const [edgePath] = getBezierPath({ ... });
  
  return (
    <>
      {/* Base edge */}
      <BaseEdge path={edgePath} style={{ stroke: '#94a3b8', strokeWidth: 2 }} />
      {/* Animated overlay */}
      <path
        d={edgePath}
        fill="none"
        stroke="hsl(var(--primary))"
        strokeWidth={2}
        strokeDasharray="8 4"
        className="react-flow__edge-path"
        style={{ animation: 'dashdraw 0.5s linear infinite' }}
      />
    </>
  );
}

// CSS (global):
// @keyframes dashdraw { to { stroke-dashoffset: -12; } }
```

---

## 11. Terminal Nodes (Input / Output)

> **Note**: React Flow v12 has built-in `type: 'input'` (source-only), `type: 'output'` (target-only), and `type: 'group'` nodes. Use these for quick prototyping — build custom terminal nodes only when you need custom styling or data:

Flow entry and exit nodes — source-only and target-only custom implementations:

```tsx
// components/nodes/InputNode.tsx — start of flow, source handle only
export const InputNode = memo(function InputNode({
  data, selected,
}: NodeProps<Node<{ label: string }>>) {
  return (
    <div className={cn(
      'rounded-full border-2 bg-primary text-primary-foreground',
      'px-4 py-2 text-sm font-semibold text-center min-w-[100px]',
      selected && 'ring-2 ring-offset-2 ring-primary',
    )}>
      {data.label}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-primary-foreground !border-2 !border-primary"
      />
    </div>
  );
});

// components/nodes/OutputNode.tsx — end of flow, target handle only
export const OutputNode = memo(function OutputNode({
  data, selected,
}: NodeProps<Node<{ label: string; status?: 'pending' | 'success' | 'error' }>>) {
  const statusClass = {
    pending: 'border-muted-foreground',
    success: 'border-green-500 bg-green-50 dark:bg-green-950',
    error: 'border-red-500 bg-red-50 dark:bg-red-950',
  }[data.status ?? 'pending'];

  return (
    <div className={cn(
      'rounded-full border-2 bg-card',
      'px-4 py-2 text-sm font-semibold text-center min-w-[100px]',
      statusClass,
      selected && 'ring-2 ring-offset-2 ring-primary',
    )}>
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-card !border-2 !border-muted-foreground"
      />
      {data.label}
    </div>
  );
});
```

**Register:**
```ts
export const nodeTypes = {
  input: InputNode,     // source-only
  output: OutputNode,   // target-only
  base: BaseNode,       // both handles
};
```

---

## Node Registration Pattern

```ts
// nodeTypes.ts — define at module scope, never inside component
import { BaseNode } from './nodes/BaseNode';
import { MultiHandleNode } from './nodes/MultiHandleNode';
import { StatusNode } from './nodes/StatusNode';
import { GroupNode } from './nodes/GroupNode';

export const nodeTypes = {
  base: BaseNode,
  multiHandle: MultiHandleNode,
  status: StatusNode,
  group: GroupNode,
} as const;

export type FlowNodeType = keyof typeof nodeTypes;

// edgeTypes.ts
import { CustomEdge } from './edges/CustomEdge';
import { DeletableEdge } from './edges/DeletableEdge';

export const edgeTypes = {
  custom: CustomEdge,
  deletable: DeletableEdge,
} as const;
```

## Tailwind Handle Styling Notes

React Flow handles use `!important` internally. To override with Tailwind, use the `!` prefix:
```tsx
className="!w-3 !h-3 !bg-primary !border-2 !border-background"
```

To style on hover:
```css
.react-flow__handle:hover {
  @apply !bg-primary !scale-125;
}
```
