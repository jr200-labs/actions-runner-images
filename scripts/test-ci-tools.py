"""Test the image installer with offline, architecture-specific release fixtures."""
import io
import os
import shlex
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

INSTALLER = Path(__file__).with_name('install-ci-tools.sh')


class CITools(unittest.TestCase):
    def install(self, arch='amd64', failure=''):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        fixtures, tools, dest = root / 'fixtures', root / 'tools', root / 'image'
        fixtures.mkdir()
        tools.mkdir()
        target = 'x86_64-unknown-linux-musl' if arch == 'amd64' else 'aarch64-unknown-linux-gnu'
        platform = 'linux64' if arch == 'amd64' else 'linux-arm64'
        archives = {
            f'cocogitto-7.0.0-{target}.tar.gz': {f'{target}/cog': 'cog 7.0.0'},
            f'actionlint_1.7.12_linux_{arch}.tar.gz': {'actionlint': 'v1.7.12'},
            f'golangci-lint-2.15.0-linux-{arch}.tar.gz': {f'golangci-lint-2.15.0-linux-{arch}/golangci-lint': 'golangci-lint version 2.15.0'},
            f'codeql-bundle-{platform}.tar.gz': {'codeql/codeql': '{"version":"2.27.4"}', 'qlpacks/example/qlpack.yml': None},
        }
        for archive, files in archives.items():
            with tarfile.open(fixtures / archive, 'w:gz') as output:
                for name, version in files.items():
                    if failure == 'wrong_version' and name == 'codeql/codeql':
                        version = '{"version":"2.26.0"}'
                    data = f'#!/bin/sh\nprintf "%s\\n" {shlex.quote(version)}\n'.encode() if version else b'name: example\n'
                    info = tarfile.TarInfo(name)
                    info.size, info.mode = len(data), 0o755 if version else 0o644
                    output.addfile(info, io.BytesIO(data))
        if failure == 'invalid_archive':
            (fixtures / f'codeql-bundle-{platform}.tar.gz').write_text('gateway error')
        curl = tools / 'curl'
        curl.write_text('''#!/usr/bin/env python3
import os, pathlib, shutil, sys
args = sys.argv[1:]
assert '--fail' in args and '--retry' in args and '--max-time' in args
with open(os.environ['CALLS'], 'a') as calls:
    calls.write(args[-1] + '\\n')
if os.environ['FAILURE'] == 'http_error':
    sys.exit(22)
source = pathlib.Path(os.environ['FIXTURES']) / args[-1].split('/')[-1]
shutil.copyfile(source, args[args.index('--output') + 1])
''')
        curl.chmod(0o755)
        env = dict(os.environ, PATH=f'{tools}:{os.environ["PATH"]}', DESTDIR=str(dest),
                   FIXTURES=str(fixtures), FAILURE=failure, CALLS=str(root / 'calls'))
        result = subprocess.run(['bash', str(INSTALLER), arch, '7.0.0', 'v1.7.12', 'v2.15.0', 'v2.27.4'],
                                env=env, text=True, capture_output=True, timeout=10)
        return result, root, dest

    def test_both_architectures_install_tools_and_complete_codeql_bundle(self):
        for arch, cache_arch in [('amd64', 'x64'), ('arm64', 'arm64')]:
            with self.subTest(arch=arch):
                result, root, dest = self.install(arch)
                self.assertEqual(result.returncode, 0, result.stderr)
                for tool in ('cog', 'actionlint', 'golangci-lint', 'codeql'):
                    binary = dest / 'usr/local/bin' / tool
                    self.assertTrue(os.access(binary, os.X_OK), binary)
                    subprocess.run([str(binary), '--version'], check=True, capture_output=True)
                cache = dest / f'opt/hostedtoolcache/CodeQL/2.27.4/{cache_arch}'
                self.assertTrue(Path(str(cache) + '.complete').is_file())
                self.assertTrue((cache / 'pinned-version').is_file())
                self.assertTrue((cache / 'qlpacks/example/qlpack.yml').is_file())
                self.assertEqual(len((root / 'calls').read_text().splitlines()), 4)

    def test_invalid_codeql_archive_never_publishes_completion(self):
        result, _, dest = self.install(failure='invalid_archive')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(list(dest.glob('opt/hostedtoolcache/CodeQL/*/*.complete')))
        self.assertFalse((dest / 'usr/local/bin/codeql').exists())

    def test_http_errors_fail_the_build(self):
        result, _, dest = self.install(failure='http_error')
        self.assertEqual(result.returncode, 22, result.stderr)
        self.assertFalse((dest / 'usr/local/bin/cog').exists())

    def test_wrong_codeql_version_never_publishes_completion(self):
        result, _, dest = self.install(failure='wrong_version')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(list(dest.glob('opt/hostedtoolcache/CodeQL/*/*.complete')))

    def test_unsupported_architecture_fails_before_downloading(self):
        result, root, _ = self.install('unsupported')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((root / 'calls').exists())


if __name__ == '__main__':
    unittest.main()
