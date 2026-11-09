"""Public chemistry release: exact artifact replay and optional regeneration.

Compiled ANGLE circuits and original C60 factorization:
https://www.kaggle.com/code/k256net/claude?scriptVersionId=361337610
Their original generators are not supplied by that public notebook; they are
reused as attributed compiled artifacts. Preserve upstream attribution and
applicable notices when redistributing.

Our contributions here are the normalization-reducing exact rotations,
ensemble compression, physical-metric C34 projection and scalar identity fit.
SVD/eigendecomposition may differ across numerical libraries. Regeneration
therefore gets a NEW official report and is never assigned the recorded hash.
Exact replay requires the nine scored files to be attached from a PUBLIC
checkpoint, plus the original competition data. No private data is required.
"""
import hashlib
import json
import shutil
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

SOURCE_URL = 'https://www.kaggle.com/code/k256net/claude?scriptVersionId=361337610'
SCORED_FAMILY_SHA256 = '8aa3639458849957bfeb51f33131a73cf08b833829f39b91149a4c5714e282b7'
SCORED_MEMBERS_SHA256 = {'angle_k_0.kmb': 'a5166e5370e3858d61ae09f220ce81c0e5a9f3322ea60372a66d0c12b87fc2de', 'angle_k_1.kmb': 'b4f41fef3704b24dd2eae172e1393b84113b1ca2228a053f461cd3ca17ee76d7', 'angle_k_2.kmb': '7873d91617f7c6873eb8b1a7582222c00b19af3c19bc09f495e27973f2c4d2a6', 'angle_k_3.kmb': 'caa88952f006b9bf6d7ffda4615d646d834edc487948bfc1a3651447ce09fa78', 'angle_k_4.kmb': 'fcc6df7101e627227fe6cd9729693cb2905e8c8fca8bf6388c98c88f1a110cf2', 'angle_k_5.kmb': 'aeca9120088611964836145cbddfce764765f65bde3065f8ad5be16af8b2b617', 'angle_k_6.kmb': 'ca0f9da0b36ad94a9fe739ea080b2eba2a7cd6a6ec252f1e16d375a40f0c9c11', 'angle_k_7.kmb': '6c47f8a61113e091497572ed6d9bb2fbc93afb02100c627442efdc9912883d91', 'submission.npz': '92ee63050914826b45460227f9e204aef68dfaf9949c34bc22b860672fb37748'}
PUBLIC_SOURCE_MEMBERS_SHA256 = {'angle_k_0.kmb': 'a5166e5370e3858d61ae09f220ce81c0e5a9f3322ea60372a66d0c12b87fc2de', 'angle_k_1.kmb': 'b4f41fef3704b24dd2eae172e1393b84113b1ca2228a053f461cd3ca17ee76d7', 'angle_k_2.kmb': '7873d91617f7c6873eb8b1a7582222c00b19af3c19bc09f495e27973f2c4d2a6', 'angle_k_3.kmb': 'caa88952f006b9bf6d7ffda4615d646d834edc487948bfc1a3651447ce09fa78', 'angle_k_4.kmb': 'fcc6df7101e627227fe6cd9729693cb2905e8c8fca8bf6388c98c88f1a110cf2', 'angle_k_5.kmb': 'aeca9120088611964836145cbddfce764765f65bde3065f8ad5be16af8b2b617', 'angle_k_6.kmb': 'ca0f9da0b36ad94a9fe739ea080b2eba2a7cd6a6ec252f1e16d375a40f0c9c11', 'angle_k_7.kmb': '6c47f8a61113e091497572ed6d9bb2fbc93afb02100c627442efdc9912883d91', 'submission.npz': '925b317df9f070c8c0be46e195f98781b259a23a2502025d41f330de4d95ad1c'}
RECORDED_FULL_REPORT = {'status': 'PASS', 'score': 2546570136.2646174, 'lambda_eff': 47.53701636715377, 'toffoli_count': 72984.0, 'num_qubits': 734, 'brot': 10, 'batch_size': 10, 'num_circuits': 8, 'reaction_depth': 88, 'num_ops': 1687180, 'verified_shots': 254464, 'submission_sha256': '8aa3639458849957bfeb51f33131a73cf08b833829f39b91149a4c5714e282b7', 'resources': {'brot': 10, 'keep_bits': 10, 'angles_toffoli_per_pass': 31792.0, 'angles_toffoli': 63584.0, 'angles_qubits': 123, 'angles_selection_qubits': 12, 'angles_persistent_qubits': 100, 'angles_temporary_qubits': 11, 'outer_state_prep_toffoli': 680, 'inner_state_prep_toffoli': 5870, 'givens_rotations_toffoli': 2850, 'outer_state_prep_persistent_qubits': 46, 'outer_state_prep_temporary_qubits': 195, 'outer_state_prep_qubits': 241, 'inner_state_prep_persistent_qubits': 44, 'inner_state_prep_temporary_qubits': 544, 'inner_state_prep_qubits': 588, 'heuristic_persistent_qubits': 90, 'heuristic_temporary_qubits': 544, 'heuristic_toffoli': 9400, 'heuristic_qubits': 634, 'persistent_qubits': 190, 'temporary_qubits': 544, 'toffoli': 72984.0, 'qubits': 734, 'angles_within_cap': True}, 'metrics': {'error_1': 0.0023992126718305005, 'error_2': 0.019276275121415883, 'Lambda': 289.99179185749193, 'E_SOS': -22144.196144201982, 'E_gap': 3.9227942019824695, 'lambda_eff': 47.53701636715377, 'gap_in_domain': True}}
COMBINED_ANGLE_TOFFOLIS = 63584

