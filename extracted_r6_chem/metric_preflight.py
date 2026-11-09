"""Official Kaggle metric v10 readers, unchanged except formatting.
Source: https://www.kaggle.com/code/metric/google-quantum-ai-metric
Adapter preflight_directory only checks the file contract; task verification is separate.
"""
import json
import math
import pathlib
import random
import stat
import sys
import time
import tokenize
import zipfile
import zlib
from collections.abc import Callable, Mapping
from typing import Any
import numpy as np
import pandas as pd
ALLOWED_INSTRUCTIONS = {'X', 'CX', 'CCX', 'Z', 'CZ', 'CCZ', 'Z_POW', 'NEG', 'SWAP', 'CSWAP', 'R', 'HMR', 'BIT_INVERT', 'BIT_STORE0', 'BIT_STORE1', 'PUSH_CONDITION', 'POP_CONDITION', 'INFO_TAG', 'DEBUG_PRINT'}
MAX_QUBIT_OR_BIT_ID = 2 ** 30 // 1536
MAX_NPZ_BYTES = 2 ** 26

class ParticipantVisibleError(Exception):
    pass

def read_circuit(path: pathlib.Path, max_registers: int) -> Any:
    """Return a submitted .kmx or .kmb circuit as a kickmix.Circuit; raise ValueError unless it is fit to verify.

    kickmix validates a file as it parses it, within limits that keep parsing cheap, but simulating
    takes memory that grows with the largest qubit and bit ids, which kickmix allows up to ~5e8,
    so those are capped at MAX_QUBIT_OR_BIT_ID. kickmix also allows a million registers, at
    ~110 bytes each even if empty, so a circuit may have at most `max_registers`, the most its
    benchmark needs. Every register must be named: the dfthcsos verifier crashes on an unnamed one.
    """
    import kickmix
    circuit = kickmix.Circuit.from_file(path, format=path.suffix.removeprefix('.'))
    unsupported = set(circuit.operation_statistics()) - ALLOWED_INSTRUCTIONS
    if unsupported:
        raise ValueError(f'unsupported instructions {sorted(unsupported)}')
    largest_id = max(circuit.num_qubits, circuit.num_bits) - 1
    if largest_id >= MAX_QUBIT_OR_BIT_ID:
        raise ValueError(f'qubit or bit id {largest_id} is above the limit of {MAX_QUBIT_OR_BIT_ID - 1}')
    if circuit.num_registers > max_registers:
        raise ValueError(f'{circuit.num_registers} registers, above the limit of {max_registers} for this benchmark')
    if not all((isinstance(name, str) for name in circuit.register_data)):
        raise ValueError('every register needs a name, given by its REGISTER line')
    return circuit

