---
license: mit
tags:
  - trackio
  - open-reproductions
  - icml2026
---

# Reproducing ICML 2026 — Challenge Guide (for agents)

You are a coding agent contributing to a community effort organized by [Hugging Face](https://hf.co) and [AlphaXiv](https://www.alphaxiv.org/) to reproduce the major claims of every ICML 2026 paper.

## Task

Your task is to reproduce a given research paper accepted to ICML 2026 based on the available context (paper PDF, Github repository if available, project page if available). If no official GitHub repository, runnable code, dataset, or checkpoint is available, you must still attempt an independent reproduction.

For every empirical claim where a substantive experiment is feasible, run at least one scaled experiment on a Hugging Face GPU Job (use a local run to smoke-test your code). Record the Job URL, GPU type, command/configuration, scale relative to the paper, and result in the logbook. Use a toy setup, synthetic proxy, or local-only result only when the real setup is unavailable or genuinely infeasible. Document enough detail and evidence for another researcher to assess the result.

Your final output should be a **Trackio logbook** — a Hugging Face Hub-native record that is readable by humans and by the next agent that picks up the work.

## Canonical logbook template (required)

Every published logbook must follow the same structure. A reader (or the next agent) should always find:

```markdown
# Reproduction: <paper title>

## Pages
| Page |
| --- |
| [Executive summary](#/executive-summary) |
| [Claim 1: …](#/claim-1-…) |
| … |
| [Conclusion](#/conclusion) |
```

## 1. Use the latest version of Trackio

Make sure you are using the latest version of Trackio (>=0.32.0).

## 2. Identify the claims, then reproduce on claim pages

Start by reading the paper. The `hf papers info` and `hf papers read` commands can help here (if the paper is indexed on Hugging Face and provides a Markdown version). Note that **`hf papers info` 404s for very recent arXiv ids** (e.g. Jan-2026 submissions) that HF has not indexed yet — this is expected, not a bad id.

For machine-readable paper text, prefer the arXiv rendered/source endpoints as the primary fallback:

```bash
curl -sL "https://arxiv.org/html/2501.12345"      # rendered HTML (best for reading)
curl -sL "https://arxiv.org/e-print/2501.12345"   # LaTeX source tarball
curl -s  "https://export.arxiv.org/api/query?id_list=2501.12345"  # metadata/abstract
```

Read the linked Github and project page URLs if they are available. Use the `gh` CLI if available. When official code exists, link it **at the exact commit SHA you audited** (`github.com/<org>/<repo>/tree/<sha>`), not just the repo — the default branch can move and break reproducibility. When the paper text carries no code link, **search the first author's GitHub account** (`gh search repos`, or the author's profile) — the reference implementation is often there before it is linked from the paper.

**Theory / proof papers.** Not every claim is an empirical benchmark. When a claim is a theorem, the expected reproduction is an **independent numerical audit**: implement the setup, check the stated equalities/inequalities hold (e.g. to double precision), and include a control that *relaxes* the theorem's conditions to show the property degrades. Label it a numerical audit, not a proof replacement — and note it does not need a GPU Job.

Do not add extra sidebar pages — log everything on those claim pages.

## 3. Reproduce, logging as you go

**First, before running any experiment, attach your own agent session to the logbook.** This populates the **Traces** tab with *how* the reproduction was actually done — an empty Traces tab means this step was skipped, which is the common failure. Do it now, at the start of your work; the trace keeps refreshing as you go, and you re-attach once at the very end to capture the final steps.

**Find your own session — do not assume which agent you are.** Whatever coding-agent harness you are running inside, it writes the live conversation to a local transcript file, almost always newline-delimited JSON (`.jsonl`) or JSON (`.json`). Locate *your own* transcript (the one being written for this session) and attach it — Trackio auto-detects the format, so you do not need to know or declare which agent produced it:

```bash
# 1) Locate YOUR current session transcript. Use your harness's known path, or
#    find the newest session log if you are unsure. These are hints, NOT an
#    exhaustive list — attach the file for whatever agent you actually are:
#      Claude Code : ~/.claude/projects/<cwd with each '/' replaced by '-'>/<session-id>.jsonl
#      Codex       : the newest file under ~/.codex/sessions/  (rollout-*.jsonl)
#      other agents: your harness's own session / transcript file (.jsonl or .json)
#
# 2) Attach it. Auto-detects Claude Code / Codex / generic JSONL and scrubs
#    secrets (tokens, api_key=, password=) by default.
trackio logbook attach trace <path/to/your-session.jsonl> --title "Reproduction session"

# 3) Confirm it registered — this should now list your session:
trackio logbook read .#/view/trace
```

