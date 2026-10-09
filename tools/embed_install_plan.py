#!/usr/bin/env python3
"""Synchronize/check the authoritative module in the standalone installer."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '# BEGIN EMBEDDED INSTALL PLAN\n'
END = '# END EMBEDDED INSTALL PLAN\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify without writing')
    args = parser.parse_args()
    path = ROOT / 'install.py'
    body = path.read_bytes().decode('utf-8')
    module = (ROOT / 'install_plan.py').read_bytes().decode('utf-8')
    if '\r' in body or '\r' in module:
        parser.error('Python sources must use LF')
    if body.count(START) != 1 or body.count(END) != 1:
        parser.error('Expected exactly one pair of embedding markers')
    prefix, tail = body.split(START, 1)
    embedded, suffix = tail.split(END, 1)
    if args.check:
        if embedded != module:
            parser.error('Embedded plan differs; run tools/embed_install_plan.py')
        print('OK: standalone plan matches authoritative source')
    else:
        path.write_bytes((prefix + START + module + END + suffix).encode('utf-8'))
        print('Synchronized standalone plan (LF)')


if __name__ == '__main__':
    main()
