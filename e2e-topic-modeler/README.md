# E2E Topic Modeler

**Embedding-to-Explanation Topic Modeling — A Browser-Based Tool**

An interactive web application that implements the E2E topic modeling methodology. Upload a CSV of text documents, and the tool will embed them with Voyage AI, cluster them, name topics with Claude (democratic voting), and classify every document — no coding required.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Browser (static site on Cloudflare Pages)               │
│                                                          │
│  1. Upload CSV  →  Parse id + text columns               │
│  2. POST /api/embed  →  Voyage AI embeddings (voyage-3)  │
│  3. L2-normalize embedding vectors                       │
│  4. K-means clustering with cosine similarity (local JS) │
│  5. Silhouette score for auto-k detection (local JS)     │
│  6. TF-IDF term extraction per cluster (local JS)        │
│  7. PCA projection for visualization (local JS)          │
│                                                          │
│  8. Topic Naming      →  POST /api  →  Claude API        │
│     (5 votes per topic, majority wins)                   │
│  9. Classification    →  POST /api  →  Claude API        │
│     (batches of 10 documents)                            │
│                                                          │
│  10. Display results + download CSV                      │
└────────────────┬──────────────────┬──────────────────────┘
                 │                  │
    ┌────────────▼───────┐  ┌──────▼──────────────┐
    │  /api (Claude)     │  │  /api/embed (Voyage) │
    │  Pages Function    │  │  Pages Function      │
    │  ANTHROPIC_API_KEY │  │  VOYAGE_API_KEY      │
    └────────────┬───────┘  └──────┬──────────────┘
                 │                  │
    ┌────────────▼───────┐  ┌──────▼──────────────┐
    │  Anthropic API     │  │  Voyage AI API       │
    │  Claude Sonnet     │  │  voyage-3            │
    └────────────────────┘  └─────────────────────┘
```

## Project Structure

```
e2e-topic-modeler/
├── public/                  ← Static site (deployed to Pages)
│   ├── index.html           ← Landing page + app UI
│   ├── css/style.css        ← Navy/gold theme
│   └── js/
│       ├── app.js           ← Pipeline orchestration, CSV parsing, results
│       ├── clustering.js    ← K-means, silhouette, PCA, term extraction
│       └── claude.js        ← API communication (Voyage embeddings + Claude)
├── functions/               ← Cloudflare Pages Functions
│   └── api/
│       ├── index.js         ← POST /api → proxies to Anthropic Claude API
│       └── embed.js         ← POST /api/embed → proxies to Voyage AI API
├── worker/                  ← Legacy standalone worker (alternative deploy)
│   ├── index.js
│   └── wrangler.toml
├── package.json             ← npm scripts for dev and deploy
├── wrangler.toml            ← Pages project config
└── README.md                ← This file
```

## The Three-Stage Pipeline

| Stage | What happens | Where it runs |
|-------|-------------|---------------|
| **1. Embed & Cluster** | Voyage AI (voyage-3) embeddings → L2-normalize → K-means with cosine similarity → PCA projection | Voyage API + browser (local) |
| **2. Name Topics** | Representative docs + top TF-IDF terms sent to Claude 5x per cluster, majority vote on name | Claude API via /api |
| **3. Classify Documents** | Each document classified into discovered topics in batches of 10 | Claude API via /api |

## Deployment

This project deploys as a **single Cloudflare Pages project** with Pages Functions. See the main repo README for step-by-step Cloudflare portal instructions.

### Quick Deploy (CLI)

```bash
cd e2e-topic-modeler
npm install
npx wrangler pages deploy public/ --project-name=e2e-topic-modeler
```

Then set your API keys in the Cloudflare dashboard under Pages > Settings > Environment variables.

### Local Development

```bash
cd e2e-topic-modeler
npm install
ANTHROPIC_API_KEY=sk-ant-... VOYAGE_API_KEY=pa-... npm run dev
# Opens at http://localhost:8788
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude (topic naming + classification) |
| `VOYAGE_API_KEY` | Yes | Voyage AI API key for document embeddings (voyage-3) |

Both must be set as **encrypted** environment variables in the Cloudflare Pages dashboard.

## CSV Format

Your input CSV must have `id` and `text` columns. Additional columns are preserved in the output.

```csv
id,text
1,"This is my first document about climate change."
2,"Machine learning is transforming healthcare."
3,"The housing market continues to fluctuate."
```

## Citation

Thomas, J. E. (2025). *Embedding-to-Explanation Topic Modeling: A Hybrid Approach for Interpretive Text Analysis.* The University of Texas at Austin.

## License

MIT License.
