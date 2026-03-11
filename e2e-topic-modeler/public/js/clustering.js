/**
 * E2E Topic Modeler — Clustering Module
 *
 * Operates on dense embedding vectors (from Voyage AI) for clustering,
 * with a lightweight TF-IDF pass used only for extracting representative
 * terms per cluster (not for document similarity).
 *
 * Pipeline:
 *   1. Voyage embeddings (provided externally) → L2-normalised
 *   2. K-Means clustering with cosine similarity
 *   3. Silhouette score for auto-detecting k
 *   4. TF-IDF term extraction per cluster (for topic naming prompts)
 *   5. PCA projection to 2D (for visualisation)
 */

const Clustering = (() => {
  'use strict';

  // =========================================================================
  // Vector Utilities
  // =========================================================================

  /** L2-normalise a vector in place and return it. */
  function l2Normalize(vec) {
    let norm = 0;
    for (let i = 0; i < vec.length; i++) norm += vec[i] * vec[i];
    norm = Math.sqrt(norm) || 1;
    for (let i = 0; i < vec.length; i++) vec[i] /= norm;
    return vec;
  }

  /** Cosine similarity between two L2-normalised vectors (= dot product). */
  function cosineSimilarity(a, b) {
    let dot = 0;
    for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
    return dot;
  }

  /** Cosine distance = 1 - cosine similarity. */
  function cosineDistance(a, b) {
    return 1 - cosineSimilarity(a, b);
  }

  /**
   * Normalise an array of embedding vectors.
   * Accepts raw arrays from the Voyage API and returns Float64Arrays.
   */
  function normalizeEmbeddings(rawEmbeddings) {
    return rawEmbeddings.map(vec => {
      const f = new Float64Array(vec);
      return l2Normalize(f);
    });
  }

  // =========================================================================
  // K-Means Clustering (cosine distance)
  // =========================================================================

  /** Simple seeded PRNG (Mulberry32). */
  function mulberry32(seed) {
    return function() {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = t + Math.imul(t ^ (t >>> 7), 61 | t) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /**
   * K-Means++ initialisation using cosine distance.
   */
  function kmeansppInit(matrix, k) {
    const N = matrix.length;
    const centroids = [];
    const rng = mulberry32(42);

    centroids.push(matrix[Math.floor(rng() * N)].slice());

    for (let c = 1; c < k; c++) {
      const dists = new Float64Array(N);
      let total = 0;
      for (let i = 0; i < N; i++) {
        let minDist = Infinity;
        for (let j = 0; j < centroids.length; j++) {
          const d = cosineDistance(matrix[i], centroids[j]);
          if (d < minDist) minDist = d;
        }
        dists[i] = minDist * minDist;
        total += dists[i];
      }
      let r = rng() * total;
      for (let i = 0; i < N; i++) {
        r -= dists[i];
        if (r <= 0) {
          centroids.push(matrix[i].slice());
          break;
        }
      }
      if (centroids.length === c) {
        centroids.push(matrix[Math.floor(rng() * N)].slice());
      }
    }
    return centroids;
  }

  /**
   * Run K-Means with cosine distance.
   * @param {Float64Array[]} matrix - L2-normalised embedding vectors
   * @param {number} k
   * @param {number} maxIter
   * @returns {{ labels: number[], centroids: Float64Array[] }}
   */
  function kmeans(matrix, k, maxIter = 100) {
    const N = matrix.length;
    const D = matrix[0].length;
    let centroids = kmeansppInit(matrix, k);
    let labels = new Int32Array(N);

    for (let iter = 0; iter < maxIter; iter++) {
      let changed = 0;
      for (let i = 0; i < N; i++) {
        let bestDist = Infinity;
        let bestK = 0;
        for (let c = 0; c < k; c++) {
          const d = cosineDistance(matrix[i], centroids[c]);
          if (d < bestDist) { bestDist = d; bestK = c; }
        }
        if (labels[i] !== bestK) { changed++; labels[i] = bestK; }
      }

      if (changed === 0) break;

      const newCentroids = Array.from({ length: k }, () => new Float64Array(D));
      const counts = new Int32Array(k);

      for (let i = 0; i < N; i++) {
        const c = labels[i];
        counts[c]++;
        for (let j = 0; j < D; j++) newCentroids[c][j] += matrix[i][j];
      }

      for (let c = 0; c < k; c++) {
        if (counts[c] === 0) {
          const ri = Math.floor(Math.random() * N);
          newCentroids[c] = matrix[ri].slice();
        } else {
          for (let j = 0; j < D; j++) newCentroids[c][j] /= counts[c];
          l2Normalize(newCentroids[c]);
        }
      }

      centroids = newCentroids;
    }

    return { labels: Array.from(labels), centroids };
  }

  // =========================================================================
  // Silhouette Score (for auto-detecting k)
  // =========================================================================

  /**
   * Compute the mean silhouette score for a given labelling.
   * Uses cosine distance. Sampled for large N to keep things snappy.
   */
  function silhouetteScore(matrix, labels, k) {
    const N = matrix.length;
    const sampleSize = Math.min(N, 500);
    const indices = [];
    if (sampleSize < N) {
      const step = N / sampleSize;
      for (let i = 0; i < sampleSize; i++) indices.push(Math.floor(i * step));
    } else {
      for (let i = 0; i < N; i++) indices.push(i);
    }

    let totalScore = 0;

    for (const i of indices) {
      const ci = labels[i];
      let aSum = 0, aCount = 0;
      const bSums = new Float64Array(k);
      const bCounts = new Int32Array(k);

      for (let j = 0; j < N; j++) {
        if (i === j) continue;
        const d = cosineDistance(matrix[i], matrix[j]);
        if (labels[j] === ci) {
          aSum += d;
          aCount++;
        } else {
          bSums[labels[j]] += d;
          bCounts[labels[j]]++;
        }
      }

      const a = aCount > 0 ? aSum / aCount : 0;
      let minB = Infinity;
      for (let c = 0; c < k; c++) {
        if (c === ci || bCounts[c] === 0) continue;
        const avg = bSums[c] / bCounts[c];
        if (avg < minB) minB = avg;
      }
      if (minB === Infinity) minB = 0;

      const s = Math.max(a, minB) === 0 ? 0 : (minB - a) / Math.max(a, minB);
      totalScore += s;
    }

    return totalScore / indices.length;
  }

  /**
   * Auto-detect the best k by evaluating silhouette scores for k = 2..maxK.
   */
  function autoDetectK(matrix, minK = 2, maxK = 15) {
    maxK = Math.min(maxK, Math.floor(matrix.length / 3), 20);
    if (maxK < minK) maxK = minK;

    let bestK = minK;
    let bestScore = -1;

    for (let k = minK; k <= maxK; k++) {
      const { labels } = kmeans(matrix, k, 50);
      const score = silhouetteScore(matrix, labels, k);
      if (score > bestScore) {
        bestScore = score;
        bestK = k;
      }
    }

    return bestK;
  }

  // =========================================================================
  // Representative Document Selection
  // =========================================================================

  /**
   * For each cluster, find the N documents closest to the centroid.
   */
  function getRepresentativeDocs(matrix, labels, centroids, topN = 10) {
    const k = centroids.length;
    const result = {};

    for (let c = 0; c < k; c++) {
      const memberIndices = [];
      for (let i = 0; i < labels.length; i++) {
        if (labels[i] === c) memberIndices.push(i);
      }
      memberIndices.sort((a, b) => {
        return cosineSimilarity(matrix[b], centroids[c]) -
               cosineSimilarity(matrix[a], centroids[c]);
      });
      result[c] = memberIndices.slice(0, topN);
    }

    return result;
  }

  // =========================================================================
  // TF-IDF Term Extraction (used ONLY for extracting top terms per cluster,
  // NOT for document similarity — that comes from Voyage embeddings)
  // =========================================================================

  const STOP_WORDS = new Set([
    'a','about','above','after','again','against','all','am','an','and','any',
    'are','aren','as','at','be','because','been','before','being','below',
    'between','both','but','by','can','couldn','d','did','didn','do','does',
    'doesn','doing','don','down','during','each','few','for','from','further',
    'get','got','had','hadn','has','hasn','have','haven','having','he','her',
    'here','hers','herself','him','himself','his','how','i','if','in','into',
    'is','isn','it','its','itself','just','ll','m','ma','me','might','more',
    'most','mustn','my','myself','need','no','nor','not','now','o','of','off',
    'on','once','only','or','other','our','ours','ourselves','out','over',
    'own','re','s','same','she','should','shouldn','so','some','such','t',
    'than','that','the','their','theirs','them','themselves','then','there',
    'these','they','this','those','through','to','too','under','until','up',
    'us','ve','very','was','wasn','we','were','weren','what','when','where',
    'which','while','who','whom','why','will','with','won','would','wouldn',
    'y','you','your','yours','yourself','yourselves','also','could','would',
    'should','one','two','like','use','used','using','make','way','may',
    'well','back','even','still','new','want','go','going','know','said',
    'say','much','many','really','get','got','see','take','come','think',
    'look','thing','things','people','time','work','first','last','long',
    'great','little','right','good','big','high','old','different','small',
    'large','next','early','young'
  ]);

  function tokenize(text) {
    return text
      .toLowerCase()
      .replace(/[^a-z\s]/g, ' ')
      .split(/\s+/)
      .filter(t => t.length > 2 && !STOP_WORDS.has(t));
  }

  /**
   * Extract the top N terms per cluster using a lightweight TF-IDF pass.
   * This is independent of the embedding vectors — it only looks at word
   * frequencies within each cluster vs. the corpus.
   *
   * @param {string[]} texts - original document texts
   * @param {number[]} labels - cluster assignment per document
   * @param {number} k - number of clusters
   * @param {number} topN - terms to return per cluster
   * @returns {Object<number, string[]>} clusterId → top terms
   */
  function getTopTerms(texts, labels, k, topN = 10) {
    const N = texts.length;
    const tokenized = texts.map(tokenize);

    // Document frequency across entire corpus
    const df = {};
    tokenized.forEach(tokens => {
      const seen = new Set(tokens);
      seen.forEach(t => { df[t] = (df[t] || 0) + 1; });
    });

    const result = {};

    for (let c = 0; c < k; c++) {
      // Aggregate term frequencies within this cluster
      const clusterTF = {};
      let clusterDocCount = 0;

      for (let i = 0; i < N; i++) {
        if (labels[i] !== c) continue;
        clusterDocCount++;
        tokenized[i].forEach(t => { clusterTF[t] = (clusterTF[t] || 0) + 1; });
      }

      // Score: cluster TF × IDF (relative to full corpus)
      const scored = Object.entries(clusterTF).map(([term, count]) => {
        const idf = Math.log((N + 1) / (df[term] + 1)) + 1;
        return { term, score: (count / clusterDocCount) * idf };
      });

      scored.sort((a, b) => b.score - a.score);
      result[c] = scored.slice(0, topN).map(x => x.term);
    }

    return result;
  }

  // =========================================================================
  // 2D Projection (PCA via power iteration) for Visualization
  // =========================================================================

  /**
   * Project high-dimensional embedding vectors to 2D using the first two
   * principal components (computed via power iteration — fast, approximate).
   */
  function projectTo2D(matrix) {
    const N = matrix.length;
    const D = matrix[0].length;

    // Center the data
    const mean = new Float64Array(D);
    for (let i = 0; i < N; i++) {
      for (let j = 0; j < D; j++) mean[j] += matrix[i][j];
    }
    for (let j = 0; j < D; j++) mean[j] /= N;

    const centered = matrix.map(row => {
      const r = new Float64Array(D);
      for (let j = 0; j < D; j++) r[j] = row[j] - mean[j];
      return r;
    });

    function principalComponent(data) {
      const d = data[0].length;
      let pc = new Float64Array(d);
      for (let j = 0; j < d; j++) pc[j] = Math.random() - 0.5;

      for (let iter = 0; iter < 50; iter++) {
        const newPc = new Float64Array(d);
        for (let i = 0; i < data.length; i++) {
          let dot = 0;
          for (let j = 0; j < d; j++) dot += data[i][j] * pc[j];
          for (let j = 0; j < d; j++) newPc[j] += dot * data[i][j];
        }
        let norm = 0;
        for (let j = 0; j < d; j++) norm += newPc[j] * newPc[j];
        norm = Math.sqrt(norm) || 1;
        for (let j = 0; j < d; j++) newPc[j] /= norm;
        pc = newPc;
      }
      return pc;
    }

    const pc1 = principalComponent(centered);

    const deflated = centered.map(row => {
      let dot = 0;
      for (let j = 0; j < D; j++) dot += row[j] * pc1[j];
      const r = new Float64Array(D);
      for (let j = 0; j < D; j++) r[j] = row[j] - dot * pc1[j];
      return r;
    });

    const pc2 = principalComponent(deflated);

    return centered.map(row => {
      let x = 0, y = 0;
      for (let j = 0; j < D; j++) {
        x += row[j] * pc1[j];
        y += row[j] * pc2[j];
      }
      return { x, y };
    });
  }

  // =========================================================================
  // Public API
  // =========================================================================

  return {
    normalizeEmbeddings,
    kmeans,
    autoDetectK,
    silhouetteScore,
    getRepresentativeDocs,
    getTopTerms,
    projectTo2D,
    cosineDistance,
    cosineSimilarity,
  };
})();