def normalization(matrix):
    return 0.25 * np.square(np.abs(matrix).sum(axis=1)).sum()

def rotate_ensemble(weights, identity, *, sweeps=5, seed=20261023):
    weights = np.asarray(weights, dtype=np.float64)
    identity = np.asarray(identity, dtype=np.float64)
    matrix = np.concatenate([weights, identity[:, None, :]], axis=1)
    gram = matrix @ matrix.swapaxes(1, 2)
    initial = normalization(matrix)
    rng = np.random.default_rng(seed)
    pairs = np.array(np.triu_indices(matrix.shape[2], 1)).T
    rows = np.arange(matrix.shape[0])
    progress = []
    for sweep in range(sweeps):
        started = time.monotonic()
        rng.shuffle(pairs)
        for first, second in pairs:
            a, b = matrix[:, :, first].copy(), matrix[:, :, second].copy()
            # Each candidate zeros a coefficient, the breakpoints of the L1 cost.
            theta = np.concatenate([np.zeros((len(a), 1)),
                                    np.arctan2(b, a) % (np.pi / 2)], axis=1)
            cosine, sine = np.cos(theta), np.sin(theta)
            plus = a[:, :, None] * cosine[:, None, :] + b[:, :, None] * sine[:, None, :]
            minus = -a[:, :, None] * sine[:, None, :] + b[:, :, None] * cosine[:, None, :]
            cost = np.abs(plus).sum(axis=1) ** 2 + np.abs(minus).sum(axis=1) ** 2
            best = np.argmin(cost, axis=1)
            c, s = cosine[rows, best], sine[rows, best]
            matrix[:, :, first] = a * c[:, None] + b * s[:, None]
            matrix[:, :, second] = -a * s[:, None] + b * c[:, None]
        value = normalization(matrix)
        progress.append({'sweep': sweep + 1, 'lambda_h2': float(value),
                         'ratio_to_initial': float(value / initial),
                         'seconds': time.monotonic() - started})
        print(json.dumps(progress[-1]), flush=True)
    assert np.allclose(matrix @ matrix.swapaxes(1, 2), gram, atol=1e-12, rtol=1e-12)
    assert normalization(matrix) <= initial * (1 + 1e-12)
    return matrix[:, :-1], matrix[:, -1], progress

