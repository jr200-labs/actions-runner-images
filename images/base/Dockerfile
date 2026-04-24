# syntax=docker/dockerfile:1.7

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
# hadolint ignore=DL3008
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER runner
