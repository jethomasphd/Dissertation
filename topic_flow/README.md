# TopicFlow

**A BERTopic and Large Language Model Pipeline for Topic Discovery and Classification**

TopicFlow is a three-stage methodology for automated topic discovery in text corpora. It combines transformer-based topic modeling (BERTopic) with large language model (LLM) interpretation and classification to produce human-interpretable, reproducible thematic analyses of any text corpus.

## The Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: BERTopic with Hyperparameter Optimization         │
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
from topicflow import TopicFlowPipeline

# Initialize
pipeline = TopicFlowPipeline(
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
topicflow run data.csv \
    --text-column "text" \
    --domain-context "social media posts about health" \
    --n-iterations 50 \
    --n-votes 100 \
    --output-dir results/

# Classify with known themes
topicflow classify data.csv \
    --text-column "text" \
    --themes "Health" "Politics" "Sports" \
    --output classified.csv
```

### Using Individual Components

```python
from topicflow.preprocessing import preprocess_corpus
from topicflow.modeling import TopicModeler
from topicflow.naming import TopicNamer
from topicflow.classifier import TopicClassifier

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

## Methodology

### Stage 1: BERTopic Modeling

Documents are embedded using SentenceTransformer (`all-MiniLM-L6-v2`), reduced via UMAP, clustered with HDBSCAN, and topics are extracted via class-based TF-IDF. A random search over UMAP and HDBSCAN hyperparameters (default: 50 iterations × 24 topic solutions = 1,200 models) selects the configuration maximizing c_v coherence.

### Stage 2: Democratic LLM Naming

Each topic's representative words are sent to an LLM (default: GPT-4o) independently N times. The most frequently returned name wins by majority vote, reducing individual LLM bias and producing stable, consensus-driven topic labels.

### Stage 3: LLM Classification

The discovered theme names are used as classification categories. Each document in the target corpus is independently classified by the LLM. Classification is validated against a human-labeled subset with a configurable agreement threshold (default: >85%).

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
@article{thomas2025topicflow,
  title={TopicFlow: A BERTopic and Large Language Model Pipeline for Topic Discovery and Classification},
  author={Thomas, Jacob Edward},
  year={2025},
  note={Preprint}
}
```

## License

MIT License. See [LICENSE](LICENSE).
