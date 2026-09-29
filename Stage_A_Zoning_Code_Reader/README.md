# Stage A — Zoning Code Reader

Stage A builds a traceable district evidence-bundle table from municipal zoning-code documents

## Purpose

The pipeline processes an official zoning-code PDF and produces structured, source-linked evidence for each zoning district, including:

- primary district text
- resolved cross-references
- applicable townwide provisions
- matched dimensional-table rows
- base versus overlay classifications
- source-page and excerpt provenance
- collection confidence and review status

## Initial jurisdiction

Town of Greenwich, Connecticut.

## Project structure

- `data/raw/`: immutable original source documents
- `data/interim/`: regenerable intermediate extraction artifacts
- `data/processed/`: cleaned structured datasets
- `notebooks/`: implementation and validation notebooks
- `outputs/`: figures, tables, logs, and manual-review materials
- `src/`: reusable pipeline code
- `tests/`: validation tests

## Source handling

Raw PDFs are not committed to Git. Instead, the notebook stores source URLs, retrieval dates, document-version metadata, and SHA-256 hashes