# syntax=docker/dockerfile:1.23

# Base runner image for ARC (Actions Runner Controller).
#
# Extends the upstream actions/actions-runner image with build tooling so
# pip jobs that compile C extensions (e.g. mariadb, cryptography) succeed
# on-runner instead of failing with "gcc not found" or missing headers.
#
# Keep this image minimal. Per-variant extras (rust toolchain, go etc.)
# belong in sibling images/<variant>/Dockerfile layers that FROM this one.

ARG BASE_IMAGE=ghcr.io/actions/actions-runner
ARG BASE_TAG=latest
FROM ${BASE_IMAGE}:${BASE_TAG}

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
# (check-merge-settings.sh, release-please outputs, etc.). Whengas's
# arc-linux-whengas pods were missing gh, which caused drift-check jobs
# to fail with "gh: command not found" when the upstream actions-runner
# base image changed between image rebuilds. Install explicitly so every
# variant of the base layer carries them.
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
        git \
        jq \
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

USER runner
