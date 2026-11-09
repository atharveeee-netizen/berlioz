"""V5 public dataset authentication and bounded local release checks.

SPDX-License-Identifier: Apache-2.0
ViberTeam adaptation of G's portfolio runtime; retain notebook NOTICE.txt.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import time
import zipfile

SALT = 'vqcc-signed-digit-memory-v1-20261023'
AR_SHA = '0f84f5bab3a02e6b357d4656553607174345a33d252cef643f9136db13212141'
DQI_SHA = '1161f7221de935ba1399ced409b9936d8b4cb570ef3314585d4b9bc2c5b24dd9'
REFERENCE_COSTS = {'invsqrt': 2076774.233715282,
                   'dqi': 24439473914136.668, 'dfthcsos': 3355599588.3155365}
ANGLE_COUNT = 25
CHEM_FILES = ['submission.npz'] + [f'angle_k_{i}.kmb' for i in range(ANGLE_COUNT)]
ARCHIVE_MEMBERS = {'invsqrt.kmb', 'dqi.kmb'} | {'dfthcsos/'+n for n in CHEM_FILES}
assert len(ARCHIVE_MEMBERS) == 28


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    import numpy as np
    def encode(item):
        if isinstance(item, np.ndarray): return item.tolist()
        if isinstance(item, np.generic): return item.item()
        if isinstance(item, Path): return str(item)
        raise TypeError(type(item).__name__)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=encode)+'\n', encoding='utf-8')


def official_manifest(competition):
    root = Path(competition)/'verifiers'
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*.py'))}


def authenticate_sources(source, manifest):
    actual = {name: digest(Path(source)/name) for name in manifest}
    assert actual == manifest, 'Embedded source bytes changed'
    return actual


def measure_full(name, function, reports, *, expected_shots, context):
    started = time.monotonic()
    result = function()
    result['wall_seconds'] = time.monotonic()-started
    if result['status'] != 'PASS' or result['verified_shots'] != expected_shots:
        save(Path(reports)/(name+'_failure.json'), result)
        raise ValueError(f'{name}: full verification did not pass')
    result['classification'] = 'FULL-PASS'
    result['verification_context'] = dict(fresh=True, salt=SALT, seed=None, **context)
    save(Path(reports)/(name+'.json'), result)
    return result


def locate_package(input_root):
    # Kaggle input mount names and nesting change; discover the public package by filename.
    matches = sorted(Path(input_root).rglob('chem_package_manifest.json'))
    if len(matches) != 1:
        raise FileNotFoundError(f'Expected one chem_package_manifest.json; found {len(matches)}')
    return matches[0].parent


def authenticate_package(input_root, pins, reports):
    package = locate_package(input_root)
    manifest_path = package/'chem_package_manifest.json'
    assert digest(manifest_path) == pins['chem_package_manifest_sha256']
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert len(manifest) == pins['chem_manifest_entries']
    aliases = {'verifier_full.json': 'chem_verifier_full.json',
               'compile_report.json': 'chem_compile_report.json',
               'HOW_TO_REBUILD.md': 'HOW_TO_REBUILD_chemistry.md'}
    source_zip = package/'chem_rebuild_source.zip'
    source_entries = {name for name in manifest if name.startswith('rebuild_source/')}
    if source_zip.is_file():
        assert digest(source_zip) == pins['chem_rebuild_source_zip_sha256']
        archive = zipfile.ZipFile(source_zip)
        assert set(archive.namelist()) == source_entries, 'Unexpected chemistry source ZIP contents'
        read_source, source_where = archive.read, 'chem_rebuild_source.zip!'
    else:
        # Kaggle extracts an uploaded ZIP into a folder; every extracted file is
        # still authenticated below against the package manifest.
        hits = sorted(p for p in Path(input_root).rglob('rebuild_source') if p.is_dir())
        assert hits, 'chemistry source folder missing'
        base = hits[0].parent
        found = {p.relative_to(base).as_posix() for p in (base/'rebuild_source').rglob('*') if p.is_file()}
        assert source_entries <= found, 'Missing extracted chemistry source files'
        read_source, source_where = (lambda name: (base/name).read_bytes()), 'extracted '+base.name+'/'
    # The original nested hash manifest was omitted during flattening. It contains
    # exactly the 29 sorted circuit/factor/report hashes and is reconstructed byte
    # for byte, then authenticated against its own original manifest entry.
    inner_names = sorted([name for name in manifest if name.startswith('angle_k_')]+[
        'compile_report.json', 'selected_compact.npz', 'submission.npz', 'verifier_full.json'])
    inner_bytes = json.dumps({name: manifest[name]['sha256'] for name in inner_names}, indent=2).encode()
    receipt = []
    if True:
        for name, entry in manifest.items():
            if name in source_entries:
                blob = read_source(name)
                location = source_where+name
            elif name == 'sha256_manifest.json':
                blob = inner_bytes
                location = 'byte-exact reconstruction from sorted package hash entries'
            else:
                target = package/aliases.get(name, name)
                assert target.parent == package and target.is_file(), name
                blob = target.read_bytes()
                location = target.name
            actual = hashlib.sha256(blob).hexdigest()
            assert len(blob) == entry['bytes'] and actual == entry['sha256'], name
            receipt.append(dict(original_name=name, location=location, bytes=len(blob), sha256=actual))
    assert {name for name in CHEM_FILES} <= set(manifest)
    assert {p.name for p in package.glob('angle_k_*.kmb')} == set(CHEM_FILES[1:])
    assert digest(package/'invsqrt_exp225a.kmb') == AR_SHA
    save(Path(reports)/'public_input_receipt.json', dict(status='PASS',
        classification='partial/file authentication; no circuit verification',
        public_dataset='anazemcev/vqcc-viberteam-verified-circuits',
        located_by='rglob chem_package_manifest.json', manifest_sha256=digest(manifest_path),
        source_zip_sha256=digest(source_zip) if source_zip.is_file() else None, chemistry_manifest_entries=receipt,
        ar_sha256=AR_SHA, private_inputs=[]))
    return package, manifest


def copy_ar(package, final):
    source = Path(package)/'invsqrt_exp225a.kmb'
    assert digest(source) == AR_SHA
    final = Path(final)
    final.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, final/'invsqrt.kmb')
    assert digest(final/'invsqrt.kmb') == AR_SHA


def copy_chemistry(package, manifest, final):
    output = Path(final)/'dfthcsos'
    output.mkdir(parents=True, exist_ok=True)
    assert not any(output.iterdir()), 'Use a fresh output directory'
    for name in CHEM_FILES:
        shutil.copyfile(Path(package)/name, output/name)
        assert digest(output/name) == manifest[name]['sha256'], name
    return output


def recompile_angles(package, manifest, work, reports):
    """Fast exact integer-word recompilation, with all 25 accepted KMB hashes required.

    The authenticated dataset NPZ remains the submitted factorization, preserving
    its exact file bytes across NumPy/ZIP versions. No training or refit occurs.
    """
    import importlib
    import sys
    source = Path(work)/'chem_compiler'
    output = Path(work)/'chem_recompiled'
    source.mkdir(parents=True, exist_ok=True)
    assert not output.exists(), 'Use a fresh recompilation directory'
    names = ('learned_factor_compile.py', 'learned_qrom.py')
    source_zip = Path(package)/'chem_rebuild_source.zip'
    if source_zip.is_file():
        with zipfile.ZipFile(source_zip) as archive:
            blobs = {name: archive.read('rebuild_source/'+name) for name in names}
    else:
        # Kaggle extracts an uploaded ZIP into a folder of the dataset.
        hits = sorted(p for p in Path(package).rglob('rebuild_source') if p.is_dir())
        assert hits, 'chemistry source folder missing'
        blobs = {name: (hits[0]/name).read_bytes() for name in names}
    if True:
        for name in names:
            blob = blobs[name]
            assert hashlib.sha256(blob).hexdigest() == manifest['rebuild_source/'+name]['sha256']
            path = source/name
            if path.exists():
                assert path.read_bytes() == blob, 'Embedded chemistry source changed: '+name
            else:
                path.write_bytes(blob)
    sys.path.insert(0, str(source))
    learned = importlib.import_module('learned_factor_compile')
    started = time.monotonic()
    circuits, _, report = learned.build_family(Path(package)/'selected_compact.npz', output,
        brot=10, J=3, canonicalize=False)
    assert len(circuits) == ANGLE_COUNT and max(c.num_qubits for c in circuits) <= 128
    hashes = {name: digest(output/name) for name in CHEM_FILES[1:]}
    assert hashes == {name: manifest[name]['sha256'] for name in CHEM_FILES[1:]}
    elapsed = time.monotonic()-started
    save(Path(reports)/'chemistry_recompile.json', dict(status='PASS',
        classification='partial/byte-exact source compilation; full verifier follows',
        seconds=elapsed, all_25_kmb_hashes_identical=True, angle_sha256=hashes,
        submission_npz_source='Authenticated dataset bytes', compiler_report=report))
    return output, elapsed


def make_archive(final, archive_path, members):
    assert set(members) == ARCHIVE_MEMBERS and len(members) == 28
    manifest = []
    for name in sorted(members):
        path = Path(final)/name
        manifest.append(dict(file=name, bytes=path.stat().st_size, sha256=digest(path)))
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for row in manifest:
            archive.write(Path(final)/row['file'], row['file'])
    with zipfile.ZipFile(archive_path) as archive:
        assert sorted(archive.namelist()) == sorted(members)
        for row in manifest:
            with archive.open(row['file']) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256']
    return manifest