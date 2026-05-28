# E2E Topic Modeler

**Embedding-to-Explanation Topic Modeling — A Browser-Based Tool**

An interactive web application that implements the E2E topic modeling methodology matching the dissertation pipeline. Upload a CSV of text documents, and the tool will:

1. **Embed** with Voyage AI (voyage-3)
2. **Reduce** with UMAP (n_neighbors=15, n_components=5, min_dist=0.01, cosine)
3. **Cluster** with HDBSCAN (mutual reachability distance, EOM extraction)
4. **Name** topics with Claude (5-vote democratic majority)
5. **Classify** all documents with Claude

## Architecture

```
┌───────────────────────────────────────────────────────────────┐
│  Browser (static site)                                        │
│                                                               │
│  1. Upload CSV  →  Parse id + text columns                    │
│  2. POST /embed  →  Voyage AI embeddings (voyage-3, 1024-dim) │
│  3. L2-normalize embedding vectors                            │
│  4. UMAP dimensionality reduction (local JS)                  │
│  5. HDBSCAN clustering with EOM extraction (local JS)         │
│  6. TF-IDF term extraction per cluster (local JS)             │
│  7. PCA projection of UMAP embedding for visualization        │
│                                                               │
│  8. Topic Naming      →  POST /chat  →  Claude API            │
│     (5 votes per topic, majority wins)                        │
│  9. Classification    →  POST /chat  →  Claude API            │
│     (batches of 10 documents)                                 │
│                                                               │
│  10. Display results + download CSV                           │
└────────────────────────┬──────────────────────────────────────┘
                         │ (CORS)
         ┌───────────────▼───────────────┐
         │  Cloudflare Worker             │
         │  POST /chat  → Claude API      │
         │  POST /embed → Voyage AI API   │
         │  Secrets:                       │
         │    ANTHROPIC_API_KEY            │
         │    VOYAGE_API_KEY               │
         └───────────────────────────────┘
```

## Project Structure

```
e2e-topic-modeler/
├── public/                  ← Static site (deployed to Pages or any host)
│   ├── index.html           ← Landing page + app UI
│   ├── css/style.css        ← Navy/gold theme
│   └── js/
│       ├── app.js           ← Pipeline orchestration, CSV parsing, results
│       ├── clustering.js    ← UMAP, HDBSCAN, PCA, TF-IDF term extraction
│       └── claude.js        ← API communication (Voyage embeddings + Claude)
├── worker/                  ← Cloudflare Worker (deployed separately)
│   ├── index.js             ← Routes /chat → Claude, /embed → Voyage
│   └── wrangler.toml        ← Worker config
├── package.json
├── wrangler.toml            ← Pages config (static site only)
└── README.md
```

## Deployment

### Step 1: Deploy the Worker

```bash
cd e2e-topic-modeler/worker
wrangler secret put ANTHROPIC_API_KEY    # paste your Anthropic key
wrangler secret put VOYAGE_API_KEY       # paste your Voyage AI key
wrangler deploy
```

Note the worker URL (e.g., `https://e2e-topic-modeler-api.your-account.workers.dev`).

### Step 2: Deploy the Static Site

```bash
cd e2e-topic-modeler
npx wrangler pages deploy public/ --project-name=e2e-topic-modeler
```

Or host `public/` anywhere (GitHub Pages, Netlify, Vercel, local server).

### Step 3: Configure

1. Open the deployed site
2. Paste your worker URL in the "API Worker URL" field
3. Click "Save" — the URL is stored in your browser's localStorage

### Local Development

```bash
cd e2e-topic-modeler/worker
ANTHROPIC_API_KEY=sk-ant-... VOYAGE_API_KEY=pa-... wrangler dev
# Worker runs at http://localhost:8787

# In another terminal, serve the static site:
cd e2e-topic-modeler/public
python -m http.server 8080
# Open http://localhost:8080, set worker URL to http://localhost:8787
```

## API Keys

| Secret | Source | Description |
|--------|--------|-------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Claude API (topic naming + classification) |
| `VOYAGE_API_KEY` | [dash.voyageai.com](https://dash.voyageai.com) | Voyage AI embeddings (voyage-3) |

## Citation

Thomas, J. E. (2025). *Embedding-to-Explanation Topic Modeling: A Hybrid Approach for Interpretive Text Analysis.* The University of Texas at Austin.

## License

MIT License.
