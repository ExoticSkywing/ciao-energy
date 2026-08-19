# iPhone Showcase MVP

This release replaces the CIAO Energy can actors with iPhone mockups while preserving the original CIAO carousel, drag, arrow, scroll timeline, camera, pedestal, and Hero-to-downstream choreography.

## Current interaction contract

- Desktop keeps 24 canonical product slots; mobile keeps 12.
- The source Three.js actors remain the only motion owners.
- DOM iPhone shells are read-only projections of each actor's world transform.
- C-position emphasis and Hero-to-Profile size adaptation are continuously interpolated from source-owned values.
- Profile and Benefit copy/controls render above the phone shells without shrinking or rerouting the product.
- The Loader includes an iOS-safe, runtime-independent recovery path.

## Run

```bash
npm ci
npm run check
npm run dev -- --hostname 0.0.0.0
```

The deployed preview for this branch is served independently on port `44122`; production on `44117` is not modified.

## Release assets

Production uses:

- `iphone-17-pro-official-bezel.png`
- `iphone-17-pro-silver-bezel.png`
- `iphone-17-pro-deep-blue-bezel.png`
- `premium-prism-wallpaper.jpg`

The bezel artwork is first-party/reference-derived project media. Do not assume a blanket open-source license for these assets.

## Verification

```bash
npm run lint
npm run typecheck
npm run build
```

Physical iPhone Safari/Reynard review remains the decisive visual acceptance gate for touch, Loader, and responsive choreography.
