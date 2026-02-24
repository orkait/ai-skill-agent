---
name: lenis-react
description: >-
  Integrate Lenis smooth scrolling into React and Next.js projects. Use when building smooth scrolling,
  scroll-linked animations, parallax effects, GSAP ScrollTrigger sync, Framer Motion sync, programmatic
  scroll-to navigation, or scroll event listeners with `lenis/react`.
compatibility: "Lenis v1+ (`lenis` package), React 16.8+, Next.js 13+ (App Router and Pages Router), Vite, CRA, Node.js 16+"
triggers:
  - lenis
  - lenis react
  - lenis/react
  - smooth scroll
  - gsap scrolltrigger lenis
  - framer motion lenis
  - parallax scroll
  - scrollTo navigation
references:
  - references/patterns/setup-and-integration-rules.md
  - references/validation/accessibility.md
  - references/examples/recipes.md
  - references/examples/full-integration-guide.md
metadata:
  author: "claude"
  version: "1.1"
  package: "lenis"
  react_binding: "lenis/react"
  strict_goal: "brain-only-skill-md"
activation:
  mode: fuzzy
  triggers:
    - lenis
    - smooth scroll react
    - nextjs lenis
    - lenis scrolltrigger
  priority: normal
---

# Lenis React Skill (Brain-Only)

Use this skill for React/Next.js integration of Lenis smooth scrolling. Keep `SKILL.md` focused on invariants and setup rules. Load examples and deep integrations from `references/`.

## Critical Setup Rules

1. Prefer the current package: `lenis` with React bindings from `lenis/react`.
2. Treat `@studio-freight/lenis` and `@studio-freight/react-lenis` as legacy packages unless the project is already pinned to them.
3. Ensure Lenis CSS is included (either import package CSS or apply required global Lenis styles) or scrolling behavior/layout may break.
4. In Next.js, any component using `ReactLenis` or `useLenis` must be a client component.

## Non-Negotiable Integration Invariants

1. For full-page scrolling, use `ReactLenis` with the root/full-page pattern and keep the provider high enough in the tree.
2. If GSAP ScrollTrigger drives the animation loop, disable Lenis auto RAF and use a single RAF driver to prevent desync.
3. Respect `prefers-reduced-motion`; allow skipping Lenis entirely when reduced motion is enabled.
4. For modals/overlays, stop Lenis on open and restart on close when scroll locking is needed.
5. For custom scroll containers, ensure wrapper/content refs are wired correctly and the container has constrained dimensions.

## Performance and UX Landmines

1. Avoid stacking multiple scroll systems (native smooth scroll CSS, another RAF loop, and Lenis) at the same time.
2. Test touch behavior on iOS before enabling touch smoothing-related options.
3. Validate sticky headers and offsets when implementing programmatic `scrollTo` navigation.
4. Confirm keyboard navigation and focus management when programmatically scrolling to sections.

## Reference Loading Guide

1. `references/patterns/setup-and-integration-rules.md` - setup, imports, core options, Next.js/client boundaries, GSAP/Framer integration rules, pitfalls.
2. `references/validation/accessibility.md` - reduced motion and accessibility guidance.
3. `references/examples/recipes.md` - reusable components and recipes (progress bar, modal, parallax, GSAP patterns, etc.).
4. `references/examples/full-integration-guide.md` - original long-form integration guide and examples preserved for deep context.