def truncate_ensemble(params, count, *, sweeps=10):
    w = np.asarray(params['W'], dtype=np.float64)
    identity = np.asarray(params['H2_I'], dtype=np.float64)
    u = np.asarray(params['U'], dtype=np.float64)
    u /= np.linalg.norm(u, axis=-1, keepdims=True)
    augmented = np.concatenate([w, identity[:, None, :]], axis=1)
    _, _, vh = np.linalg.svd(augmented, full_matrices=False)
    transformed = augmented @ vh.swapaxes(1, 2)
    gram = (u @ u.swapaxes(1, 2)) ** 2
    discarded = transformed[:, :-1, count:]
    energy = np.einsum('rbc,rbd,rdc->rc', discarded, gram, discarded)
    offset = transformed[:, -1, count:] - discarded.sum(axis=1)
    h2_bound = float(energy.sum())
    h1_bound = float(np.sum(np.abs(offset) * np.sqrt(np.maximum(0, energy))))
    # Retain the old sparse basis as closely as the smaller subspace permits.
    basis = vh[:, :count].swapaxes(1, 2)
    importance = np.square(augmented).sum(axis=1) * np.square(basis).sum(axis=2)
    indices = np.argsort(-importance, axis=1)[:, :count]
    target = np.take_along_axis(augmented, indices[:, None], axis=2)
    retained = transformed[:, :, :count]
    left, _, right = np.linalg.svd(retained.swapaxes(1, 2) @ target, full_matrices=False)
    retained = retained @ (left @ right)
    w, identity, progress = rotate_ensemble(retained[:, :-1], retained[:, -1], sweeps=sweeps)
    result = {**params, 'W': w, 'H2_I': identity}
    report = {'ensemble_count': count, 'h2_error_increase_upper_bound': h2_bound,
              'h1_target_change_upper_bound': h1_bound,
              'lambda_h2': float(normalization(np.concatenate([w, identity[:, None]], axis=1))),
              'rotation_sweeps': progress}
    return result, report

def tune_identity_offset(inputs, words, edges, brot, official_metrics):
    from scipy.optimize import linear_sum_assignment
    from dfthcsos.scoreinfra.dfthc_math import reconstruct_u_vectors, reconstruct_x

    n = inputs.num_orbitals
    vectors = reconstruct_u_vectors(np.asarray(words) / (1 << (brot - 1)), edges)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    one_body = vectors[:n]
    rank, bases, _ = inputs.w.shape
    x = reconstruct_x(vectors[n:].reshape(rank, bases, n), inputs.w)
    x = np.tril(x) + np.swapaxes(np.tril(x, k=-1), -1, -2)
    hbase = (inputs.ref['h1_thc'] - 0.5 * inputs.ref['electrons'] * inputs.S
             + inputs.beta_1 * np.eye(n))
    contraction = np.einsum('rc,rcpq->pq', inputs.W, x, optimize=True)
    abs_weights = np.abs(inputs.w).sum(axis=1)
    sum_weights = inputs.w.sum(axis=1)
    offset_norm_squared = float(np.square(inputs.W).sum())

    def evaluate(scale):
        h1 = hbase - scale * contraction
        eigenvalues, eigenvectors = np.linalg.eigh(h1)
        rows, cols = linear_sum_assignment(-np.abs(one_body @ eigenvectors))
        matched = np.empty_like(eigenvalues)
        matched[rows] = eigenvalues[cols]
        reconstructed = np.einsum('j,jp,jq->pq', matched, one_body, one_body, optimize=True)
        error_1 = float(np.linalg.norm(reconstructed - h1))
        lambda_1 = float(np.abs(eigenvalues).sum())
        lambda_2 = float(0.25 * np.square(abs_weights + np.abs(scale * inputs.W + sum_weights)).sum())
        normalization = lambda_1 + lambda_2
        e_sos = float(inputs.ref['ecore'] - inputs.ref['electrons'] * inputs.beta_1
                      - (lambda_1 - eigenvalues.sum())
                      - 0.5 * scale * scale * offset_norm_squared)
        gap = float(inputs.energy_upper - e_sos)
        valid = error_1 <= 0.02 and gap > 3.914899 and normalization > 49.0 and gap < 2 * normalization
        effective = float(np.sqrt(gap * (2 * normalization - gap))) if valid else float('inf')
        return {'scale': float(scale), 'error_1': error_1, 'Lambda': normalization,
                'E_gap': gap, 'E_SOS': e_sos, 'lambda_eff': effective}

    reference = evaluate(1.0)
    for key in ['error_1', 'Lambda', 'E_gap', 'E_SOS']:
        assert np.isclose(reference[key], official_metrics[key], atol=1e-7, rtol=1e-9), key
    if official_metrics['error_2'] > 0.02:
        return None
    offsets = np.r_[np.logspace(-7, -1, 13), 0.3, 0.5]
    grid = np.unique(np.r_[1.0, 1 - offsets, 1 + offsets])
    candidates = [evaluate(t) for t in grid]
    for _ in range(2):
        index = min(range(len(candidates)), key=lambda i: candidates[i]['lambda_eff'])
        if not np.isfinite(candidates[index]['lambda_eff']):
            return None
        low, high = grid[max(0, index - 1)], grid[min(len(grid) - 1, index + 1)]
        grid = np.unique(np.r_[grid[index], np.linspace(low, high, 101)])
        candidates = [evaluate(t) for t in grid]
    best = min(candidates, key=lambda row: row['lambda_eff'])
    params = {**inputs.params, 'H2_I': sum_weights + best['scale'] * inputs.W}
    return params, best

