# base

Minimum-viable runner image: `ghcr.io/actions/actions-runner` + the
smallest set of dev headers + compiler tooling needed to build common
Python C extensions on-runner.

## What it adds over upstream

- `build-essential` + `pkg-config` — gcc, make, pkg-config for native wheel builds.
- `libmariadb-dev` — unblocks `mariadb` Python package (no Linux wheels on PyPI).
- `libssl-dev`, `libffi-dev` — common deps for `cryptography`, `pyOpenSSL`.
- `python3-dev` — Python headers for `Cython` / `pybind11` extensions.
- `ca-certificates`, `curl`, `git` — guaranteed present (they already are
  in upstream, kept explicit for forward-compat).

## What it doesn't add

- Rust toolchain (goes in `images/rust/`).
- Go toolchain (goes in `images/go/`).
- Node (actions-runner already bundles it).

## Size

Expect ~200–300 MiB above the upstream base after the apt layer.

## Consumers

Downstream IaC repos pin `ghcr.io/jr200-labs/actions-runner-images:vX.Y.Z`
on their `AutoscalingRunnerSet` `runner` container. Renovate auto-bumps
on new releases.
