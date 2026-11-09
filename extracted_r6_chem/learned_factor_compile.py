"""Portable learned factor -> signed angle words -> exact ANGLE family.

SPDX-License-Identifier: Apache-2.0
Signed gauge/QROM attribution is recorded in neighbor learned_qrom.py.
No opaque U/KMB dependency or training optimizer is required by this module.
The compact exchange format contains angle_words:uint16,W,H2_I,H1_I,
Hsym_lower,tree_edges. beta is passed explicitly; arbitrary R/B/C are read
from W.shape. Circuit correctness and physical fit acceptance are separate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import learned_qrom as Q

COMPACT_KEYS = ("angle_words", "W", "H2_I", "H1_I", "Hsym_lower", "tree_edges")


def canonicalize_words(angle_words, tree_edges, brot=10, *, drift_limit=1e-11):
    """Decode, signed-canonicalize and certify every row up to global sign.

    The certificate concerns already quantized vectors, never an unquantized
    training vector. W/offsets are not fitted or modified by this operation.
    """
    from dfthcsos.scoreinfra.dfthc_math import reconstruct_u_vectors
    words = np.asarray(angle_words)
    edges = np.asarray(tree_edges)
    if brot not in (8, 9, 10, 11, 12) or words.ndim != 2 or not np.issubdtype(words.dtype, np.integer):
        raise ValueError("Expected2D integer words and beta8 or10")
    if np.any(words < 0) or np.any(words >= (1 << brot)):
        raise ValueError("Word outside beta range")
    if edges.shape != (words.shape[1], 2) or not np.issubdtype(edges.dtype, np.integer):
        raise ValueError("tree_edges must have one integer parent/child row per angle")
    n, seen = words.shape[1] + 1, {0}
    for parent, child in edges:
        parent, child = int(parent), int(child)
        if parent not in seen or child in seen or not 0 <= child < n:
            raise ValueError("Gauge requires an ordered rooted Givens tree")
        seen.add(child)
    old = reconstruct_u_vectors(words / (1 << (brot - 1)), edges)
    a, angles = old.copy(), np.empty(words.shape, dtype=np.float64)
    for k, (p, q) in reversed(list(enumerate(edges))):
        norm = np.hypot(a[:, p], a[:, q])
        sign = np.where(np.abs(a[:, p]) < 1e-12,
                        np.where(a[:, q] > 0, -1, 1), np.where(a[:, p] < 0, -1, 1))
        angles[:, k] = np.where(norm < 1e-12, 0,
                                 np.arctan2(a[:, q] * sign, a[:, p] * sign))
        a[:, p] = np.where(norm < 1e-12, 0, norm * sign)
        a[:, q] = 0
    canonical = np.rint(angles * ((1 << (brot - 1)) / np.pi)).astype(np.int64) % (1 << brot)
    if np.any(((canonical >> (brot - 1)) ^ (canonical >> (brot - 2))) & 1):
        raise ArithmeticError("Signed-angle redundant-bit identity failed")
    decoded = reconstruct_u_vectors(canonical / (1 << (brot - 1)), edges)
    row_sign = np.where(np.einsum("ij,ij->i", old, decoded) < 0, -1, 1)
    aligned = decoded * row_sign[:, None]
    drift = float(np.max(np.abs(aligned - old)))
    projector_frob_bound = 2 * np.linalg.norm(aligned - old, axis=1)
    if drift > drift_limit:
        raise ArithmeticError(f"Signed gauge exceeds row component certificate: {drift}")
    report = dict(rows_checked=len(words), angles_per_row=words.shape[1], brot=brot,
                  max_component_drift_up_to_row_sign=drift,
                  max_projector_frobenius_drift_upper_bound=float(projector_frob_bound.max()),
                  redundant_bit_identity=f"bit{brot-1}=bit{brot-2}",
                  certificate="ALL_ROWS_UP_TO_SIGN_WITH_FLOATING_TOLERANCE",
                  physical_accuracy_or_score_claim=False,
                  source="Kozykorpesh V3/run361677445 signed Givens gauge; generalized beta8/beta10")
    return canonical.astype("<u2"), report


def validate_compact(data, brot):
    if brot not in (8, 9, 10, 11, 12):
        raise ValueError("Supported beta values are8 and10")
    missing = set(COMPACT_KEYS) - set(data)
    if missing:
        raise KeyError(f"Missing compact arrays: {sorted(missing)}")
    w, words = np.asarray(data["W"]), np.asarray(data["angle_words"])
    if w.ndim != 3 or min(w.shape) < 1 or not np.all(np.isfinite(w)):
        raise ValueError("W must be finite with positive R/B/C")
    n = words.shape[1] + 1 if words.ndim == 2 else 0
    if words.shape != (n + w.shape[0] * w.shape[1], n - 1):
        raise ValueError("Expected N+R*B angle rows and N-1 columns")
    if not np.issubdtype(words.dtype, np.integer) or np.any(words < 0) or np.any(words >= (1 << brot)):
        raise ValueError("Words must be integers in the requested beta range")
    if np.shape(data["H2_I"]) != (w.shape[0], w.shape[2]):
        raise ValueError("H2_I must have shape(R,C)")
    for key in COMPACT_KEYS[1:]:
        if not np.all(np.isfinite(data[key])):
            raise ValueError(f"Nonfinite compact array {key}")
    if np.shape(data["tree_edges"]) != (n - 1, 2):
        raise ValueError("tree_edges dimensions disagree with words")
    edges = np.asarray(data["tree_edges"])
    if not np.issubdtype(edges.dtype, np.integer):
        raise ValueError("tree_edges must contain integer vertex IDs")
    seen = {0}
    for parent, child in edges:
        parent, child = int(parent), int(child)
        if parent not in seen or child in seen or not 0 <= child < n:
            raise ValueError("Expected an ordered rooted Givens tree")
        seen.add(child)
    if np.shape(data["H1_I"]) not in ((), (1,)):
        raise ValueError("H1_I must be a scalar")
    if np.shape(data["Hsym_lower"]) != (n * (n + 1) // 2,):
        raise ValueError("Hsym_lower must contain the packed lower triangle")
    return dict(N=n, R=int(w.shape[0]), B=int(w.shape[1]), C=int(w.shape[2]),
                addresses=len(words), brot=int(brot))


def load_compact(path, brot=10):
    with np.load(path, allow_pickle=False) as archive:
        data = {key: np.array(archive[key]) for key in COMPACT_KEYS}
    validate_compact(data, brot)
    return data


def save_compact(data, destination, brot=10, *, canonicalize=True, cap_bytes=None):
    data = {key: np.array(data[key], copy=True) for key in COMPACT_KEYS}
    shape = validate_compact(data, brot)
    report = None
    if canonicalize:
        data["angle_words"], report = canonicalize_words(data["angle_words"], data["tree_edges"], brot)
    data["angle_words"] = np.asarray(data["angle_words"], dtype="<u2")
    data["tree_edges"] = np.asarray(data["tree_edges"], dtype="<i8")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(destination, **data)
    size = destination.stat().st_size
    if cap_bytes is not None and size > cap_bytes:
        raise ValueError(f"Compact file {size}bytes exceeds requested {cap_bytes}byte cap")
    return dict(**shape, bytes=size, sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                U_saved=False, gauge=report, physical_accuracy_or_score_claim=False)


def restore_factor(data, brot=10):
    """Regenerate the official U from the signed words; copy all other arrays."""
    from dfthcsos.scoreinfra.dfthc_math import reconstruct_u_vectors
    shape = validate_compact(data, brot)
    result = {key: np.array(data[key], copy=True) for key in COMPACT_KEYS}
    vectors = reconstruct_u_vectors(np.asarray(data["angle_words"]) / (1 << (brot - 1)),
                                    data["tree_edges"])
    result["U"] = vectors[shape["N"]:].reshape(shape["R"], shape["B"], shape["N"])
    return result


def build_family(compact, output_directory, *, brot=10, J=3, canonicalize=True):
    """Compile from explicit learned arrays, returning family plus reports.

    Resources use the untouched official heuristic model, but do not test the
    learned factor's Hamiltonian errors. The full verifier is still required.
    Existing circuit files are refused, avoiding stale family members.
    """
    data = load_compact(compact, brot) if isinstance(compact, (str, Path)) else {
        key: np.array(compact[key], copy=True) for key in COMPACT_KEYS}
    shape = validate_compact(data, brot)
    gauge = None
    if canonicalize:
        data["angle_words"], gauge = canonicalize_words(data["angle_words"], data["tree_edges"], brot)
    elif np.any(((data["angle_words"] >> (brot - 1)) ^ (data["angle_words"] >> (brot - 2))) & 1):
        raise ValueError("canonicalize=False requires already signed angle words")
    out = Path(output_directory)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob("angle_k_*.kmb")) or any(out.glob("angle_k_*.kmx")):
        raise FileExistsError("Output already contains an ANGLE family")
    circuits, entries = [], []
    deltas = Q.batch_deltas(data["angle_words"], J)
    for k, delta in enumerate(deltas):
        circuit, resource = Q.build(delta, brot, return_report=True)
        path = out / f"angle_k_{k}.kmb"
        circuit.to_file(path, format="kmb")
        resource.update(k=k, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)
        circuits.append(circuit)
        entries.append(resource)
    factor = restore_factor(data, brot)
    np.savez_compressed(out / "submission.npz", **factor)
    family_t = sum(e["static_toffoli"] for e in entries)
    from dfthcsos.verify import resource_costs
    resources = resource_costs(SimpleNamespace(w=data["W"], num_orbitals=shape["N"]),
                              circuits, brot, 2 * family_t)
    report = dict(status="GENERATED_EXACT_INTEGER_TABLES_FULL_VERIFIER_PENDING", **shape,
                  J=J, num_circuits=len(circuits), gauge=gauge, circuits=entries,
                  family_toffoli_per_forward_pass=family_t,
                  family_toffoli_forward_and_reverse=2 * family_t,
                  official_resource_model=resources,
                  static_count_scope="No classically conditioned Toffoli gates are emitted; static counts equal every executed pass",
                  physical_accuracy_or_score_claim=False, full_official_verification="NOT_RUN",
                  arrays_preserved=["W", "H2_I", "H1_I", "Hsym_lower", "tree_edges"])
    (out / "compile_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return tuple(circuits), data, report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("compact", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--brot", type=int, choices=(8, 9, 10, 11, 12), default=10)
    parser.add_argument("--J", type=int, default=3)
    args = parser.parse_args()
    _, _, result = build_family(args.compact, args.output, brot=args.brot, J=args.J)
    print(json.dumps({key: result[key] for key in ["status", "N", "R", "B", "C", "J", "brot",
        "num_circuits", "family_toffoli_per_forward_pass", "official_resource_model"]}), flush=True)