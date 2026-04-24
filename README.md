# actions-runner-images

Custom GitHub Actions runner images used by the `jr200-labs` and `whengas`
self-hosted ARC (Actions Runner Controller) deployments.

Extends the upstream `ghcr.io/actions/actions-runner` base with build
tooling so jobs that compile native Python wheels (e.g. `mariadb`,
`cryptography`) don't fail on vanilla runner pods.

## Images

| Image | Path                        | Purpose                                                   |
|-------|-----------------------------|-----------------------------------------------------------|
| base  | `images/base/Dockerfile`    | Ubuntu runner + build-essential + MariaDB/SSL dev headers |

Consumed from `whengas/whengas-iac` via `services/arc-runners-*/env/base/values.yaml`
`template.spec.containers[name=runner].image`.

## Layout

```
images/
  base/
    Dockerfile           # image recipe
    README.md            # image-specific notes
  <future-variant>/      # e.g. rust/, go/ — same pattern
shared/                  # (reserved) cross-image assets
```

## CI

- Pull requests run hadolint (via `lint_docker.yaml` reusable, recursive)
  and commitlint (via `lint_commits.yaml` reusable).
- Merges to `master` trigger release-please; merging the release PR cuts
  a tag + GitHub Release, which dispatches `build.yaml` to build and push
  the image to `ghcr.io/jr200-labs/actions-runner-images:<tag>`.

## Versioning

Single-package semver across the repo. When a second image variant
lands, this flips to release-please manifest mode (per-image versions,
tags like `base-v1.2.3`).

## Adding a new image

1. Create `images/<variant>/Dockerfile` + `README.md`.
2. Add a row to the Images table above.
3. (Future) duplicate the build dispatch path in `.github/workflows/`.

## Config sync

Shared configs (`release-please-config.json`, cached `.shared/.hadolint.yaml`)
are pulled at pre-commit time from `jr200-labs/github-action-templates`.
Edits to those files belong upstream — see that repo's `shared/` dir.