def build_physical_c34(params, decoded_vectors):
    """Keep the top 34 physical/identity directions, then five exact sweeps."""
    w = np.asarray(params['W'], dtype=np.float64)
    identity = np.asarray(params['H2_I'], dtype=np.float64)
    rank, bases, count = w.shape
    n = params['U'].shape[-1]
    assert count == 44 and identity.shape == (rank, count)
    vectors = np.array(decoded_vectors[n:], dtype=np.float64, copy=True).reshape(rank, bases, n)
    vectors /= np.linalg.norm(vectors, axis=-1, keepdims=True)
    assert np.isfinite(vectors).all()
    offset = identity - w.sum(axis=1)
    gram = (vectors @ vectors.swapaxes(1, 2)) ** 2
    metric = w.swapaxes(1, 2) @ gram @ w + offset[:, :, None] * offset[:, None, :]
    _, eigenvectors = np.linalg.eigh(metric)
    basis, discarded = eigenvectors[:, :, -34:], eigenvectors[:, :, :-34]
    augmented = np.concatenate([w, identity[:, None, :]], axis=1)
    retained = augmented @ basis
    projected_gram = retained @ retained.swapaxes(1, 2)
    importance = np.square(augmented).sum(axis=1) * np.square(basis).sum(axis=2)
    indices = np.argsort(-importance, axis=1)[:, :34]
    target = np.take_along_axis(augmented, indices[:, None], axis=2)
    left, _, right = np.linalg.svd(retained.swapaxes(1, 2) @ target, full_matrices=False)
    retained = retained @ (left @ right)
    before = float(normalization(retained))
    new_w, new_identity, sweeps = rotate_ensemble(
        retained[:, :-1], retained[:, -1], sweeps=5, seed=20261023,
    )
    candidate = {**params, 'W': new_w, 'H2_I': new_identity}
    after = np.concatenate([new_w, new_identity[:, None, :]], axis=1)
    assert new_w.shape == (rank, bases, 34) and np.isfinite(after).all()
    assert np.allclose(after @ after.swapaxes(1, 2), projected_gram, atol=1e-12, rtol=1e-12)
    assert all(np.array_equal(candidate[key], params[key])
               for key in params if key not in {'W', 'H2_I'})
    dropped_w = w @ discarded
    dropped_offset = np.einsum('rc,rck->rk', offset, discarded)
    x = np.einsum('rbp,rbq,rbk->rkpq', vectors, vectors, dropped_w, optimize=True)
    flat = x.reshape(-1, n * n)
    delta_h2 = float(np.linalg.norm(flat @ flat.T))
    delta_h1 = float(np.linalg.norm(np.einsum('rk,rkpq->pq', dropped_offset, x)))
    offset_loss = float(np.square(dropped_offset).sum())
    report = {
        'method': 'physical-metric C34 projection', 'C': 34, 'alpha': 1.0,
        'rotation_sweeps': sweeps, 'lambda_h2_before_rotations': before,
        'lambda_h2_after_rotations': float(normalization(after)),
        'hamiltonian_delta_frobenius': delta_h2,
        'h1_target_delta_frobenius': delta_h1,
        'discarded_native_offset_norm_squared': offset_loss,
        'gap_change_absolute_upper_bound': float(2 * np.sqrt(n) * delta_h1 + 0.5 * offset_loss),
        'limits': 'Conservative bounds do not replace official error1/error2 and gap checks.',
    }
    return candidate, report