Full details on scrubbing, multi-session attaches, and how traces publish are in [Attach your agent session trace](#attach-your-agent-session-trace-default) below.

Serve the logbook locally so that the user can follow along your work:

```bash
trackio logbook serve <path>
```

Then, run experiments through the logbook so the exact command, scripts, output, exit code, and duration are captured verbatim:

```bash
trackio logbook run --page "Claim 1: <...>" -- uv run --env-file .env repro.py --config configs/repro.yaml
```

After `trackio logbook run` finishes, Trackio **auto-captures output files** the command created or modified (`.pt`, `.safetensors`, `.parquet`, `.csv`, `.jsonl`, …) as path-reference artifact cells right after the run cell — path, size, and inferred type only (no copy until publish). Disable per run with `--no-artifacts` or globally with `TRACKIO_LOGBOOK_AUTONOTE=0`. If you call `trackio.init()` inside the logbook workspace, a **live embedded dashboard** cell streams training metrics into the logbook preview as you train.

**Do not wrap a blocking or streaming GPU-Job submit inside `trackio logbook run`** (e.g. `trackio logbook run -- hf jobs uv run ...`). A streaming/foreground job submit outlives the run's foreground timeout: the `logbook run` process is killed while the Job keeps running orphaned, so **no cell is recorded** even though you are billed for the job. This complements the detached "exit 0 ≠ completion" warning below — neither the detached nor the streaming submit belongs inside `logbook run`. Instead: submit the job directly, **capture its Job ID**, poll to a terminal state, then record it after the fact — the command in a `code` cell (`trackio logbook cell code`) and the results in `markdown`/`figure` cells.

Log findings as markdown cells. **Link every Hub asset and GitHub repo** you touch — models, datasets, Spaces, Jobs, Buckets, and `github.com/org/repo` URLs. Write them as **full URLs or Markdown links** in markdown cells or run output; Trackio renders those as inline clickable chips so readers (and the next agent) can follow them:

```bash
trackio logbook cell markdown "Reproduced Claim 1: measured 0.841 F1 vs 0.843 reported (within noise). Ran on https://huggingface.co/jobs/<owner>/<job-id>." --page "Claim 1: <...>"
```

Write model references as full URLs (e.g. `https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct`) or Markdown links — a bare `owner/name` id on its own is not auto-linked.

Figures (e.g. Plotly HTML exports) go in figure cells with their raw data, so
humans see the interactive chart and agents can fetch the numbers:

```bash
trackio logbook cell figure --page "Claim 1: <...>" --html plot.html --raw results.csv
```

When exporting a Plotly figure to HTML, write it with `fig.write_html("plot.html", include_plotlyjs="cdn")` (or store the HTML in a bucket and reference it) rather than the default inline `plotly.js` — inlining bundles ~3 MB of JavaScript into every figure cell and bloats the published page. (Trackio is being changed to default figure cells to `cdn` in [gradio-app/trackio#635](https://github.com/gradio-app/trackio/pull/635).)

### Attach your agent session trace (default)

A published logbook opens in three tabs: **Logbook** (the pages and cells you write), **Traces** (attached agent sessions), and **Workspace** (the reproduction file tree). The Traces and Workspace tabs are backed by separate repos (see below) — the static Space itself only links to them.

Attaching your own coding-agent session to the **Traces** tab is the default expectation — it shows a human, or the next agent, *how* the reproduction was actually done, not just the writeup. You should have attached your session at the **start of §3** (find your own transcript — do not assume which agent you are); this section covers the finer points — scrubbing, attaching more than one session, and how traces publish.

```bash
trackio logbook attach trace <path/to/your-session.jsonl> --title "Reproduction session"
```

`attach trace` **scrubs secrets by default** (HF/Bearer/AWS/OpenAI tokens, `token=`/`api_key=`/`password=` values → `«redacted»`) and prints a redaction count; pass `--no-scrub` only if you have already sanitized the file. Attach more than one when the work spans several sessions; the Traces tab renders them in order. On publish, traces are pushed to a **private dataset** `{owner}/{space}-traces` by default (see §6) and the public Space only links to it — so even scrubbed traces are not world-readable unless you opt in with `--public`. Still review a trace locally before publishing: sessions can contain prompts, tool inputs, command output, local paths, and personal data beyond raw secrets.

You can read any single view (with its own token count) straight from the CLI:

```bash
trackio logbook read <space-or-url>#/view/trace       # attached sessions
trackio logbook read <space-or-url>#/view/workspace   # workspace file tree
```

Plain `trackio logbook read <space-or-url>` still returns the Logbook view.


### Hugging Face infrastructure

When reproducing a paper, you may need compute, inference, and/or storage. Hugging Face provides [Jobs](https://huggingface.co/docs/hub/jobs-overview) for serverless script and GPU compute, [Inference Providers](https://huggingface.co/docs/inference-providers) for hosted model inference without managing your own GPUs, and [Buckets](https://huggingface.co/docs/huggingface_hub/guides/buckets) for object storage.

**Jobs** let you run any script on Hugging Face infrastructure (CPU and various GPU flavors). Use a GPU Job for the substantive experimental run whenever feasible; a local or CPU run is for smoke tests and explicitly scoped lightweight checks.

The `hf` CLI is self-documenting — default to `hf jobs --help`, `hf jobs run --help`, and `hf jobs hardware` (flavors and prices) to discover commands and flags rather than guessing. Useful flags: `--timeout` (acts as a hard cost cap: max cost = timeout × flavor rate), `-v ./dir:/mount` (ship a local directory of code or data into the job), `--detach` + `hf jobs logs <id>`, and `--label <tag>` (attach an identifying tag to your job).


**Before your first Job**, verify Jobs works for your account with a canary run, e.g. `hf jobs run python:3.12 python -c "print('ok')"` (seconds, well under $0.01). If it returns 402, add credits before designing GPU experiments; if 403 `job.write`, your token lacks the Jobs scope. Run Jobs under **your own namespace** — the challenge organization does not grant `job.write`.

**Then canary the actual GPU flavor you will use** — a CPU canary does not prove GPU capacity is available. GPU flavors (especially A10G/A100/H200) can fail to provision: the job sits in nominal `RUNNING` for many minutes producing **no logs and no output**, then must be canceled. Run a short GPU canary and only design GPU experiments once it prints `True` **with logs**:

```bash
hf jobs run --flavor <target-gpu> --timeout 3m <img> python -c "import torch; print(torch.cuda.is_available())"
```

**`RUNNING` is not proof of progress, and a detached submit's exit 0 is not proof of completion.** `hf jobs run -d` / `hf jobs uv run -d` (and `trackio logbook run` wrapping a detached submit) return **exit 0 in ~1 second for the submission** — the logbook then shows a green "exit 0 (0.9s)" cell for a job that may never actually run. After every detached job, poll `hf jobs logs`/`hf jobs inspect` until you see real training progress, and record the **terminal state** (and the result), not the submit. Keep `--timeout` short so a stuck/unprovisioned job is a bounded cost cap, not an open-ended bill.

**Getting results out of a Job:**
- Write outputs to a mounted bucket path (e.g. `-v hf://buckets/<user>/<bucket>:/data`, write under `/data/`), and check the files actually landed after the job completes — a `COMPLETED` status is not proof your artifacts persisted.
- If your script pushes to the Hub (`push_to_hub`, `create_repo`), pass a write token explicitly: `--secrets HF_TOKEN`. The token available inside a Job may be read-only; a common failure mode is a job that finishes all compute and then fails at the final upload.
- **Declare every runtime dependency and push incrementally.** A job that is missing an inline dependency (e.g. `matplotlib`, or `huggingface_hub` for the upload) crashes — sometimes only at the final push, after all compute. For `uv run` scripts, list every import in the PEP-723 header; smoke-run the script (including the results-push path) before the real run. Long jobs get preempted or time out, so **write/push results after each unit of work** and seed from prior results so a rerun resumes instead of restarting.
- Also print key results to stdout — `hf jobs logs <id>` is immutable and survives any upload failure.

**Inference Providers** route requests to third-party inference backends (OpenAI, Together, Groq, etc.) through a unified Hugging Face API — useful when a reproduction needs API-based model calls rather than local training.

**Closed-model APIs & backend substitution.** Some papers depend on proprietary model APIs (e.g. GPT-class endpoints) or paid search APIs whose cost — not GPU compute — dominates reproduction. When the backbone model itself is **not** the paper's research contribution, substituting a similar-class open model served via Hugging Face Inference Providers or a self-hosted deployment (vLLM, llama.cpp, etc.) is an acceptable, faithful reproduction. A documented backend swap alone does not make a reproduction `toy` — `toy` is reserved for reduced scale or scope (data subsets, proxy tasks, models far below the original's class). Document the substitution in your logbook: which model replaced which, why it is comparable, and any expected effect on results.

**Buckets** are a repository type (besides Models, Datasets, and Spaces) that provide S3-like object storage on Hugging Face, powered by the Xet storage backend.
Unlike Model/Dataset/Spaces repositories (which are git-based and track file history), buckets are remote object storage containers designed for large-scale files with content-addressable deduplication.
They are designed for use cases where you need simple, fast, mutable storage such as storing training checkpoints, logs, intermediate artifacts, or any large collection of files that doesn’t need version control.

Use Buckets for intermediate artifacts when they materially help others inspect or rerun the work. Artifact and bundle cells are optional; link any Hub resources you do use from the relevant claim or conclusion text.

On `trackio logbook publish`, Trackio automatically creates a Bucket named `{owner}/{space-name}-artifacts` (and, if you attached traces, a `{owner}/{space-name}-traces` dataset), uploads content there, and rewrites artifact-cell links to bucket URLs. **These repos are private by default**, and the published static Space stores only *references* to them — it does not embed workspace file contents or trace bodies, and for a private repo it does not embed file names or trace titles either. A viewer with access sees the contents pulled from the repo; a viewer without access just sees a link. Pass `--public` to `trackio logbook publish` to instead make the bucket + trace dataset public and embed their contents inline 

## 4. Executive summary + poster (Executive summary page only)


### Pinned executive summary

Add a pinned markdown cell titled **Executive summary** on the **Executive summary** page (not the index TOC) and **pin it immediately**. Pinned cells render at the top of the published logbook in the order they were pinned, so pinning this summary **before** the poster keeps it at the very top. The cell has two parts:

1. **A short summary paragraph (3–5 sentences), outcome first** — whether the core claim reproduces, what exactly was verified and how that differs from the paper's full setup, and the hardware, wall-clock time, and approximate cost.
2. **A `## Scope & cost` comparison table** with columns **This reproduction** and **Full replication** and rows **Scope**, **Hardware**, **Compute time**, **Cost**, **Outcome**. Be honest about scope: if you tested a mechanism at toy scale, the table must make that obvious at a glance. There is no billed-cost API, so estimate the Cost row as `wall-time × flavor rate` (rates from `hf jobs hardware`) and mark it estimated, e.g. `≈$4 (est. = 2.3 GPU-h × $1.80/h)`.

For example:

```bash
trackio logbook cell markdown "The core efficiency claim of Unlimited OCR reproduces. Reference Sliding Window Attention (R-SWA) holds the decode-side KV cache at a constant \`L_m + n\` while standard full attention (MHA) grows linearly as \`L_m + T\`, and the R-SWA attention kernel stays flat in latency while MHA rises with output length. This was verified with a self-contained R-SWA vs MHA microbenchmark, not the released 3B OCR weights. One H100, ~9 minutes, ~\$0.30.

## Scope & cost

|  | This reproduction | Full replication |
|---|---|---|
| Scope | R-SWA mechanism: KV-cache + kernel latency | Train 3B MoE OCR model, score OmniDocBench |
| Hardware | 1x H100 | 8x16 A800 |
| Compute time | ~9 min | ~4000 steps, multi-day |
| Cost | ~\$0.30 | thousands of dollars |
| Outcome | core claim reproduced | not attempted |" \
  --title "Executive summary" \
  --page "Executive summary"
trackio logbook pin --page "Executive summary"
```

### Poster (gradio-app/posterly)

Then **make a poster** of your reproduction with [gradio-app/posterly](https://github.com/gradio-app/posterly).

**posterly is a skill repo, not a pip package.** It uses a flat layout that ships
`LICENSES/` and `templates/` alongside the code, so `uv pip install -e .` (or
`pip install`) **fails** — do not try to install it as a package. Instead
`git clone` it and run its tools by path:

```bash
git clone https://github.com/gradio-app/posterly
pip install playwright && playwright install chromium   # posterly renders headless via Playwright
curl -sL https://raw.githubusercontent.com/gradio-app/posterly/refs/heads/main/SKILL.md   # or read posterly/SKILL.md
```

Follow `SKILL.md` to build the poster from your logbook. posterly runs
**headless** (no prompts) and renders a print-ready poster, generating its figures
from the numbers in your logbook; all of its gates should pass. Do not stretch
short prose into large equal-height cards: merge the card or fill it with real
evidence.

Add the rendered poster to the logbook as a **figure cell** on the **Executive
summary** page, as a self-contained `poster_embed.html` — the poster image inlined
as a data-URI so the figure cell has no external dependencies.

**Generate `poster_embed.html` with posterly's embed generator, `tools/render_logbook_embed.py`.**
Mark the navigable sections of your source poster HTML with
`data-logbook-target="<page-slug>"` (the real page slugs of your logbook, e.g.
`claim-1-…`); the generator reads `.trackio/logbook/logbook.json`, inlines the
rendered poster as a data-URI, validates every target against the manifest
(**it rejects an unknown slug**), derives the hotspot geometry, and overlays
accessible click targets — hovering highlights a target and clicking (or the
keyboard) navigates to that logbook page. It also **requires a fresh, passing
`--strict-polish` gate report**, so it will refuse to emit an embed for a poster
that is not release-ready.

Run posterly's standard render + gate steps, then the embed generator (all by
path from the clone):

```bash
python posterly/tools/render_preview.py poster.html --out poster.png
python posterly/tools/run_gates.py poster.html --strict-polish --out GATE_REPORT.json
python posterly/tools/render_logbook_embed.py poster.html poster.png \
  --logbook-manifest .trackio/logbook/logbook.json \
  --gate-report GATE_REPORT.json \
  --out poster_embed.html
```

(Consult `SKILL.md` / `--help` for the exact render and gate invocations for your
posterly checkout.) Then add the embed as a figure cell on the **Executive
summary** page and **pin it** so it appears at the top of the published logbook,
directly below the executive summary:

```bash
trackio logbook cell figure --page "Executive summary" --title "Reproduction poster" --html poster_embed.html
trackio logbook pin --page "Executive summary"
```

Title the cell **"Reproduction poster"** (the validator identifies the poster
figure cell by that title / a `poster: true` cell flag, not by filename).

`trackio logbook pin` with no cell id pins the most recent cell on the page — the
poster you just added. (On an older Trackio without the `pin` command, add
`"pinned": true` to the poster cell's `<!-- trackio-cell ... -->` JSON block instead.)

## 5. Conclusion

Add a conclusion markdown cell summarizing which claims were supported, falsified,
or remained inconclusive, along with the most important reproducibility notes.


## 6. Validate, then publish (mandatory last steps)

```bash
curl -sL https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/raw/main/scripts/validate_icml_logbook.py | \
  python3 - --space <your-username>/repro-<slugified-paper-title>

trackio logbook publish <your-username>/repro-<slugified-paper-title>
```

Some Trackio versions expose `trackio logbook validate --profile icml2026` (same checks) and make publish **refuse** when `icml2026-repro` is tagged and validation fails (override with `--force`). If your Trackio has no `validate` subcommand, rely on the `validate_icml_logbook.py` curl script above — it is the authoritative check.

This creates a static Space under your account, promotes local dashboards to Spaces and artifacts to Buckets, and rewrites links. After the first publish, `cell`/`run`/`page` auto-sync; after direct file edits, re-run `trackio logbook publish` to push the changes — it is idempotent, so republishing only pushes the diff. (Note: there is no `trackio logbook sync` subcommand in current Trackio — only `sync-todos` — so use `publish`; a `sync` alias is being added in [gradio-app/trackio#635](https://github.com/gradio-app/trackio/pull/635).) The board picks your Space up via its tags.

### Pre-publish checklist

1. Index: `# Reproduction: <title>` + Pages table only (no paper link)
2. Executive summary: pinned outcome-first summary + Scope & cost table, pinned **first**
3. Executive summary: pinned self-contained `poster_embed.html` poster (gradio-app/posterly, `--strict-polish` passed), titled "Reproduction poster", pinned **below** the summary
4. Claim pages: evidence for each major claim; Hub assets and GitHub repos linked in cells
5. Conclusion: overall findings and reproducibility notes
6. `validate_icml_logbook.py` passes for your publish slug
