# Dissertation Repository

**Jacob Edward Thomas, PhD — The University of Texas at Austin**

This repository contains the research tools, deliverables, and source materials for a mixed-methods dissertation on alcohol industry marketing history and computational text analysis.

## Projects

### [E2E Topic Modeler](e2e-topic-modeler/) — Web App

A browser-based implementation of the Embedding-to-Explanation (E2E) topic modeling methodology. Deployed on Cloudflare Pages. Upload a CSV of text documents and the tool will:

1. **Embed** documents into dense semantic vectors using Voyage AI (voyage-3)
2. **Cluster** embedding vectors using K-means with cosine similarity
3. **Name** discovered topics using Claude with democratic voting (5 votes, majority wins)
4. **Classify** all documents into the discovered topics using Claude

**Stack:** HTML/CSS/JS, Cloudflare Pages + Pages Functions, Voyage AI, Claude API

### [E2E Python Pipeline](topic_flow/) — Research Implementation

The production-grade Python implementation of the same E2E methodology, used for the dissertation research. Combines BERTopic with LLM interpretation for research-quality results with hyperparameter optimization across 1,200 candidate models.

**Stack:** Python, BERTopic, SentenceTransformer, UMAP, HDBSCAN, OpenAI GPT-4o

## E2E Methodology

Both implementations follow the same core methodology described in the dissertation:

```
Documents → Embed → Cluster → LLM Name (democratic voting) → LLM Classify
```

| Stage | Web App | Python Pipeline |
|-------|---------|----------------|
| Embedding | Voyage AI (voyage-3) | SentenceTransformer (all-MiniLM-L6-v2) |
| Clustering | K-means + silhouette | HDBSCAN + UMAP + c_v coherence |
| Naming | Claude (5 votes) | GPT-4o (5,000 votes) |
| Classification | Claude | GPT-4o |

## Deliverables

Generated research outputs in `deliverables/`:

| File | Description | Generator |
|------|-------------|-----------|
| `the_drinking_age.docx` | Popular history book on alcohol marketing | `generate_book.py` |
| `topicflow_methods_paper.docx` | E2E methodology paper | `generate_methods_paper.py` |
| `brief_report_study1.docx` | Study 1 brief report | `generate_brief_report_1.py` |
| `brief_report_study2.docx` | Study 2 brief report | `generate_brief_report_2.py` |
| `email_to_pasch.docx` | Publication discussion email | `generate_email.py` |
| `dissertation_dissection.html` | Interactive dissertation breakdown | — |

## Source Material

- `THOMAS-PRIMARY-2025.pdf` — Original dissertation document
- `dissertation_full.txt` — Full text extraction

## Citation

```bibtex
@phdthesis{thomas2025dissertation,
  title={A Mixed-Methods Study of Alcohol Industry Marketing},
  author={Thomas, Jacob Edward},
  year={2025},
  school={The University of Texas at Austin}
}
```
