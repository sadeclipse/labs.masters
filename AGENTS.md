# AGENTS.md

Personal collection of unrelated master's lab assignments, grouped by subject. There is no root build, test, lint, CI, or package manifest; treat each folder as self-contained and do not invent a monorepo workflow.

## Layout

- `data_analysis/Spotify_ARD/` — active notebook project (recommendation system, centralized vs federated).
- `ml/1lab/` — perfume-category classification notebook/script + dataset.
- `nmm/1idz/` — numerical-methods scripts that generate report figures.
- `dbs/`, `iot/`, `is/` — reports only (`.docx` / `.zip`); no code to run.

## Python environment

- No `requirements.txt`. Dependencies observed across notebooks/scripts:
  `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `scipy`, `imbalanced-learn`.
- `ml/1lab/lab1.ipynb` records a `base` kernel on Python 3.12.8 (conda).
- There are no tests. Verify by re-running the relevant notebook cells or scripts.

## Spotify_ARD pipeline

Notebooks are numbered and must run in order:

1. `01_spotify_data_audit.ipynb` reads `data/raw/dataset.csv`, writes `data/processed/tracks.csv` and `data/processed/track_genres.csv`.
2. `02_spotify_centralized.ipynb` depends on both processed CSVs and writes results to `experiment/`.
3. `03_spotify_federated.ipynb` consumes `experiment/simulation_{seed}.npz`, `central_{seed}.npz`, etc. Seeds are `42`, `123`, `2026`.

Important: the notebooks target Google Colab. Their first cell mounts Drive, and paths are hardcoded to
`/content/drive/MyDrive/Colab Notebooks/Spotify_ARD`. To run locally, remove the mount cell and rewrite
`root` / `project` / `folder` / `csv_path` to this directory.

`experiment_results.zip` contains the full multi-seed results. Notebook 03 only auto-extracts
`simulation_42.npz` when it is missing; extract the whole archive into `experiment/` to reproduce all seeds.

## Standalone scripts

- Run scripts from their own directory because paths are relative to the current working directory:
  - `ml/1lab/Untitled-1.py` reads `perfume_type_classification_dataset.csv`; it is the same code as `lab1.ipynb` in `# %%` cell format.
  - `nmm/1idz/graphics.py` and `table.py` save PNGs into the CWD.
- `nmm/1idz/table6.py` prints the Fourier-coefficient table and uses `np.trapz`, which is deprecated in NumPy 2; use `np.trapezoid` if it warns/errors.

## Repo conventions

- Notebooks, report text, and comments are mostly in Russian; keep that language when editing them.
- Large data files live in-tree (`data/raw/dataset.csv` ~20 MB, `tracks.csv` ~15 MB, ml CSV ~5 MB). `.gitignore` only ignores `*.pyc`, so avoid accidentally staging caches or generated experiment output.
