# Dissertation Repository

**Jacob Edward Thomas, PhD — The University of Texas at Austin**

This repository contains the research tools, deliverables, and source materials for a mixed-methods dissertation on alcohol industry marketing history and computational text analysis.

## Projects

### [E2E Topic Modeler](e2e-topic-modeler/)

A browser-based topic modeling tool deployed on Cloudflare Pages. Upload a CSV of text documents and the tool will:
1. Embed and cluster documents using TF-IDF + K-means (runs locally in your browser)
2. Name discovered topics using Claude with democratic voting
3. Classify all documents into the discovered topics

**Stack:** HTML/CSS/JS, Cloudflare Pages + Pages Functions, Claude API

### [TopicFlow](topic_flow/)

A production-grade Python pipeline for topic discovery and classification. Combines BERTopic with LLM interpretation for research-quality results.

**Stack:** Python, BERTopic, SentenceTransformer, OpenAI GPT-4o

## Deliverables

Generated research outputs in `deliverables/`:

| File | Description | Generator |
|------|-------------|-----------|
| `the_drinking_age.docx` | Popular history book on alcohol marketing | `generate_book.py` |
| `topicflow_methods_paper.docx` | TopicFlow methodology paper | `generate_methods_paper.py` |
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
