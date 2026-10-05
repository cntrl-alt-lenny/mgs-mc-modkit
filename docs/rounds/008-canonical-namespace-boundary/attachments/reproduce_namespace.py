"""Diagnostic namespace reproduction; executes only a generated C++ probe."""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--compile-cpp', action='store_true')
    args = parser.parse_args()
    root = args.source_root.resolve()
    sys.path.insert(0, str(root))
    fixture = runpy.run_path(str(root / 'tests/test_schema_capture.py'))
    constants = fixture['CONSTANTS']
    decoy = 'namespace Decoy {\n' + constants + '\n}\n'
    actual = constants.replace('namespace ConfigKeys {', 'namespace Actual {').replace(
        'Enable First Person Shooter Mode', 'Replacement Key')
    header = decoy + actual + '\nnamespace ConfigKeys = Actual;\n'
    with tempfile.TemporaryDirectory() as scratch:
        source = fixture['source'](Path(scratch), constants=header)
        try:
            captured = fixture['capture'].capture(source, 'test', 'tree')
        except fixture['capture'].CaptureError as error:
            print('API rejected:', error)
        else:
            print('API fields:', json.dumps(captured['fields']['First Person Shooter Mode'], sort_keys=True))
        cli = subprocess.run(
            [sys.executable, str(root / 'tools/capture_settings_schema.py'),
             str(source), '--tag', 'test', '--tree', 'tree'], capture_output=True, text=True)
        print('CLI exit:', cli.returncode, 'stdout bytes:', len(cli.stdout.encode()), 'stderr:', repr(cli.stderr))
        print('Actual global ConfigKeys::Demo_Setting resolves to Replacement Key.')
        if args.compile_cpp:
            compiler = shutil.which('clang++') or shutil.which('g++')
            if not compiler:
                print('C++ probe not verified: no clang++ or g++ available.')
                return
            driver = source / 'prove.cpp'
            driver.write_text('#include "src/resources/config_keys.hpp"\n#include <cstdio>\n'
                              'int main(){std::puts(ConfigKeys::Demo_Setting);}\n')
            executable = source / ('prove.exe' if sys.platform == 'win32' else 'prove')
            compiled = subprocess.run(
                [compiler, '-std=c++11', str(driver), '-o', str(executable)], capture_output=True, text=True)
            print('Compile exit:', compiled.returncode, 'stderr:', repr(compiled.stderr))
            if compiled.returncode:
                raise SystemExit(compiled.returncode)
            native = subprocess.run([str(executable)], capture_output=True, text=True)
            print('Native C++ resolution exit:', native.returncode, 'stdout:', repr(native.stdout))
            if native.returncode:
                raise SystemExit(native.returncode)


if __name__ == '__main__':
    main()
