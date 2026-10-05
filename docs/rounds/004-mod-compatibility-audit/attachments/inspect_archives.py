"""Static release-archive evidence; never extract or execute archive contents."""
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def inspect(item, cache):
    path = cache / item['name']
    command = ['curl', '-fL', '--retry', '2', '--max-time', '300', '-sS', item['url'], '-o', str(path)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"curl {item['url']}: exit {result.returncode}: {result.stderr}")
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    digest = h.hexdigest()
    assert 'sha256:' + digest == item['api_digest'], item['name']
    listed = subprocess.run(['bsdtar', '-tf', str(path)], capture_output=True, text=True)
    assert listed.returncode == 0, listed.stderr
    listing = listed.stdout
    with zipfile.ZipFile(path) as archive:
        names = sorted(i.filename for i in archive.infolist() if not i.is_dir())
        # Retain only compact configuration details, not distributed binaries.
        configs = {}
        for name in names:
            if name.lower().endswith(('.ini', '.settings')):
                data = archive.read(name)
                configs[name] = {'sha256': hashlib.sha256(data).hexdigest(),
                                 'text': data.decode('utf-8-sig')}
        return dict(item, downloaded_bytes=path.stat().st_size, sha256=digest,
                    curl_exit=result.returncode, listing_command='bsdtar -tf <cache>/' + path.name,
                    listing_exit=listed.returncode, listing_sha256=hashlib.sha256(listing.encode()).hexdigest(),
                    file_count=len(names), files=names, configs=configs,
                    prefixes=dict(Counter('/'.join(n.split('/')[:2]) if '/' in n else n for n in names)))


def main():
    manifest, cache, output = map(Path, sys.argv[1:])
    cache.mkdir(parents=True, exist_ok=True)
    items = json.loads(manifest.read_text())['archives']
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda item: inspect(item, cache), items))
    by_name = {r['name']: r for r in rows}
    hd_old = by_name['MGSHDFix_4.1.0.zip']
    hd_new = by_name['MGSHDFix_4.1.2.zip']
    m2_old = by_name['MGSM2Fix_3.6.0.zip']
    m2_new = by_name['MGSM2Fix_3.7.3.zip']
    summary = {'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'archives': rows}
    summary['layout_delta'] = {}
    for label, old, new in [('MGSHDFix', hd_old, hd_new), ('MGSM2Fix', m2_old, m2_new)]:
        summary['layout_delta'][label] = {'added': sorted(set(new['files']) - set(old['files'])),
                                          'removed': sorted(set(old['files']) - set(new['files']))}
    summary['collisions'] = {}
    for row in rows:
        if 'Compilation_Base' in row['name']:
            summary['collisions'][row['name']] = sorted(set(hd_new['files']) & set(row['files']))
    # Full file lists remain reproducible but untracked in cache; compact summaries
    # retain their digests and only non-asset payload paths for the report.
    for row in rows:
        all_names = '\n'.join(row.pop('files')) + '\n'
        (cache / (row['name'] + '.files.txt')).write_text(all_names)
        row['file_names_sha256'] = hashlib.sha256(all_names.encode()).hexdigest()
        row['control_files'] = [n for n in all_names.splitlines() if n.endswith(('.asi', '.dll', '.exe', '.ini', '.settings', '.hlsl', '.log')) or 'LICENSE' in n or 'README' in n]
        row['prefixes'] = dict(Counter(n.split('/')[0] for n in all_names.splitlines()))
        # Store config text temporarily; committed evidence keeps exact keys/digests.
        for name, config in row['configs'].items():
            (cache / (row['name'] + '.' + Path(name).name + '.txt')).write_text(config.pop('text'))
    output.write_text(json.dumps(summary, indent=2) + '\n')
    for row in rows:
        print(f"{row['name']}: curl exit 0; bsdtar listing exit 0; {row['downloaded_bytes']} bytes; SHA256 {row['sha256']}; {row['file_count']} files")
    print('layout delta:', summary['layout_delta'])
    print('candidate HD/base collisions:', summary['collisions'])


if __name__ == '__main__':
    main()
