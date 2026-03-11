# E2E Topic Modeling — Python Research Pipeline

**A BERTopic and Large Language Model Pipeline for Topic Discovery and Classification**

This is the Python research implementation of the Embedding-to-Explanation (E2E) topic modeling methodology. It combines transformer-based topic modeling (BERTopic) with large language model (LLM) interpretation and classification to produce human-interpretable, reproducible thematic analyses of any text corpus.

> **Note:** For the browser-based version of this methodology (no coding required), see the [E2E Topic Modeler web app](../e2e-topic-modeler/).

## The Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Embedding & Clustering (BERTopic)                  │
│  ┌──────────┐  ┌──────┐  ┌─────────┐  ┌────────┐  ┌─────┐ │
│  │ Embed    │→ │ UMAP │→ │ HDBSCAN │→ │ TF-IDF │→ │ c_v │ │
│  │(MiniLM)  │  │      │  │         │  │        │  │score│ │
│  └──────────┘  └──────┘  └─────────┘  └────────┘  └─────┘ │
│  × N iterations × M topic solutions = best model           │
├─────────────────────────────────────────────────────────────┤
│  STAGE 2: LLM Democratic Topic Naming                       │
│  For each topic: prompt LLM K times → majority vote → name  │
├─────────────────────────────────────────────────────────────┤
│  STAGE 3: LLM Corpus Classification                         │
│  For each document: prompt LLM → classify into theme        │
│  Validated against human-labeled subset (>85% agreement)    │
└─────────────────────────────────────────────────────────────┘
```

## E2E Methodology Comparison

| Component | Python Pipeline (this) | Web App (e2e-topic-modeler) |
|-----------|----------------------|---------------------------|
| **Embeddings** | SentenceTransformer (all-MiniLM-L6-v2) | Voyage AI (voyage-3) |
| **Dim. Reduction** | UMAP | N/A (K-means on full vectors) |
| **Clustering** | HDBSCAN | K-means + cosine similarity |
| **Topic Extraction** | Class-based TF-IDF | TF-IDF (term extraction only) |
| **Topic Naming** | GPT-4o (5,000 votes) | Claude (5 votes) |
| **Classification** | GPT-4o | Claude |
| **Optimization** | 50 iterations × 24 solutions | Silhouette score for k |

## Installation

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install bertopic sentence-transformers umap-learn hdbscan gensim nltk scikit-learn openai pandas numpy matplotlib tqdm
```

## Quick Start

### Python API

```python
from e2e import E2EPipeline

# Initialize
pipeline = E2EPipeline(
    domain_context="tweets about public health",
    n_iterations=10,    # 50 for full optimization
    n_votes=50,         # 5000 for full democratic naming
)

# Run on your corpus
documents = ["your", "list", "of", "text", "documents"]
results = pipeline.run(documents)

# Classify a broader corpus
labels = pipeline.classify(more_documents)

# Validate against human labels
validation = pipeline.validate_classifier(
    sample_texts, human_labels, threshold=0.85
)

# Save results
pipeline.save("output/")
```

### Command Line

```bash
# Full pipeline
e2e run data.csv \
    --text-column "text" \
    --domain-context "social media posts about health" \
    --n-iterations 50 \
    --n-votes 100 \
    --output-dir results/

# Classify with known themes
e2e classify data.csv \
    --text-column "text" \
    --themes "Health" "Politics" "Sports" \
    --output classified.csv
```

### Using Individual Components

```python
from e2e.preprocessing import preprocess_corpus
from e2e.modeling import TopicModeler
from e2e.naming import TopicNamer
from e2e.classifier import TopicClassifier

# Stage 1: Preprocessing
docs = preprocess_corpus(raw_documents, custom_stopwords={"brandname", "rt"})

# Stage 2: Topic Modeling
modeler = TopicModeler(n_iterations=50, topic_range=(2, 26))
result = modeler.optimize(docs)
print(f"Best model: {result.best_result.n_topics} topics, coherence={result.best_result.coherence:.4f}")

# Stage 3: Topic Naming
namer = TopicNamer(n_votes=100, domain_context="social media posts")
topic_words = {tid: [w for w, _ in result.best_model.get_topic(tid)]
               for tid in result.best_model.get_topics() if tid != -1}
names = namer.name_all_topics(topic_words)

# Stage 4: Classification
themes = [names[tid]["name"] for tid in sorted(names)]
classifier = TopicClassifier(themes=themes)
labels = classifier.classify_corpus(all_documents)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `embedding_model` | `"all-MiniLM-L6-v2"` | SentenceTransformer model |
| `n_iterations` | `50` | Hyperparameter search iterations |
| `topic_range` | `(2, 26)` | Min/max topic count to evaluate |
| `n_votes` | `100` | LLM naming votes per topic |
| `llm_model` | `"gpt-4o"` | OpenAI model for naming/classification |
| `temperature` | `0.5` | LLM sampling temperature |
| `random_seed` | `None` | Seed for reproducibility |

## Environment Variables

- `OPENAI_API_KEY`: Required for Stages 2 and 3 (LLM naming and classification).

## Citation

```bibtex
@phdthesis{thomas2025e2e,
  title={Embedding-to-Explanation Topic Modeling: A Hybrid Approach for Interpretive Text Analysis},
  author={Thomas, Jacob Edward},
  year={2025},
  school={The University of Texas at Austin}
}
```

## License

MIT License. See [LICENSE](LICENSE).
