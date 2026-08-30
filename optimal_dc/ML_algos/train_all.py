"""Run the full training matrix (3 algorithms x 2 reward arms x N seeds) with one command.

This is the single file to hand a cluster operator. From the directory that
CONTAINS optimal_dc/:

    python -m optimal_dc.ML_algos.train_all --smoke          # ~5 min validation, do this first
    python -m optimal_dc.ML_algos.train_all                  # full matrix: 18 runs, 500k steps each
    python -m optimal_dc.ML_algos.train_all --seeds 0        # minimum matrix: 6 runs

Each run is an independent SUBPROCESS of benchmarks.py train:
  - crash isolation: an FMU failure kills one run, never the campaign;
  - parallelism: runs are CPU-bound (the FMU dominates; the nets barely touch
    the GPU), so --parallel N runs N at once (default: half the cores);
  - resume: runs whose metadata.json records >= the requested n_steps are
    skipped (a --smoke pass therefore never masquerades as a completed full
    run); interrupted/crashed runs AUTO-RESUME — benchmarks train finds their
    resume_state.pt (full nets+optimizer+RNG+day-sampler snapshot, saved at
    every episode-end PPO-update boundary) and continues BIT-IDENTICALLY to
    an uninterrupted run, losing at most the steps since that boundary. The
    snapshot is config/seed-fingerprinted: resuming under a changed config
    fails loudly instead of silently mixing settings. Re-invoking the same
    command always continues the campaign without losing progress.

Outputs land in --output (default optimal_dc/ML_algos/checkpoints/matrix/):
  <algo>_<arm>_s<seed>/   weights (*.pth) + config.json + metadata.json + run.log
  manifest.json           per-run status for the whole campaign
Send the whole tree back.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

_ML_ALGOS = Path(__file__).resolve().parent
_REPO_ROOT = _ML_ALGOS.parents[1]          # the directory containing optimal_dc/

ALGOS = ["ma_ca_ppo", "mh_ma_ca_ppo", "unified_mlp"]
ARMS = {  # arm name -> config file (native = sustain-lc proxy reward; energy = ours)
    "native": _ML_ALGOS / "config" / "variant_a_synth.yaml",
    "energy": _ML_ALGOS / "config" / "variant_a_synth_energy.yaml",
}


def completed_steps(run_dir: Path) -> int:
    """n_steps a successfully finished run in run_dir trained for, else -1.
    metadata.json is written only on success, but its step count still has to
    be checked — a 450-step --smoke pass shares the run dirs with the full
    matrix and must not count as a completed 500k run."""
    try:
        meta = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
        return int(meta["n_steps"])
    except (OSError, ValueError, KeyError, TypeError):
        return -1


def build_jobs(algos, arms, seeds, n_steps, out_root):
    jobs = []
    for algo in algos:
        for arm in arms:
            for seed in seeds:
                run_dir = out_root / f"{algo}_{arm}_s{seed}"
                jobs.append({
                    "name": run_dir.name,
                    "dir": run_dir,
                    "cmd": [sys.executable, "-m", "optimal_dc.ML_algos.benchmarks",
                            "train", "--algo", algo,
                            "--config", str(ARMS[arm]),
                            "--n_steps", str(n_steps), "--seed", str(seed),
                            "--output", str(run_dir)],
                })
    return jobs


def main(argv=None):
    ap = argparse.ArgumentParser(description="Train the full baseline matrix")
    ap.add_argument("--algos", nargs="+", default=ALGOS, choices=ALGOS)
    ap.add_argument("--arms", nargs="+", default=list(ARMS), choices=list(ARMS))
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--n-steps", type=int, default=500_000)
    ap.add_argument("--parallel", type=int, default=None,
                    help="concurrent runs (default: half the CPU cores)")
    ap.add_argument("--output", type=Path,
                    default=_ML_ALGOS / "checkpoints" / "matrix")
    ap.add_argument("--smoke", action="store_true",
                    help="450-step validation of every selected cell (seed 0 only)")
    args = ap.parse_args(argv)

    if args.smoke:
        args.n_steps, args.seeds = 450, [0]
    n_par = args.parallel or max(1, (__import__("os").cpu_count() or 4) // 2)
    out_root = args.output.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    jobs = build_jobs(args.algos, args.arms, args.seeds, args.n_steps, out_root)
    pending = []
    for j in jobs:
        done_steps = completed_steps(j["dir"])
        if done_steps >= args.n_steps:
            j["status"] = f"skipped (already complete: {done_steps} steps)"
            print(f"[skip] {j['name']} -- metadata.json records {done_steps} steps")
        else:
            if done_steps >= 0:
                print(f"[redo] {j['name']} -- metadata.json records only "
                      f"{done_steps} < {args.n_steps} steps; will resume")
            pending.append(j)

    print(f"{len(pending)} runs to execute ({len(jobs) - len(pending)} already complete), "
          f"{n_par} in parallel, {args.n_steps} steps each\n")

    running, t0, interrupted = [], time.time(), False
    try:
        while pending or running:
            while pending and len(running) < n_par:
                j = pending.pop(0)
                j["dir"].mkdir(parents=True, exist_ok=True)
                log = open(j["dir"] / "run.log", "w", encoding="utf-8")
                print(f"[start] {j['name']}")
                j["log"], j["t_start"] = log, time.time()
                j["proc"] = subprocess.Popen(j["cmd"], cwd=str(_REPO_ROOT),
                                             stdout=log, stderr=subprocess.STDOUT)
                running.append(j)
            time.sleep(10)
            for j in running[:]:
                rc = j["proc"].poll()
                if rc is None:
                    continue
                running.remove(j)
                j["log"].close()
                hrs = (time.time() - j["t_start"]) / 3600
                ok = rc == 0 and completed_steps(j["dir"]) >= args.n_steps
                j["status"] = f"{'done' if ok else f'FAILED (exit {rc})'} in {hrs:.2f} h"
                print(f"[{'done' if ok else 'FAIL'}] {j['name']} -- {j['status']} "
                      f"({len(pending)} pending, {len(running)} running)")
    except KeyboardInterrupt:
        # Ctrl+C reaches the children too (same console); each exits on its
        # own, leaving its last boundary snapshot as the resume point. Record
        # what was in flight and still write the manifest below.
        interrupted = True
        for j in running:
            j["log"].close()
            j["status"] = "interrupted (re-invoke to resume)"
        for j in pending:
            j["status"] = "interrupted before start"

    manifest = {j["name"]: j.get("status", "?") for j in jobs}
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if interrupted:
        print(f"\ncampaign interrupted after {(time.time()-t0)/3600:.2f} h -- "
              f"re-invoke the same command to resume; manifest -> {out_root/'manifest.json'}")
        return 130
    failed = [n for n, s in manifest.items() if "FAIL" in s]
    print(f"\ncampaign finished in {(time.time()-t0)/3600:.2f} h -- "
          f"{len(manifest) - len(failed)}/{len(manifest)} ok; manifest -> {out_root/'manifest.json'}")
    if failed:
        print("failed runs (re-invoke the same command to retry just these):")
        for n in failed:
            print("  ", n)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
