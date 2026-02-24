# Lenis React - Setup and Integration Rules

## Package and Imports

- Current package: `lenis`
- React bindings: `lenis/react`
- Prefer:
  - `ReactLenis`
  - `useLenis`
- Legacy packages (`@studio-freight/lenis`, `@studio-freight/react-lenis`) should only be used when the project is already pinned to them.

## Installation and CSS (Required)

- Install `lenis`.
- Include Lenis CSS (package import) or the required global Lenis styles.
- Missing Lenis CSS commonly causes incorrect layout/scroll behavior.

## Full-Page Integration Pattern

- Place the `ReactLenis` provider high in the app tree.
- Use the root/full-page configuration for standard page scrolling.
- Keep provider placement stable so nested components can access `useLenis()` reliably.

## Next.js Rules

- Components using `ReactLenis` or `useLenis` must be client components.
- Keep the provider in a dedicated client wrapper when using App Router layouts.

## Programmatic Scrolling

- Use `lenis.scrollTo(...)` for links, section jumps, and back-to-top buttons.
- Account for sticky header height with an offset.
- Pair scroll with focus management for keyboard/screen-reader users where appropriate.

## GSAP ScrollTrigger Synchronization

- Use a single RAF source.
- When GSAP drives frames, set Lenis auto RAF off and feed Lenis from GSAP's ticker.
- If both run their own loops, scroll positions can drift/desync.

## Framer Motion Synchronization

- If driving Lenis from Framer Motion's frame loop, disable Lenis auto RAF.
- Ensure cleanup removes the frame callback on unmount.

## Custom Scroll Containers

- Use explicit wrapper/content refs for non-root scroll regions.
- Ensure container dimensions and overflow behavior are configured correctly.
- Test nested scroll interactions with modals/drawers.

## Operational Pitfalls Checklist

- Do not combine Lenis with conflicting native CSS smooth scrolling behavior.
- Test touch and wheel behavior across desktop + iOS.
- Stop/start Lenis around scroll-locked overlays.
- Validate reduced-motion handling before release.
