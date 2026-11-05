# SETUP.md — what YOU install (so the agent doesn't waste tokens on it)

## 1. Tools
- Python 3.10, 3.11 or 3.12 (check: python --version)
- Git (check: git --version) and a GitHub account
- A code agent: Antigravity or Codex (either works; both start from AGENTS.md)
- Optional: GitHub CLI (gh) to make auth easy

## 2. Repo and virtual environment
```bash
mkdir lensed-agn-detection && cd lensed-agn-detection
git init
python -m venv .venv
# activate:   Windows: .venv\Scripts\activate      Mac/Linux: source .venv/bin/activate
```
Copy ALL the files from this folder into the repo root (AGENTS.md, STATE.md, DECISIONS.md,
requirements.txt, docs/, skills/).

## 3. Python packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
If you have an NVIDIA GPU locally, install torch from the selector at pytorch.org instead of the
default. Most laptops: the default CPU build is fine for development.
Verify:
```bash
python -c "import torch, astropy, sklearn; print(torch.__version__, torch.cuda.is_available())"
```

## 4. GitHub remote
Create an empty repo named lensed-agn-detection on GitHub, then:
```bash
git remote add origin https://github.com/<you>/lensed-agn-detection.git
git branch -M main
git add -A && git commit -m "init: agent files" && git push -u origin main
```
Make sure you are logged in (gh auth login, or a personal access token) so the agent's pushes work.

## 5. Data
1. Download the SMALL dataset first (about 350 MiB uncompressed) from the challenge site.
2. Unzip into data/raw/ inside the repo (data/ is gitignored by Phase 0, but create .gitignore first
   if you download before running the agent: put "data/" in it).
3. Set the data path (the code reads this, never hard-codes paths):
```bash
# Mac/Linux
export LENS_DATA_ROOT="$(pwd)/data/raw"
# Windows PowerShell
$env:LENS_DATA_ROOT = "$PWD\data\raw"
```
4. Only after Phases 1-4 work, download more: either the main dataset (about 17 GiB) or the
   individual-band sets (about 3.5 GiB each). Remember: small and per-band sets are subsets of main,
   so do not mix them in one experiment.
5. Check free disk space before the big download.

## 6. GPU for training (Colab)
Develop locally on the small dataset. Run long trainings on Colab or Kaggle with a free GPU.
- Colab: Runtime > Change runtime type > GPU.
- In a notebook: clone your repo, pip install -r requirements.txt, set LENS_DATA_ROOT, run
  python src/train.py --config configs/<file>.yaml.
- Colab's disk is wiped between sessions, so keep the dataset zips on Google Drive and unzip each session.
- Simplest result sync: copy results/ and figures/ from Colab back into your local repo, then let the agent commit.
- The agent will write docs/COLAB_RUN.md with ready-to-paste cells when a run is too slow locally.

## 7. Start the agent
Open the repo folder in Antigravity or Codex. First message:
"Read AGENTS.md and STATE.md. Then do phase 0."
If your agent does not auto-load AGENTS.md, that first message is enough. If it wants a different
filename, copy AGENTS.md to that name (for example GEMINI.md or CLAUDE.md).

## 8. Troubleshooting
- Import error for astropy/torch: the venv is not activated.
- Push rejected: log in to GitHub (gh auth login) and retry.
- Out of memory on Colab: lower batch_size in the YAML, or use fewer objects.
- Slow data loading: ask the agent for the Phase 2 cache of the subset you use.
