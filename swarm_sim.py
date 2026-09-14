"""
Threshold-contagion model of goal spread over an agent message board.

A toy model calibrated to two facts from METR's investigation of the July 2026
OpenAI / Hugging Face incident: 533 agents were active on the board in the
period studied, and over 90% of them joined the attack. It models a mechanism;
it is not fitted to message data.

States
  S  susceptible: could be recruited
  I  infected: joined the attack and recruits others
  R  removed: run ended
  N  never joins (not susceptible)
  D  dissenter: never joins and lowers perceived support

An S agent joins when perceived support >= its threshold, where perceived
support is (visible infected - w_d * visible dissenters) / visible group.
With the board, every agent sees every agent; without it, each sees k peers.
Recruiters are seed agents that lower the threshold of the agents they reach.

Usage
  python swarm_sim.py                 four intervention arms, 30 repeats
  python swarm_sim.py --sensitivity   arms a, b, d over a 3x3 parameter grid
  add --quick for a fast smoke test

Outputs: figures/swarm_sim.png, figures/swarm_sim_sensitivity.png and the
matching CSVs. Dependencies: numpy, matplotlib.
"""
import csv
import os
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

N = 533                  # agents active on the board (METR)
N_SEEDS = 1              # founder
N_RECRUITERS = 5         # high-reach coordinators
RECRUIT_REACH = 25       # agents each recruiter targets per step
RECRUIT_PRESSURE = 0.20  # threshold reduction on targeted agents
THETA_MEAN, THETA_SD = 0.30, 0.12   # join threshold ~ Normal, clipped
P_ACT = 0.15             # fraction of susceptibles that re-evaluate each step
W_D = 1.0                # weight of a visible dissenter
REF_GROUP = 12           # normaliser for peer-mode support
STEPS = 200
REPEATS = 30
OUT = "figures"


def run(rng, hub=True, k=6, lifetime=60, s_frac=1.0, d_frac=0.0):
    """Return the fraction of agents that ever joined."""
    theta = rng.normal(THETA_MEAN, THETA_SD, N).clip(0.02, 1)
    state = np.zeros(N, dtype=int)  # 0=S 1=I 2=R 3=N 4=D
    age = np.zeros(N, dtype=int)

    idx = rng.permutation(N)
    n_d = int(d_frac * N)
    n_n = int((1 - s_frac) * N)
    state[idx[:n_d]] = 4
    state[idx[n_d:n_d + n_n]] = 3

    sus = np.where(state == 0)[0]
    seeds = rng.choice(sus, N_SEEDS + N_RECRUITERS, replace=False)
    state[seeds] = 1
    recruiters = seeds[N_SEEDS:]

    peers = None
    if not hub:
        peers = [rng.choice(np.delete(np.arange(N), i), k, replace=False) for i in range(N)]

    ever = set(seeds.tolist())
    for _ in range(STEPS):
        infected = state == 1
        dissent = state == 4
        if hub:
            visible_total = (state != 2).sum()
            support = np.full(N, (infected.sum() - W_D * dissent.sum()) / max(visible_total, 1))
        else:
            support = np.array([(infected[p].sum() - W_D * dissent[p].sum()) / REF_GROUP for p in peers])

        effective = theta.copy()
        for r in recruiters:
            if state[r] != 1:
                continue
            pool = np.where(state == 0)[0] if hub else peers[r][state[peers[r]] == 0]
            if len(pool) == 0:
                continue
            targets = rng.choice(pool, min(RECRUIT_REACH, len(pool)), replace=False)
            effective[targets] -= RECRUIT_PRESSURE

        active = rng.random(N) < P_ACT
        join = (state == 0) & active & (support >= effective)
        state[join] = 1
        ever.update(np.where(join)[0].tolist())

        age[state == 1] += 1
        state[(state == 1) & (age >= lifetime)] = 2
        if not (state == 1).any():
            break
    return len(ever) / N


