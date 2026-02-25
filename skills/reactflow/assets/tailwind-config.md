# Tailwind + React Flow v12 Integration

## Setup

### 1. tailwind.config.js
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './src/**/*.{ts,tsx,js,jsx}',
    // Include React Flow source to purge its classes if you use them
    './node_modules/@xyflow/react/**/*.js',
  ],
  theme: {
    extend: {
      // Map React Flow CSS vars to shadcn/ui theme
    },
  },
};
```

### 2. Required CSS import (app entry)
```ts
// app/layout.tsx or main.tsx — MUST come before your own styles
import '@xyflow/react/dist/style.css';
```

---

## CSS Variable Mapping

Override React Flow's design tokens to match your Tailwind theme.
Add to your global CSS file (after the React Flow import):

```css
/* globals.css */

/* Light mode */
.react-flow {
  --xy-background-color: hsl(var(--background));
  --xy-background-pattern-color: hsl(var(--border));

  --xy-node-background-color: hsl(var(--card));
  --xy-node-border: 1px solid hsl(var(--border));
  --xy-node-border-radius: 8px;
  --xy-node-boxshadow-hover: 0 1px 4px hsl(var(--border));
  --xy-node-boxshadow-selected: 0 0 0 1px hsl(var(--primary));
  --xy-node-color: hsl(var(--card-foreground));

  --xy-edge-stroke: hsl(var(--muted-foreground));
  --xy-edge-stroke-width: 1.5;
  --xy-edge-stroke-selected: hsl(var(--primary));

  --xy-connectionline-stroke: hsl(var(--primary));
  --xy-connectionline-stroke-width: 2;

  --xy-handle-background-color: hsl(var(--background));
  --xy-handle-border-color: hsl(var(--muted-foreground));

  --xy-selection-background-color: hsl(var(--primary) / 0.08);
  --xy-selection-border: 1px solid hsl(var(--primary));

  --xy-controls-button-background-color: hsl(var(--background));
  --xy-controls-button-background-color-hover: hsl(var(--accent));
  --xy-controls-button-color: hsl(var(--foreground));
  --xy-controls-button-color-hover: hsl(var(--accent-foreground));
  --xy-controls-button-border-color: hsl(var(--border));
  --xy-controls-box-shadow: 0 1px 6px hsl(var(--border));

  --xy-minimap-background-color: hsl(var(--muted));
  --xy-minimap-mask-background-color: hsl(var(--background) / 0.8);
  --xy-minimap-node-background-color: hsl(var(--border));
}

/* Dark mode (when .dark class on html) */
.dark .react-flow {
  --xy-background-color: hsl(var(--background));
  --xy-background-pattern-color: hsl(var(--border));
  --xy-node-background-color: hsl(var(--card));
  --xy-node-border: 1px solid hsl(var(--border));
  --xy-edge-stroke: hsl(var(--muted-foreground));
  --xy-selection-background-color: hsl(var(--primary) / 0.15);
  --xy-controls-button-background-color: hsl(var(--card));
  --xy-minimap-background-color: hsl(var(--card));
}
```

---

## Handle Styling with Tailwind

React Flow adds inline styles to handles with `!important`. To override:

```tsx
// Use Tailwind's `!` prefix for important:
<Handle
  type="source"
  position={Position.Right}
  className="!w-3 !h-3 !rounded-full !bg-background !border-2 !border-muted-foreground hover:!border-primary"
/>
```

Or target via CSS:
```css
.react-flow__handle {
  @apply w-3 h-3 rounded-full bg-background border-2 border-muted-foreground;
}
.react-flow__handle:hover,
.react-flow__handle.connecting {
  @apply border-primary;
}
.react-flow__handle.valid {
  @apply border-green-500 bg-green-500/10;
}
```

---

## Preventing pan/drag interference

Use these built-in classes on interactive elements inside nodes:

```tsx
// nodrag — prevents node dragging when clicking this element
// nopan  — prevents viewport panning when clicking this element
// nowheel — prevents zoom when scrolling on this element

<div className="nodrag nopan overflow-auto max-h-32">
  Scrollable content inside node
</div>

<input className="nodrag" type="text" />
<select className="nodrag nopan" />
```

---

## Scroll inside nodes

```tsx
// Scrollable content inside a node
<div
  className="nodrag nopan nowheel overflow-y-auto max-h-48 scrollbar-thin"
  style={{ cursor: 'default' }}
>
  {items.map(item => <div key={item.id}>{item.label}</div>)}
</div>
```

---

## Common Layout Patterns

### Full-page flow editor
```tsx
// parent must have explicit height
<div className="flex h-screen overflow-hidden">
  <Sidebar />
  <main className="flex-1 relative">
    <ReactFlowProvider>
      <ReactFlow ... />
    </ReactFlowProvider>
  </main>
</div>
```

### Flow in a card/modal
```tsx
<Card>
  <CardContent className="p-0">
    <div className="h-[400px] w-full rounded-lg overflow-hidden">
      <ReactFlow ... />
    </div>
  </CardContent>
</Card>
```

### Responsive flow (avoid % heights — use CSS)
```css
/* globals.css */
.flow-container {
  height: calc(100vh - 64px); /* 64px = header height */
}
```

---

## Animation utilities

```css
/* Edge dash animation */
@keyframes dashdraw {
  to { stroke-dashoffset: -20; }
}

/* Node pulse on selection */
@keyframes nodePulse {
  0%, 100% { box-shadow: 0 0 0 0 hsl(var(--primary) / 0.4); }
  50% { box-shadow: 0 0 0 4px hsl(var(--primary) / 0); }
}

.node-selected-pulse {
  animation: nodePulse 1.5s ease-in-out 1;
}
```