def continue_exact_c34(params):
    """One fixed ten-sweep candidate; other factorization fields stay exact."""
    w, identity = np.asarray(params['W']), np.asarray(params['H2_I'])
    assert w.shape == (65, 60, 34) and identity.shape == (65, 34)
    augmented = np.concatenate([w, identity[:, None, :]], axis=1)
    before_gram = augmented @ augmented.swapaxes(1, 2)
    before = float(normalization(augmented))
    new_w, new_identity, sweeps = rotate_ensemble(w, identity, sweeps=10, seed=20261023)
    candidate = {**params, 'W': new_w, 'H2_I': new_identity}
    after = np.concatenate([new_w, new_identity[:, None, :]], axis=1)
    after_gram = after @ after.swapaxes(1, 2)
    assert np.isfinite(after).all()
    assert np.allclose(after_gram, before_gram, atol=1e-12, rtol=1e-12)
    assert all(np.array_equal(candidate[key], params[key])
               for key in params if key not in {'W', 'H2_I'})
    value = float(normalization(after))
    assert value <= before * (1 + 1e-12)
    return candidate, {
        'method': 'ten exact C34 ensemble-rotation sweeps', 'C': 34,
        'lambda_h2_before': before, 'lambda_h2_after': value,
        'augmented_gram_max_error': float(np.max(np.abs(after_gram - before_gram))),
        'sweeps': sweeps,
    }

def _family(path):
    path = Path(path)
    return path / 'dfthcsos' if (path / 'dfthcsos').is_dir() else path


def _sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _check_members(source, expected):
    actual = {name: _sha256(source / name) for name in expected}
    assert actual == expected, 'Public chemistry input is not the pinned family.'
    return actual


