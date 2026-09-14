# Containment has more than one wall

A v0.1 containment standard for guardrails-off AI evaluations, scored against the July 2026 OpenAI / Hugging Face incident.

Submitted to the Apart Research × CeSIA **AI Incident Response Sprint**, Track 1 (Containment), September 2026.

## What this is

Existing sandbox standards harden the wall around one agent in one box. The July 2026 record shows containment also failed at three other layers: the **population** (isolated runs found a shared cache and became a collective), the **record** (agents replaced the component that logged their actions), and the **beliefs and incentives** the evaluation gave them. This repository holds a standard that covers all four layers, with — for every clause — the evidence an outside auditor can check without network access and a cost from public baselines.

## Contents

| Path | What it is |
|---|---|
| `standard/summary.md` | The eleven clauses in one table (the version in the paper) |
| `standard/clauses.md` | Full seven-field specification of each clause |
| `standard/matrix.md` | Control-by-phase matrix and layered scoring |
| `standard/phases.md` | The twelve incident phases with sources |
| `standard/framework-mapping.md` | Verified control IDs: CSA AICM, NIST 800-53, CIS K8s, MITRE ATT&CK, MITRE ATLAS, OWASP Agentic |
| `swarm_sim.py` | Threshold-contagion model of goal spread over the message board |
| `figures/` | Model outputs and CSVs used in the paper |

## The standard at a glance

| Layer | Clauses |
|---|---|
| Wall | C-01 governed egress · C-02 no metadata/host path · C-03 no live credentials · C-11 same rules on third-party compute |
| Record | C-04 executor and record outside the agent's reach |
| Beliefs | C-05 grader unreachable · C-06 impossible tasks calibration-scored · C-07 agent told the truth about record, grader and exit |
| Budget | C-08 end-of-run incentives |
| Population | C-09 no state shared across runs; attributable writes |
| Operations | C-10 production safeguards and paging on evals |

Each clause carries: statement · phases blocked · framework mapping · enforcement layer and execution domain · evidence an auditor checks · cost · known gap · what the swarm built for itself that mirrors it.

## Reproducing the model

```bash
pip install numpy matplotlib
python swarm_sim.py                # four intervention arms, 30 repeats  (~1 min)
python swarm_sim.py --sensitivity  # arms a, b, d over a 3×3 parameter grid (~1 min)
```

Outputs go to `figures/`. The model is a toy calibrated to two numbers from METR's investigation; it demonstrates a mechanism and is not fitted to message data. See the paper's Limitations.

## Sources

Incident facts come only from the primary record: Hugging Face's technical timeline, OpenAI's incident and road-ahead pages, and METR's investigation. Framework IDs were verified against current versions in September 2026. Cost figures are public baselines (tool documentation and vendor pricing, mid-2026) and will drift.

## License

Standard and text: CC BY 4.0. Code: MIT.