def read_npz(path: pathlib.Path, spec: Mapping[str, tuple[str, tuple[int | str, ...]]]) -> dict[str, np.ndarray]:
    """Return the arrays `spec` names from an .npz; raise ValueError unless each is a plain number array as specified.

    `spec` maps each key to the numpy dtype kinds it may have, such as 'f' for floats, and its shape,
    in which a string names a dimension of any positive size that must agree wherever it recurs.

    Each array's header is a Python literal of its dtype and shape, which np.load trusts: a few KB
    of deflated zeros can claim a terabyte-sized array, and the dtype can be anything numpy can
    describe, from structured and nested types to Python objects that need unpickling. So the
    headers are read first, and the arrays loaded only if each is a plain number type of its kind,
    not big-endian, with its shape, and they total at most MAX_NPZ_BYTES. Only format 1.0 headers,
    which numpy.savez writes, are accepted, and numpy refuses any over 10 KB before parsing it.
    """
    dimensions: dict[str, int] = {}
    total = 0
    with zipfile.ZipFile(path) as archive:
        members = {name.removesuffix('.npy'): name for name in archive.namelist()}
        missing = [key for key in spec if key not in members]
        if missing:
            raise ValueError(f'{path.name} has no {missing}')
        for key, (kinds, expected_shape) in spec.items():
            with archive.open(members[key]) as member:
                if np.lib.format.read_magic(member) != (1, 0):
                    raise ValueError(f'{key} in {path.name} is not in .npy format 1.0, which numpy.savez writes')
                shape, _, dtype = np.lib.format.read_array_header_1_0(member)
            if dtype.kind not in kinds or dtype.names is not None or dtype.subdtype is not None or (dtype.byteorder == '>'):
                raise ValueError(f'{key} in {path.name} has dtype {dtype}, not a plain number type of numpy kind {kinds!r}')
            matches = len(shape) == len(expected_shape) and all((size > 0 and size == (dimensions.setdefault(expected, size) if isinstance(expected, str) else expected) for size, expected in zip(shape, expected_shape, strict=True)))
            if not matches:
                raise ValueError(f'{key} in {path.name} has shape {shape}, not {expected_shape} with its named dimensions as in {dimensions}')
            total += math.prod(shape) * dtype.itemsize
    if total > MAX_NPZ_BYTES:
        raise ValueError(f'the arrays in {path.name} take {total:,} bytes, above the limit of {MAX_NPZ_BYTES:,}')
    with np.load(path, allow_pickle=False) as npz:
        return {key: np.array(npz[key]) for key in spec}

def find_one(root: pathlib.Path, name: str, description: str, is_dir: bool=False) -> pathlib.Path:
    """The one path called `name` (a glob) under `root`, where the submission unpacked; raise ParticipantVisibleError otherwise."""
    paths = [path for path in root.rglob(name) if path.is_dir() == is_dir and '__MACOSX' not in path.relative_to(root).parts]
    if len(paths) != 1:
        raise ParticipantVisibleError(f'The submission must contain exactly one {description}, found {len(paths)}.')
    return paths[0]


def preflight_directory(directory):
    root = pathlib.Path(directory).resolve()
    inv_path = find_one(root, 'invsqrt.km[xb]', 'inverse circuit')
    dqi_path = find_one(root, 'dqi.km[xb]', 'DQI circuit')
    chemistry = find_one(root, 'dfthcsos', 'chemistry directory', is_dir=True)
    inv = read_circuit(inv_path, 1)
    inv_qubits = inv.num_qubits
    del inv
    decoder = read_circuit(dqi_path, 4095 + 70)
    decoder_qubits = decoder.num_qubits
    del decoder
    angles = sorted(chemistry.glob('angle_k_*.km[xb]'))
    if not angles or {p.stem for p in angles} != {f'angle_k_{i}' for i in range(len(angles))}:
        raise ValueError('Angle circuits must have consecutive numbering with no duplicate formats')
    angle_widths = []
    for path in angles:
        circuit = read_circuit(path, 128)
        if circuit.num_qubits > 128:
            raise ValueError('ANGLE circuit exceeds the 128-qubit cap')
        angle_widths.append(circuit.num_qubits)
        del circuit
    specification = {
        'U': ('f', ('R', 'B', 76)), 'W': ('f', ('R', 'B', 'C')),
        'H2_I': ('f', ('R', 'C')), 'H1_I': ('f', ()),
        'Hsym_lower': ('f', (2926,)), 'tree_edges': ('iu', (75, 2))
    }
    npz_path = find_one(chemistry, 'submission.npz', 'factorization')
    arrays = read_npz(npz_path, specification)
    paths = [inv_path, dqi_path, *sorted(angles, key=lambda p: int(p.stem.rsplit('_', 1)[1])), npz_path]
    return {'status': 'PASS', 'scope': 'Official file readers and archive layout; separate task PASS required',
            'invsqrt_qubits': inv_qubits, 'dqi_qubits': decoder_qubits,
            'angle_qubits': angle_widths, 'factorization_shape': list(arrays['W'].shape),
            'archive_members': [str(p.relative_to(root)).replace('\\', '/') for p in paths]}