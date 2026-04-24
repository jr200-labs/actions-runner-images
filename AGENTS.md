# actions-runner-images — AGENTS.md

Scope: custom runner images for jr200-labs + whengas self-hosted ARC.

## Non-negotiable rules

1. **No project-specific data.** This repo lives under `jr200-labs/`,
   which is the generic tooling org. Never mention `whengas`, vessel
   names, LNG, shipping, or any other downstream-project concern in code,
   tests, or docs. Refer to consumers as "downstream callers" if you
   must reference them.
2. **Conventional commits only.** `feat:`, `fix:`, `build:`, `ci:`,
   `docs:`, `chore:`. Anything else breaks release-please's changelog
   routing. Squash-merge PRs (enforced in repo settings).
3. **Never admin-merge.** Human owner approves + merges all PRs.
4. **Never push to `master` directly.** Always branch + PR.

## Repo structure

- `images/<variant>/Dockerfile` — one image per subdirectory.
- `shared/` — reserved for future cross-image assets (shared install
  scripts, common base layer, etc.). Empty for now.
- `.github/workflows/` — CI (hadolint + commitlint), release-please,
  build dispatch, renovate.

## Release flow

Conventional commits to `master` → release-please opens a Release PR →
merging the Release PR creates a tag + GitHub Release → the
`release-please.yaml` workflow detects `release_created == true` and
dispatches `build.yaml` → `build_docker_image_multiplatform` reusable
builds multi-arch (amd64 + arm64) + pushes to ghcr.

Image tag == release tag (e.g. `v0.3.0`). Downstream IaC pins image
tags via Renovate (see `github-action-templates` org defaults).

When a second image lands, release-please flips to manifest mode:

```jsonc
{
  "packages": {
    "images/base": { "package-name": "base", "include-component-in-tag": true },
    "images/rust": { "package-name": "rust", "include-component-in-tag": true }
  }
}
```

Tags become `base-v1.2.3`, `rust-v0.4.0`.

## Adding a new image

1. Create `images/<variant>/Dockerfile` (pass hadolint).
2. Add `images/<variant>/README.md` describing what the variant adds
   on top of `base`.
3. For multi-image phase: update `release-please-config.json` to
   manifest mode and duplicate the build dispatch job in
   `release-please.yaml` for the new variant.
4. Update consumer `whengas-iac` runner set values once the image is
   tagged.

## Shared config sync

This repo has no language marker for python/go/node — `shared/sync.sh`
detects `docker` instead (via the `Dockerfile` / `images/*/Dockerfile`
markers) and syncs:

- `release-please-config.json` → committed at repo root (drift-enforced).
- `.shared/.hadolint.yaml` → gitignored cache; `lint_docker.yaml`
  reusable auto-surfaces it at CI time.

Run `.shared/sync.sh` (or let the pre-commit hook do it) to refresh.
Do not edit these files in-tree — edit upstream in
`jr200-labs/github-action-templates/shared/`.

## Runners

CI uses the org-level `RUNNER_PROFILES` variable to route `runs-on`.
Because this repo is in `jr200-labs/` (all-public org), the default
profile currently points at `ubuntu-latest` (GitHub-hosted, free for
public repos). To force self-hosted, flip `vars.RUNNER_PROFILE` at the
org or repo level.

## Related repos

- `jr200-labs/github-action-templates` — reusable workflows + shared
  configs this repo consumes.
- `whengas/whengas-iac` — ARC deployment (`services/arc-runners-*`)
  that pulls images from this repo.
