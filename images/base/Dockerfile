# syntax=docker/dockerfile:1.29

# Base runner image for ARC (Actions Runner Controller).
#
# Extends the upstream actions/actions-runner image with build tooling so
# pip jobs that compile C extensions (e.g. mariadb, cryptography) succeed
# on-runner instead of failing with "gcc not found" or missing headers.
#
# Keep this image minimal. Per-variant extras (rust toolchain, go etc.)
# belong in sibling images/<variant>/Dockerfile layers that FROM this one.

FROM ghcr.io/actions/actions-runner:2.338.2

# Build args consumed by build_docker_image_multiplatform (informational;
# the image itself is arch-agnostic — apt picks the right arch at install).
ARG BUILD_OS
ARG BUILD_ARCH

USER root

# Playwright chromium shared-lib deps (libnspr4, libnss3, libatk*, etc.)
# let `playwright test` launch headless chromium without
# `npx playwright install-deps` at job time. Ubuntu 24.04 uses t64 suffix
# for the libstdc++/time_t-transition packages (libasound2t64, libcups2t64,
# libatk-bridge2.0-0t64, libatk1.0-0t64, libatspi2.0-0t64).
#
# jq + gh are required by shared tooling in github-action-templates
# (check-merge-settings.sh, release-please outputs, etc.). Install them
# explicitly so every variant of the base layer carries them.
#
# gettext-base provides `envsubst`, which sigstore/cosign-installer@v4+
# invokes during install. Without it, the action exits 127 and any
# workflow signing OCI artifacts (e.g. dotagents publish-oci-artifact)
# fails before producing an image (JRL-38).
# hadolint ignore=DL3008,DL3009,DL4006
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        libmariadb-dev \
        libssl-dev \
        libffi-dev \
        python3-dev \
        ca-certificates \
        curl \
        gettext-base \
        git \
        jq \
        file \
        libnspr4 \
        libnss3 \
        libatk1.0-0t64 \
        libatk-bridge2.0-0t64 \
        libcups2t64 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libcairo2 \
        libasound2t64 \
        libatspi2.0-0t64 \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# yq is a YAML processor used by canonical caller workflows (e.g.
# build-docker-image.yaml's discover-images job parses
# .github/images.yaml — JRL-39). Distributed as a single static
# binary, not in apt, so install directly. Pinned via Renovate (regex
# manager on this RUN line).
# renovate: datasource=github-tags depName=mikefarah/yq
ARG YQ_VERSION=v4.54.2
# hadolint ignore=DL4006
RUN ARCH=$(dpkg --print-architecture) \
    && curl --fail --show-error --location \
        --retry 5 --retry-delay 2 --retry-all-errors --retry-max-time 300 \
        --connect-timeout 10 --max-time 120 \
        "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_${ARCH}" \
        -o /usr/local/bin/yq \
    && chmod 0755 /usr/local/bin/yq

# CI executables are installed once per image, without compiler toolchains.
# renovate: datasource=github-releases depName=cocogitto/cocogitto
ARG COCOGITTO_VERSION=7.0.0
# renovate: datasource=github-releases depName=rhysd/actionlint
ARG ACTIONLINT_VERSION=v1.7.12
# renovate: datasource=github-releases depName=golangci/golangci-lint
ARG GOLANGCI_LINT_VERSION=v2.15.0
# CodeQL uses bundle tags; regex versioning excludes Action release tags.
# renovate: datasource=github-releases depName=github/codeql-action versioning=regex:^codeql-bundle-v(?<major>\d+)\.(?<minor>\d+)\.(?<patch>\d+)$
ARG CODEQL_VERSION=codeql-bundle-v2.27.4
ARG TARGETARCH
COPY scripts/install-ci-tools.sh /tmp/install-ci-tools.sh
RUN bash /tmp/install-ci-tools.sh "$TARGETARCH" "$COCOGITTO_VERSION" \
      "$ACTIONLINT_VERSION" "$GOLANGCI_LINT_VERSION" "${CODEQL_VERSION#codeql-bundle-}" \
    && rm /tmp/install-ci-tools.sh \
    && chown -R runner:runner /opt/hostedtoolcache

ENV RUNNER_TOOL_CACHE=/opt/hostedtoolcache

USER runner
