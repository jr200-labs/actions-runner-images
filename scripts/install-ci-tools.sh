#!/usr/bin/env bash
# Install release binaries during the image build, never during a CI job.
set -euo pipefail

arch=${1:?architecture required}
cog_version=${2:?Cocogitto version required}; cog_version=${cog_version#v}
actionlint_version=${3:?actionlint version required}; actionlint_version=${actionlint_version#v}
golangci_version=${4:?golangci-lint version required}; golangci_version=${golangci_version#v}
codeql_version=${5:?CodeQL version required}; codeql_version=${codeql_version#v}
for version in "$cog_version" "$actionlint_version" "$golangci_version" "$codeql_version"; do
  [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Invalid tool version" >&2; exit 1; }
done
case "$arch" in
  amd64) cog_target=x86_64-unknown-linux-musl; codeql_platform=linux64; cache_arch=x64 ;;
  arm64) cog_target=aarch64-unknown-linux-gnu; codeql_platform=linux-arm64; cache_arch=arm64 ;;
  *) echo "Unsupported CI tools architecture: $arch" >&2; exit 1 ;;
esac

# DESTDIR supports staging and offline installation tests.
bin="${DESTDIR:-}/usr/local/bin"
cache="${DESTDIR:-}/opt/hostedtoolcache"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$bin" "$cache"
download() {
  curl --fail --silent --show-error --location \
    --retry 5 --retry-delay 2 --retry-all-errors --retry-max-time 300 \
    --connect-timeout 10 --max-time 120 --output "$2" "$1"
}

download "https://github.com/cocogitto/cocogitto/releases/download/$cog_version/cocogitto-$cog_version-$cog_target.tar.gz" "$work/cog.tar.gz"
tar -xzf "$work/cog.tar.gz" -C "$work" "$cog_target/cog"
"$work/$cog_target/cog" --version
install -m 0755 "$work/$cog_target/cog" "$bin/cog"

download "https://github.com/rhysd/actionlint/releases/download/v$actionlint_version/actionlint_${actionlint_version}_linux_${arch}.tar.gz" "$work/actionlint.tar.gz"
tar -xzf "$work/actionlint.tar.gz" -C "$work" actionlint
"$work/actionlint" -version
install -m 0755 "$work/actionlint" "$bin/actionlint"

download "https://github.com/golangci/golangci-lint/releases/download/v$golangci_version/golangci-lint-$golangci_version-linux-$arch.tar.gz" "$work/golangci.tar.gz"
tar -xzf "$work/golangci.tar.gz" -C "$work" "golangci-lint-$golangci_version-linux-$arch/golangci-lint"
"$work/golangci-lint-$golangci_version-linux-$arch/golangci-lint" version
install -m 0755 "$work/golangci-lint-$golangci_version-linux-$arch/golangci-lint" "$bin/golangci-lint"

# Keep the full bundle, including query packs, in the native Actions tool cache.
# CodeQL Action looks up this version/architecture and its completion marker.
codeql_cache="$cache/CodeQL/$codeql_version/$cache_arch"
download "https://github.com/github/codeql-action/releases/download/codeql-bundle-v$codeql_version/codeql-bundle-$codeql_platform.tar.gz" "$work/codeql.tar.gz"
mkdir -p "$codeql_cache"
tar -xzf "$work/codeql.tar.gz" -C "$codeql_cache"
actual_codeql=$("$codeql_cache/codeql/codeql" version --format=json | jq -r .version)
if [ "$actual_codeql" != "$codeql_version" ]; then
  echo "CodeQL bundle version does not match image pin" >&2
  exit 1
fi
touch "$codeql_cache/pinned-version" "$codeql_cache.complete"
ln -s "../../../opt/hostedtoolcache/CodeQL/$codeql_version/$cache_arch/codeql/codeql" "$bin/codeql"
