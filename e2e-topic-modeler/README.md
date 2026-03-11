# E2E Topic Modeler

**Embedding-to-Explanation Topic Modeling — A Browser-Based Tool**

An interactive web application that performs end-to-end topic modeling entirely in the browser. Upload a CSV of text documents, and the tool will embed, cluster, name, and classify them — no coding required.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Browser (static site on Cloudflare Pages)               │
│                                                          │
│  1. Upload CSV  →  Parse id + text columns               │
│  2. TF-IDF vectorization  (pure JS, runs locally)        │
│  3. K-means clustering    (pure JS, runs locally)        │
│  4. PCA visualization     (pure JS, runs locally)        │
│                                                          │
│  5. Topic Naming      →  POST /api  →  Claude API        │
│  6. Classification    →  POST /api  →  Claude API        │
│                                                          │
│  7. Display results + download CSV                       │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────▼─────────────┐
        │  Pages Function (/api)   │
        │  functions/api.js        │
        │  Injects ANTHROPIC_API_KEY│
        │  Proxies to Anthropic    │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │  Anthropic Claude API    │
        │  claude-sonnet-4-5       │
        └──────────────────────────┘
```

## Project Structure

```
e2e-topic-modeler/
├── public/                  ← Static site (deployed to Pages)
│   ├── index.html           ← Landing page + app UI
│   ├── css/style.css        ← Navy/gold theme
│   └── js/
│       ├── app.js           ← Pipeline orchestration, CSV parsing, results
│       ├── clustering.js    ← TF-IDF, K-means, PCA (pure JavaScript)
│       └── claude.js        ← Claude API communication via /api proxy
├── functions/               ← Cloudflare Pages Functions
│   └── api.js               ← POST /api → proxies to Anthropic Claude API
├── worker/                  ← Legacy standalone worker (alternative deploy)
│   ├── index.js             ← Same proxy logic as functions/api.js
│   └── wrangler.toml        ← Config for standalone worker deployment
├── package.json             ← npm scripts for dev and deploy
├── wrangler.toml            ← Pages project config
└── README.md                ← This file
```

## The Three-Stage Pipeline

| Stage | What happens | Where it runs |
|-------|-------------|---------------|
| **1. Embed & Cluster** | TF-IDF vectorization → K-means with cosine similarity → PCA projection | Browser (local) |
| **2. Name Topics** | Representative docs + top terms sent to Claude 5× per cluster, majority vote on name | Claude API via /api |
| **3. Classify Documents** | Each document classified into discovered topics in batches of 10 | Claude API via /api |

## Deployment

This project is designed to deploy as a **single Cloudflare Pages project** with Pages Functions. See the main README for step-by-step Cloudflare portal instructions.

### Quick Deploy (CLI)

```bash
cd e2e-topic-modeler
npm install
npx wrangler pages deploy public/ --project-name=e2e-topic-modeler
```

Then set your API key in the Cloudflare dashboard under Pages → Settings → Environment variables.

### Local Development

```bash
cd e2e-topic-modeler
npm install
npm run dev
# Opens at http://localhost:8788
```

For local dev, set the environment variable:
```bash
ANTHROPIC_API_KEY=sk-ant-... npm run dev
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude access. Set as encrypted in Pages dashboard. |

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