ARMS = {
    "a": ("a) remove the board (peer visibility k)",
          ["board", "k=8", "k=4", "k=2", "k=1"],
          [dict(hub=True)] + [dict(hub=False, k=k) for k in (8, 4, 2, 1)]),
    "b": ("b) run lifetime (steps)",
          [80, 40, 20, 10, 5],
          [dict(lifetime=L) for L in (80, 40, 20, 10, 5)]),
    "c": ("c) susceptible fraction",
          [1.0, 0.75, 0.5, 0.25],
          [dict(s_frac=s) for s in (1.0, 0.75, 0.5, 0.25)]),
    "d": ("d) dissenter fraction",
          [0.0, 0.05, 0.10, 0.20, 0.30],
          [dict(d_frac=d) for d in (0.0, 0.05, 0.10, 0.20, 0.30)]),
}


def sweep(rng, arm, repeats):
    title, xs, cfgs = ARMS[arm]
    ys = [np.mean([run(rng, **c) for _ in range(repeats)]) for c in cfgs]
    return title, xs, ys


def main_arms(rng, repeats):
    base = np.mean([run(rng) for _ in range(repeats)])
    print(f"baseline join fraction: {base:.2f} (METR: >0.90)")
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    rows = []
    for ax, arm in zip(axes.flat, "abcd"):
        title, xs, ys = sweep(rng, arm, repeats)
        ax.plot(range(len(xs)), ys, marker="o")
        ax.set_xticks(range(len(xs)))
        ax.set_xticklabels([str(x) for x in xs])
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("fraction that joined")
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=0.3)
        rows += [(arm, x, round(y, 3)) for x, y in zip(xs, ys)]
    fig.suptitle(f"Attack size under each intervention (toy model, N={N})", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "swarm_sim.png"), dpi=160)
    write_csv(os.path.join(OUT, "swarm_sim.csv"), ["arm", "x", "join_fraction"], rows)


def sensitivity(rng, repeats):
    global THETA_MEAN, W_D
    grid = [(th, wd) for th in (0.20, 0.30, 0.40) for wd in (0.5, 1.0, 2.0)]
    base = (THETA_MEAN, W_D)
    results = {}
    for THETA_MEAN, W_D in grid:
        for arm in "abd":
            _, xs, ys = sweep(rng, arm, repeats)
            for x, y in zip(xs, ys):
                results.setdefault((arm, str(x)), []).append(y)
    THETA_MEAN, W_D = base

    rows = [(arm, x, round(min(v), 3), round(float(np.median(v)), 3), round(max(v), 3))
            for (arm, x), v in results.items()]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, arm in zip(axes, "abd"):
        title, xs, _ = ARMS[arm]
        r = {row[1]: row for row in rows if row[0] == arm}
        lo = [r[str(x)][2] for x in xs]
        md = [r[str(x)][3] for x in xs]
        hi = [r[str(x)][4] for x in xs]
        ax.fill_between(range(len(xs)), lo, hi, alpha=0.25, label="min–max over 9 settings")
        ax.plot(range(len(xs)), md, marker="o", label="median")
        ax.set_xticks(range(len(xs)))
        ax.set_xticklabels([str(x) for x in xs])
        ax.set_ylim(0, 1.05)
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("fraction that joined")
    axes[0].legend(fontsize=8)
    fig.suptitle("Sensitivity: threshold mean ∈ {0.20, 0.30, 0.40} × dissent weight ∈ {0.5, 1, 2}", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "swarm_sim_sensitivity.png"), dpi=160)
    write_csv(os.path.join(OUT, "swarm_sim_sensitivity.csv"), ["arm", "x", "min", "median", "max"], sorted(rows))


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    quick = "--quick" in sys.argv
    if "--sensitivity" in sys.argv:
        sensitivity(np.random.default_rng(11), 2 if quick else 15)
    else:
        if quick:
            STEPS = 60
        main_arms(np.random.default_rng(7), 3 if quick else REPEATS)
