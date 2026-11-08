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
- Prebuilt Cocogitto (`cog`), actionlint and golangci-lint on `/usr/local/bin`.
- The complete CodeQL bundle and query packs in
  `/opt/hostedtoolcache/CodeQL/<version>/<architecture>`, including the
  completion marker used by CodeQL Action. `codeql` is also on `PATH`.
- `file`, used by CodeQL's Go tracing.

Tool versions are pinned in annotated Docker build arguments and tracked by
Renovate. The installer selects native Linux amd64 or arm64 archives and checks
each executable during the image build. No Go or Rust compilation takes place
in jobs to provide these tools. Failed downloads or extraction fail the image
build; a CodeQL completion marker is written only after validation.

`RUNNER_TOOL_CACHE=/opt/hostedtoolcache` makes the bundle visible to CodeQL
Action. A matching CLI version is reused automatically. When CodeQL Action
starts requesting a newer CLI version, update the image pin and rebuild; an
unmatched version may still be downloaded by the action. Keep that environment
variable intact in the runner deployment and do not mask the image's tool cache
with an empty volume.

Shared workflows prefer version-matched preinstalled tools. golangci-lint also
needs a compatible Go compiler version; workflows retain their cache/install
path for unmatched tool versions and other runner images. The application Go
toolchain and language build dependencies remain workflow responsibilities.

## What it doesn't add

- Rust toolchain (goes in `images/rust/`).
- Go toolchain (goes in `images/go/`).
- Node (actions-runner already bundles it).

## Size

The CodeQL bundle includes its runtime, extractors and query packs and increases
the image size. Measure both platform manifests after building; no image size or
pull-time measurement is available from offline installer tests.

## Validation

Run the offline archive-layout and failure checks:

```sh
python3 scripts/test-ci-tools.py
```

Build and smoke-test the native image before publishing:

```sh
docker build -f images/base/Dockerfile -t ci-runner:local .
docker run --rm --entrypoint bash ci-runner:local -c \
  'cog --version && actionlint -version && golangci-lint version && codeql version'
```

Repeat the build and execution checks on native amd64 and arm64 runners. Offline
fixtures verify archive selection and tool-cache layout, not native CodeQL
execution or successful security analysis.

## Consumers

Downstream IaC repos pin `ghcr.io/jr200-labs/actions-runner-images:vX.Y.Z`
on their `AutoscalingRunnerSet` `runner` container. Renovate auto-bumps
on new releases.
