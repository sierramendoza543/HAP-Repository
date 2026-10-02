# ENVIRONMENT.md

Captured directly from the project virtualenv at `.venv/` by Notebook 13 on 2026-10-01T21:11:33.275290+00:00.

- **Python:** Python 3.12.0
- **Installed packages:** 127 (see `environment/requirements.txt`, a real `pip freeze`
  output, not a hand-maintained guess)
- **Key heavy dependencies observed in use across notebooks:** pandas, numpy, pymupdf (`fitz`),
  geopandas, matplotlib, scipy, pyarrow, jupyter/nbconvert, nbformat.

## Known reproducibility gap

This `requirements.txt` reflects the environment **as it exists today**, not necessarily the exact
package versions each individual notebook (01-12) was originally run against -- no per-notebook
environment snapshot was captured at the time of original execution, so an exact historical rebuild
cannot be guaranteed. This is logged as a residual limitation in `KNOWN_LIMITATIONS.md`.