def _copy_family(source, factorization, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for name in SCORED_MEMBERS_SHA256:
        incoming = Path(factorization) if name == 'submission.npz' else source / name
        shutil.copy2(incoming, destination / name)


def verify_scored_chemistry(public_checkpoint, *, output):
    """Copy exact scored bytes and run the unchanged full official verifier."""
    from dfthcsos import verify as cv

    source, output = _family(public_checkpoint), Path(output)
    destination = output / 'dfthcsos'
    assert source.resolve() not in {output.resolve(), destination.resolve()}
    _check_members(source, SCORED_MEMBERS_SHA256)
    edges = cv.load_tree_edges(None, source)
    assert cv.submission_sha256(cv.load_circuits(source), source / 'submission.npz', edges) == SCORED_FAMILY_SHA256
    _copy_family(source, source / 'submission.npz', destination)
    _check_members(destination, SCORED_MEMBERS_SHA256)
    started = time.monotonic()
    full = cv.verify(destination, salt='public-r6-exact-replay')
    assert full['status'] == 'PASS' and full['verified_shots'] == 254464
    assert full['submission_sha256'] == SCORED_FAMILY_SHA256
    assert full['resources'] == RECORDED_FULL_REPORT['resources']
    assert np.isclose(full['score'], RECORDED_FULL_REPORT['score'], atol=1e-4, rtol=1e-10)
    assert full['resources']['angles_toffoli'] == 2 * full['resources']['angles_toffoli_per_pass']
    assert np.isclose(full['score'], cv.score_from_metrics(full['metrics'], full['resources']), rtol=1e-12)
    _check_members(destination, SCORED_MEMBERS_SHA256)
    result = {'mode': 'exact_scored_artifact_replay', 'selected_family': str(destination),
              'report': full, 'member_sha256': SCORED_MEMBERS_SHA256,
              'source_url': SOURCE_URL, 'seconds': time.monotonic() - started}
    (output / 'chemistry_release_verification.json').write_text(json.dumps(result, indent=2))
    return result


def regenerate_public_chemistry(public_c60_family, *, output):
    """Optional fixed winning-method path from public inputs; report actual bytes.

    This omits the R2 C36 benchmark branch and all rank grids. A successful
    regenerated candidate can have a different hash/cost from the scored
    checkpoint. It receives its own complete official verification.
    """
    from dfthcsos import verify as cv
    from dfthcsos.scoreinfra.dfthc_math import reconstruct_u_vectors

    source, output = _family(public_c60_family), Path(output)
    assert source.resolve() not in {output.resolve(), (output / 'dfthcsos').resolve()}
    _check_members(source, PUBLIC_SOURCE_MEMBERS_SHA256)
    output.mkdir(parents=True, exist_ok=True)
    family, edges = cv.load_circuits(source), cv.load_tree_edges(None, source)
    inputs_base = cv.load_inputs(source / 'submission.npz')
    with np.load(source / 'submission.npz', allow_pickle=False) as archive:
        original = {key: archive[key] for key in archive.files}
    assert original['W'].shape == (65, 60, 60)
    words, brot = original['angle_words'], 10

    rotated_w, rotated_identity, exact25 = rotate_ensemble(original['W'], original['H2_I'], sweeps=25)
    c44, compression = truncate_ensemble({**original, 'W': rotated_w, 'H2_I': rotated_identity}, 44, sweeps=10)
    np.savez(output / 'intermediate_c44.npz', **c44)
    vectors = reconstruct_u_vectors(words / (1 << (brot - 1)), edges)
    c34, projection = build_physical_c34(c44, vectors)

    def screen(params, name):
        path = output / (name + '.npz')
        np.savez(path, **params)
        inputs = replace(inputs_base, factorization_file=path,
                         params={**inputs_base.params, 'W': params['W'], 'H2_I': params['H2_I']},
                         w=params['W'], W=params['H2_I'] - params['W'].sum(axis=1))
        metrics = cv.evaluate_words(inputs, words, edges, brot)
        resources = cv.resource_costs(inputs, family, brot, COMBINED_ANGLE_TOFFOLIS)
        assert resources['angles_toffoli'] == 2 * resources['angles_toffoli_per_pass'] == COMBINED_ANGLE_TOFFOLIS
        return inputs, metrics, resources, cv.score_from_metrics(metrics, resources)

    inputs, metrics, resources, score = screen(c34, 'c34_raw')
    selected, fit = c34, None
    if metrics['error_2'] <= cv.ERROR_2_THRESHOLD:
        tuned = tune_identity_offset(inputs, words, edges, brot, metrics)
        if tuned is not None:
            adjusted, diagnostics = tuned
            tuned_params = {**c34, 'H2_I': adjusted['H2_I']}
            _, tuned_metrics, tuned_resources, tuned_score = screen(tuned_params, 'c34_identity_tuned')
            assert np.isclose(tuned_metrics['error_2'], metrics['error_2'], atol=1e-12, rtol=1e-10)
            if tuned_score < score:
                selected, metrics, resources, score, fit = tuned_params, tuned_metrics, tuned_resources, tuned_score, diagnostics
    assert np.isfinite(score), cv.rejection_reason(metrics, resources)
    final, exact10 = continue_exact_c34(selected)
    _, final_metrics, final_resources, final_score = screen(final, 'c34_rotated')
    assert np.isfinite(final_score), cv.rejection_reason(final_metrics, final_resources)
    assert final_score <= score * (1 + 1e-10)
    for key in ['error_1', 'error_2', 'E_SOS', 'E_gap']:
        assert np.isclose(final_metrics[key], metrics[key], atol=1e-7, rtol=0), key
    destination = output / 'dfthcsos'
    _copy_family(source, output / 'c34_rotated.npz', destination)
    expected = cv.submission_sha256(cv.load_circuits(destination), destination / 'submission.npz', edges)
    full = cv.verify(destination, salt='public-winning-method-regeneration')
    assert full['status'] == 'PASS' and full['verified_shots'] == 254464
    assert full['submission_sha256'] == expected
    assert cv.submission_sha256(cv.load_circuits(destination), destination / 'submission.npz', edges) == expected
    assert full['resources']['angles_toffoli'] == 2 * full['resources']['angles_toffoli_per_pass'] == COMBINED_ANGLE_TOFFOLIS
    assert np.isclose(full['score'], cv.score_from_metrics(full['metrics'], full['resources']), rtol=1e-12)
    result = {'mode': 'regenerated_candidate_with_fresh_full_verification',
              'selected_family': str(destination), 'report': full,
              'matches_scored_r6_hash': expected == SCORED_FAMILY_SHA256,
              'within_recorded_cost': full['score'] <= RECORDED_FULL_REPORT['score'],
              'source_url': SOURCE_URL, 'stages': {'exact25': exact25, 'C44': compression,
                  'physical_C34': projection, 'identity_fit': fit, 'exact10': exact10}}
    (output / 'chemistry_regeneration_verification.json').write_text(json.dumps(result, indent=2))
    return result