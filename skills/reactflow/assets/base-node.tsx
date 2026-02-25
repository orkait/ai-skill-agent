// assets/base-node.tsx
// Production-ready base node for React Flow v12
// Stack: @xyflow/react v12 + Tailwind + shadcn/ui + lucide-react
//
// Usage:
//   1. Copy this file to components/nodes/BaseNode.tsx
//   2. Register: const nodeTypes = { base: BaseNode }
//   3. Create nodes: { id: '1', type: 'base', position: {x:0,y:0}, data: { label: 'My Node' } }

import { memo, type ReactNode } from 'react';
import {
  Handle,
  Position,
  NodeToolbar,
  useReactFlow,
  type NodeProps,
  type Node,
} from '@xyflow/react';
import { cn } from '@/lib/utils';
import { Trash2, Copy } from 'lucide-react';

// ──────────────────────────────────────────────
// Types
// ──────────────────────────────────────────────

export type BaseNodeData = {
  /** Display label shown in the node */
  label: string;
  /** Optional subtitle / description */
  description?: string;
  /** Optional icon rendered left of label */
  icon?: ReactNode;
  /** Optional badge text (e.g. type indicator) */
  badge?: string;
  /** Optional header color class (e.g. 'bg-blue-500') */
  headerColor?: string;
  /** Whether source/target handles are shown */
  hasTarget?: boolean;
  hasSource?: boolean;
};

export type FlowBaseNode = Node<BaseNodeData>;

// ──────────────────────────────────────────────
// Component
// ──────────────────────────────────────────────

export const BaseNode = memo(function BaseNode({
  id,
  data,
  selected,
  isConnectable,
}: NodeProps<FlowBaseNode>) {
  const { deleteElements, addNodes, getNode } = useReactFlow();
  const hasTarget = data.hasTarget ?? true;
  const hasSource = data.hasSource ?? true;

  const handleDelete = () => deleteElements({ nodes: [{ id }] });

  const handleDuplicate = () => {
    const node = getNode(id);
    if (!node) return;
    addNodes({
      ...node,
      id: `${id}-copy-${Date.now()}`,
      selected: false,
      position: {
        x: node.position.x + 20,
        y: node.position.y + 20,
      },
    });
  };

  return (
    <>
      {/* Toolbar (visible when selected) */}
      <NodeToolbar
        isVisible={selected}
        position={Position.Top}
        className="flex gap-1 bg-background rounded-md border shadow-sm p-1"
      >
        <button
          onClick={handleDuplicate}
          className="p-1 rounded hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
          title="Duplicate"
        >
          <Copy className="h-3.5 w-3.5" />
        </button>
        <div className="w-px bg-border" />
        <button
          onClick={handleDelete}
          className="p-1 rounded hover:bg-destructive hover:text-destructive-foreground transition-colors text-muted-foreground"
          title="Delete"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </NodeToolbar>

      {/* Node body */}
      <div
        className={cn(
          'rounded-lg border bg-card shadow-sm overflow-hidden',
          'min-w-[160px] max-w-[280px]',
          'transition-all duration-100',
          selected
            ? 'border-primary shadow-md ring-1 ring-primary/20'
            : 'border-border hover:border-muted-foreground/60',
        )}
      >
        {/* Optional color header stripe */}
        {data.headerColor && (
          <div className={cn('h-1 w-full', data.headerColor)} />
        )}

        {/* Content */}
        <div className="px-3 py-2.5 flex items-start gap-2">
          {/* Icon */}
          {data.icon && (
            <span className="mt-0.5 flex-shrink-0 text-muted-foreground">
              {data.icon}
            </span>
          )}

          {/* Text */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium truncate leading-tight">
                {data.label}
              </p>
              {data.badge && (
                <span className="flex-shrink-0 rounded-sm bg-muted px-1 py-0.5 text-[10px] font-mono text-muted-foreground">
                  {data.badge}
                </span>
              )}
            </div>
            {data.description && (
              <p className="text-xs text-muted-foreground mt-0.5 leading-snug">
                {data.description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Handles */}
      {hasTarget && (
        <Handle
          type="target"
          position={Position.Left}
          isConnectable={isConnectable}
          className={cn(
            '!w-3 !h-3 !rounded-full',
            '!bg-background !border-2',
            selected ? '!border-primary' : '!border-muted-foreground',
            'hover:!border-primary hover:!bg-primary/10 transition-colors',
          )}
        />
      )}
      {hasSource && (
        <Handle
          type="source"
          position={Position.Right}
          isConnectable={isConnectable}
          className={cn(
            '!w-3 !h-3 !rounded-full',
            '!bg-background !border-2',
            selected ? '!border-primary' : '!border-muted-foreground',
            'hover:!border-primary hover:!bg-primary/10 transition-colors',
          )}
        />
      )}
    </>
  );
});

BaseNode.displayName = 'BaseNode';
