/**
 * E2E Topic Modeler — Clustering Module
 *
 * Implements the full dissertation methodology in the browser:
 *   1. Voyage AI embeddings (provided externally)
 *   2. UMAP dimensionality reduction  (n_neighbors, n_components, min_dist, cosine)
 *   3. HDBSCAN clustering             (min_cluster_size, EOM extraction)
 *   4. TF-IDF term extraction per cluster (for topic naming prompts)
 *   5. PCA projection to 2D (for visualization)
 */

const Clustering = (() => {
  'use strict';

  // =========================================================================
  // Vector Utilities
  // =========================================================================

  function l2Normalize(vec) {
    let norm = 0;
    for (let i = 0; i < vec.length; i++) norm += vec[i] * vec[i];
    norm = Math.sqrt(norm) || 1;
    for (let i = 0; i < vec.length; i++) vec[i] /= norm;
    return vec;
  }

  function cosineSimilarity(a, b) {
    let dot = 0;
    for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
    return dot;
  }

  function cosineDistance(a, b) {
    return 1 - cosineSimilarity(a, b);
  }

  function euclideanDistSq(a, b) {
    let s = 0;
    for (let i = 0; i < a.length; i++) { const d = a[i] - b[i]; s += d * d; }
    return s;
  }

  function euclideanDist(a, b) {
    return Math.sqrt(euclideanDistSq(a, b));
  }

  function normalizeEmbeddings(rawEmbeddings) {
    return rawEmbeddings.map(vec => {
      const f = new Float64Array(vec);
      return l2Normalize(f);
    });
  }

  // =========================================================================
  // UMAP  —  Uniform Manifold Approximation and Projection
  //
  // Reference: McInnes, Healy & Melville (2018). UMAP: Uniform Manifold
  //   Approximation and Projection for Dimension Reduction.
  //
  // Dissertation params: n_neighbors=15, n_components=4, min_dist=0.01,
  //   metric=cosine
  // =========================================================================

  /**
   * Brute-force k-nearest-neighbor search with cosine distance.
   * Returns { indices: Int32Array[], distances: Float64Array[] }
   */
  function knnCosine(matrix, k, onProgress) {
    const N = matrix.length;
    const indices = Array.from({ length: N }, () => new Int32Array(k));
    const distances = Array.from({ length: N }, () => new Float64Array(k));

    for (let i = 0; i < N; i++) {
      if (onProgress && i % 50 === 0) onProgress(i, N);

      // Partial sort: keep track of k smallest distances
      const heap = []; // max-heap of { dist, idx }

      for (let j = 0; j < N; j++) {
        if (i === j) continue;
        const d = cosineDistance(matrix[i], matrix[j]);

        if (heap.length < k) {
          heap.push({ dist: d, idx: j });
          if (heap.length === k) heap.sort((a, b) => b.dist - a.dist);
        } else if (d < heap[0].dist) {
          heap[0] = { dist: d, idx: j };
          heap.sort((a, b) => b.dist - a.dist);
        }
      }

      heap.sort((a, b) => a.dist - b.dist);
      for (let n = 0; n < k; n++) {
        indices[i][n] = heap[n].idx;
        distances[i][n] = heap[n].dist;
      }
    }

    return { indices, distances };
  }

  /**
   * Compute smooth kNN bandwidths (sigma) and nearest-neighbor distances (rho)
   * per point via binary search, so that sum of fuzzy weights ≈ log2(k).
   */
  function smoothKNN(knnDists, k) {
    const N = knnDists.length;
    const target = Math.log2(k);
    const sigmas = new Float64Array(N);
    const rhos = new Float64Array(N);

    for (let i = 0; i < N; i++) {
      rhos[i] = knnDists[i][0]; // distance to nearest neighbor

      let lo = 1e-20, hi = Infinity, mid = 1.0;

      for (let iter = 0; iter < 64; iter++) {
        let sum = 0;
        for (let j = 0; j < k; j++) {
          const d = Math.max(knnDists[i][j] - rhos[i], 0);
          sum += Math.exp(-d / mid);
        }

        if (Math.abs(sum - target) < 1e-5) break;

        if (sum > target) {
          hi = mid;
          mid = (lo + hi) / 2;
        } else {
          lo = mid;
          mid = hi === Infinity ? mid * 2 : (lo + hi) / 2;
        }
      }

      sigmas[i] = mid;
    }

    return { sigmas, rhos };
  }

  /**
   * Build the fuzzy simplicial set (weighted directed graph) from kNN data,
   * then symmetrize: W_sym(i,j) = W(i,j) + W(j,i) - W(i,j)·W(j,i).
   * Returns a flat array of { i, j, w } edges (undirected, deduplicated).
   */
  function buildFuzzyGraph(knnIndices, knnDists, sigmas, rhos) {
    const N = knnIndices.length;
    const k = knnIndices[0].length;

    // Directed weights stored as Map<"i,j", weight>
    const directed = new Map();

    for (let i = 0; i < N; i++) {
      for (let n = 0; n < k; n++) {
        const j = knnIndices[i][n];
        const d = Math.max(knnDists[i][n] - rhos[i], 0);
        const w = Math.exp(-d / sigmas[i]);
        directed.set(`${i},${j}`, w);
      }
    }

    // Symmetrize
    const edgeMap = new Map();

    for (const [key, wIJ] of directed) {
      const [si, sj] = key.split(',');
      const i = parseInt(si), j = parseInt(sj);
      const lo = Math.min(i, j), hi = Math.max(i, j);
      const symKey = `${lo},${hi}`;

      if (!edgeMap.has(symKey)) {
        const wJI = directed.get(`${j},${i}`) || 0;
        const wSym = wIJ + wJI - wIJ * wJI;
        if (wSym > 0) edgeMap.set(symKey, { i: lo, j: hi, w: wSym });
      }
    }

    return Array.from(edgeMap.values());
  }

  /**
   * Find a, b parameters for the output distance metric via grid search.
   * The curve 1/(1 + a·d^(2b)) should approximate the membership function.
   */
  function findABParams(spread, minDist) {
    const xs = [], ys = [];
    for (let i = 1; i <= 300; i++) {
      const x = i / 100;
      xs.push(x);
      ys.push(x <= minDist ? 1.0 : Math.exp(-(x - minDist) / spread));
    }

    let bestA = 1, bestB = 1, bestErr = Infinity;

    for (let ai = 1; ai <= 40; ai++) {
      const a = ai * 0.15;
      for (let bi = 1; bi <= 40; bi++) {
        const b = bi * 0.05;
        let err = 0;
        for (let k = 0; k < xs.length; k++) {
          const pred = 1 / (1 + a * Math.pow(xs[k], 2 * b));
          err += (pred - ys[k]) ** 2;
        }
        if (err < bestErr) { bestErr = err; bestA = a; bestB = b; }
      }
    }

    return { a: bestA, b: bestB };
  }

  /**
   * SGD optimisation of the low-dimensional embedding.
   * Uses the epochs-per-sample scheme from the reference implementation.
   */
  function optimizeEmbedding(embedding, edges, N, dim, nEpochs, a, b, onProgress) {
    const nNegative = 5;
    const initialLR = 1.0;

    // Compute epochs_per_sample
    let maxW = 0;
    for (const e of edges) if (e.w > maxW) maxW = e.w;

    const epochsPerSample = edges.map(e => e.w > 0 ? maxW / e.w : nEpochs + 1);
    const nextSample = new Float64Array(edges.length);

    for (let epoch = 0; epoch < nEpochs; epoch++) {
      if (onProgress && epoch % 20 === 0) onProgress(epoch, nEpochs);

      const lr = initialLR * (1.0 - epoch / nEpochs);

      for (let e = 0; e < edges.length; e++) {
        if (nextSample[e] > epoch) continue;
        nextSample[e] += epochsPerSample[e];

        const { i, j } = edges[e];

        let dSq = 0;
        for (let d = 0; d < dim; d++) dSq += (embedding[i][d] - embedding[j][d]) ** 2;

        // Attractive force
        if (dSq > 0) {
          const gradCoeff = (-2 * a * b * Math.pow(dSq, b - 1)) / (1 + a * Math.pow(dSq, b));
          for (let d = 0; d < dim; d++) {
            const g = Math.max(-4, Math.min(4, gradCoeff * (embedding[i][d] - embedding[j][d])));
            embedding[i][d] += lr * g;
            embedding[j][d] -= lr * g;
          }
        }

        // Repulsive forces (negative sampling)
        for (let s = 0; s < nNegative; s++) {
          const k = Math.floor(Math.random() * N);
          if (k === i) continue;

          let dSqN = 0;
          for (let d = 0; d < dim; d++) dSqN += (embedding[i][d] - embedding[k][d]) ** 2;

          if (dSqN > 0) {
            const g0 = (2 * b) / ((0.001 + dSqN) * (1 + a * Math.pow(dSqN, b)));
            for (let d = 0; d < dim; d++) {
              const g = Math.max(-4, Math.min(4, g0 * (embedding[i][d] - embedding[k][d])));
              embedding[i][d] += lr * g;
            }
          }
        }
      }
    }
  }

  /**
   * Run UMAP.
   *
   * @param {Float64Array[]} matrix - L2-normalised embedding vectors
   * @param {Object} options
   * @param {number} options.nNeighbors   - default 15
   * @param {number} options.nComponents  - default 5
   * @param {number} options.minDist      - default 0.01
   * @param {number} options.nEpochs      - default 200
   * @param {number} options.spread       - default 1.0
   * @param {Function} options.onProgress - (step, detail) => void
   * @returns {Float64Array[]} array of reduced-dimension vectors
   */
  function umap(matrix, options = {}) {
    const {
      nNeighbors = 15,
      nComponents = 5,
      minDist = 0.01,
      nEpochs = 200,
      spread = 1.0,
      onProgress,
    } = options;

    const N = matrix.length;
    const k = Math.min(nNeighbors, N - 1);

    // Step 1: kNN
    if (onProgress) onProgress('knn', 'Computing nearest neighbors...');
    const { indices, distances } = knnCosine(matrix, k, (i, total) => {
      if (onProgress) onProgress('knn', `kNN: ${i}/${total} points`);
    });

    // Step 2: Smooth bandwidths
    if (onProgress) onProgress('smooth', 'Computing fuzzy simplicial set...');
    const { sigmas, rhos } = smoothKNN(distances, k);

    // Step 3: Build fuzzy graph
    const edges = buildFuzzyGraph(indices, distances, sigmas, rhos);

    // Step 4: Output metric parameters
    const { a, b } = findABParams(spread, minDist);

    // Step 5: Random initialization
    const embedding = Array.from({ length: N }, () => {
      const v = new Float64Array(nComponents);
      for (let d = 0; d < nComponents; d++) v[d] = (Math.random() - 0.5) * 0.01;
      return v;
    });

    // Step 6: Optimize
    if (onProgress) onProgress('optimize', 'Optimizing UMAP layout...');
    optimizeEmbedding(embedding, edges, N, nComponents, nEpochs, a, b, (epoch, total) => {
      if (onProgress) onProgress('optimize', `UMAP SGD: epoch ${epoch}/${total}`);
    });

    return { embedding, knnIndices: indices, knnDists: distances };
  }

  // =========================================================================
  // HDBSCAN  —  Hierarchical Density-Based Spatial Clustering
  //
  // Reference: Campello, Moulavi & Sander (2013). Density-Based Clustering
  //   Based on Hierarchical Density Estimates.
  //
  // Dissertation params: min_cluster_size variable (optimized), EOM method
  // =========================================================================

  /**
   * Compute core distances: the euclidean distance to the minSamples-th
   * nearest neighbor for each point (in the UMAP-reduced space).
   */
  function computeCoreDistances(points, minSamples) {
    const N = points.length;
    const coreDists = new Float64Array(N);

    for (let i = 0; i < N; i++) {
      const dists = [];
      for (let j = 0; j < N; j++) {
        if (i === j) continue;
        dists.push(euclideanDist(points[i], points[j]));
      }
      dists.sort((a, b) => a - b);
      coreDists[i] = dists[Math.min(minSamples - 1, dists.length - 1)];
    }

    return coreDists;
  }

  /**
   * Build MST using Prim's algorithm with mutual reachability distance.
   * mutual_reach(i,j) = max(core[i], core[j], d(i,j))
   */
  function buildMutualReachabilityMST(points, coreDists) {
    const N = points.length;
    const inMST = new Uint8Array(N);
    const minWeight = new Float64Array(N).fill(Infinity);
    const minFrom = new Int32Array(N).fill(-1);
    const mstEdges = [];

    inMST[0] = 1;
    for (let j = 1; j < N; j++) {
      const d = euclideanDist(points[0], points[j]);
      minWeight[j] = Math.max(coreDists[0], coreDists[j], d);
      minFrom[j] = 0;
    }

    for (let step = 0; step < N - 1; step++) {
      let bestNode = -1, bestWeight = Infinity;
      for (let j = 0; j < N; j++) {
        if (!inMST[j] && minWeight[j] < bestWeight) {
          bestWeight = minWeight[j];
          bestNode = j;
        }
      }

      if (bestNode === -1) break;

      inMST[bestNode] = 1;
      mstEdges.push({ from: minFrom[bestNode], to: bestNode, weight: bestWeight });

      for (let j = 0; j < N; j++) {
        if (inMST[j]) continue;
        const d = euclideanDist(points[bestNode], points[j]);
        const mr = Math.max(coreDists[bestNode], coreDists[j], d);
        if (mr < minWeight[j]) {
          minWeight[j] = mr;
          minFrom[j] = bestNode;
        }
      }
    }

    return mstEdges;
  }

  /**
   * Build single-linkage tree (dendrogram) from sorted MST edges
   * using union-find.
   *
   * Returns array of merge nodes:
   *   { left, right, distance, size, id }
   * where id = N + index
   */
  function buildSingleLinkageTree(mstEdges, N) {
    mstEdges.sort((a, b) => a.weight - b.weight);

    const parent = new Int32Array(2 * N);
    const size = new Int32Array(2 * N).fill(1);
    for (let i = 0; i < 2 * N; i++) parent[i] = i;

    function find(x) {
      while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; }
      return x;
    }

    const tree = [];
    let nextId = N;

    for (const edge of mstEdges) {
      const rA = find(edge.from);
      const rB = find(edge.to);
      if (rA === rB) continue;

      const newSize = size[rA] + size[rB];
      tree.push({ left: rA, right: rB, distance: edge.weight, size: newSize, id: nextId });

      parent[rA] = nextId;
      parent[rB] = nextId;
      size[nextId] = newSize;
      nextId++;
    }

    return tree;
  }

  /**
   * Enumerate all leaf (point) indices under a node in the single-linkage tree.
   */
  function getLeaves(nodeId, slTree, N) {
    if (nodeId < N) return [nodeId];
    const leaves = [];
    const stack = [nodeId];
    while (stack.length > 0) {
      const id = stack.pop();
      if (id < N) {
        leaves.push(id);
      } else {
        const merge = slTree[id - N];
        stack.push(merge.left, merge.right);
      }
    }
    return leaves;
  }

  /**
   * Condense the single-linkage tree: walk top-down, only split into a
   * new cluster when the child subtree has >= minClusterSize points.
   * Points in too-small subtrees "fall out" of the parent cluster.
   *
   * Returns { entries, numClusters }
   *   entries: [{ parent, child, lambda, childSize }, ...]
   *   numClusters: total condensed cluster count
   */
  function condenseTree(slTree, N, minClusterSize) {
    if (slTree.length === 0) {
      return { entries: [], numClusters: 1 };
    }

    const entries = [];
    let nextCluster = 0;
    const clusterMap = {};

    // Root is the last merge node
    const rootSlId = N + slTree.length - 1;
    clusterMap[rootSlId] = nextCluster++;

    const stack = [rootSlId];

    while (stack.length > 0) {
      const slId = stack.pop();
      const clusterId = clusterMap[slId];
      const merge = slTree[slId - N];
      const lambda = merge.distance > 0 ? 1 / merge.distance : Infinity;

      for (const childSlId of [merge.left, merge.right]) {
        let childSize;
        if (childSlId < N) {
          childSize = 1;
        } else {
          childSize = slTree[childSlId - N].size;
        }

        if (childSize < minClusterSize) {
          // All points fall out of parent cluster
          const leaves = getLeaves(childSlId, slTree, N);
          for (const leaf of leaves) {
            entries.push({ parent: clusterId, child: leaf, lambda, childSize: 1 });
          }
        } else {
          // Genuine split → new cluster
          const newClusterId = nextCluster++;
          clusterMap[childSlId] = newClusterId;
          entries.push({ parent: clusterId, child: newClusterId, lambda, childSize });

          if (childSlId >= N) {
            stack.push(childSlId);
          } else {
            // Single point that meets cluster size (shouldn't happen with minClusterSize > 1)
            entries.push({ parent: newClusterId, child: childSlId, lambda, childSize: 1 });
          }
        }
      }
    }

    return { entries, numClusters: nextCluster };
  }

  /**
   * Extract clusters using the Excess of Mass (EOM) method.
   *
   * For each condensed cluster: stability = Σ (lambda_point - lambda_birth)
   * Walk bottom-up: at each non-leaf node, if children's combined stability
   * exceeds the node's own stability, keep the children; otherwise merge.
   *
   * Returns { labels: number[], nClusters: number }
   *   labels[i] = cluster index (0-based) or -1 for noise
   */
  function extractClustersEOM(condensedEntries, numClusters, N) {
    // Birth lambda for each cluster
    const birthLambda = new Float64Array(numClusters);
    // Root birth lambda is 0
    birthLambda[0] = 0;

    // Find birth lambdas (the lambda at which the cluster appears as a child)
    for (const e of condensedEntries) {
      if (e.childSize > 1) {
        birthLambda[e.child] = e.lambda;
      }
    }

    // Compute stability
    const stability = new Float64Array(numClusters);
    for (const e of condensedEntries) {
      if (e.childSize === 1) {
        stability[e.parent] += (e.lambda - birthLambda[e.parent]);
      }
    }

    // Build children-of-cluster map
    const children = Array.from({ length: numClusters }, () => []);
    for (const e of condensedEntries) {
      if (e.childSize > 1) {
        children[e.parent].push(e.child);
      }
    }

    // Determine leaf clusters
    const isLeaf = children.map(ch => ch.length === 0);

    // Selected clusters
    const selected = new Uint8Array(numClusters);

    // Walk bottom-up (higher IDs are deeper in the tree)
    for (let c = numClusters - 1; c >= 0; c--) {
      if (isLeaf[c]) {
        selected[c] = 1;
      } else {
        const childStabSum = children[c].reduce((s, ch) => s + stability[ch], 0);
        if (childStabSum > stability[c]) {
          // Children win → propagate their total stability upward
          stability[c] = childStabSum;
        } else {
          // This cluster wins → select it, deselect all descendants
          selected[c] = 1;
          const descStack = [...children[c]];
          while (descStack.length > 0) {
            const d = descStack.pop();
            selected[d] = 0;
            descStack.push(...children[d]);
          }
        }
      }
    }

    // Never select root (cluster 0) — that means "everything is one cluster"
    selected[0] = 0;

    // Build parent map for clusters
    const clusterParent = new Int32Array(numClusters).fill(-1);
    for (const e of condensedEntries) {
      if (e.childSize > 1) {
        clusterParent[e.child] = e.parent;
      }
    }

    // Assign each point to its deepest selected ancestor
    const pointCluster = new Int32Array(N).fill(-1);
    for (const e of condensedEntries) {
      if (e.childSize === 1) {
        let c = e.parent;
        while (c >= 0 && !selected[c]) {
          c = clusterParent[c];
        }
        if (c >= 0) {
          pointCluster[e.child] = c;
        }
      }
    }

    // Renumber selected clusters to 0, 1, 2, ...
    const selectedIds = [];
    for (let c = 0; c < numClusters; c++) {
      if (selected[c]) selectedIds.push(c);
    }

    const labelMap = {};
    selectedIds.forEach((c, i) => { labelMap[c] = i; });

    const labels = new Int32Array(N).fill(-1);
    for (let i = 0; i < N; i++) {
      if (pointCluster[i] >= 0 && labelMap[pointCluster[i]] !== undefined) {
        labels[i] = labelMap[pointCluster[i]];
      }
    }

    return { labels: Array.from(labels), nClusters: selectedIds.length };
  }

  /**
   * Run HDBSCAN on UMAP-reduced points.
   *
   * @param {Float64Array[]} points - UMAP-reduced vectors
   * @param {Object} options
   * @param {number} options.minClusterSize - default 15
   * @param {number} options.minSamples     - default = minClusterSize
   * @param {Function} options.onProgress
   * @returns {{ labels: number[], nClusters: number }}
   */
  function hdbscan(points, options = {}) {
    const {
      minClusterSize = 15,
      minSamples = null,
      onProgress,
    } = options;

    const ms = minSamples || minClusterSize;
    const N = points.length;

    if (N < minClusterSize * 2) {
      // Not enough points for meaningful clustering
      return { labels: Array.from({ length: N }, () => -1), nClusters: 0 };
    }

    // Step 1: Core distances
    if (onProgress) onProgress('core', 'Computing core distances...');
    const coreDists = computeCoreDistances(points, ms);

    // Step 2: MST with mutual reachability
    if (onProgress) onProgress('mst', 'Building minimum spanning tree...');
    const mstEdges = buildMutualReachabilityMST(points, coreDists);

    // Step 3: Single-linkage tree
    if (onProgress) onProgress('tree', 'Building cluster hierarchy...');
    const slTree = buildSingleLinkageTree(mstEdges, N);

    // Step 4: Condense
    if (onProgress) onProgress('condense', 'Condensing cluster tree...');
    const { entries, numClusters } = condenseTree(slTree, N, minClusterSize);

    // Step 5: EOM extraction
    if (onProgress) onProgress('eom', 'Extracting clusters (EOM)...');
    const result = extractClustersEOM(entries, numClusters, N);

    return result;
  }

  // =========================================================================
  // TF-IDF Term Extraction  (for topic naming prompts — NOT for clustering)
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
   * Extract top N terms per cluster using class-based TF-IDF.
   * Noise points (label === -1) are excluded.
   */
  function getTopTerms(texts, labels, nClusters, topN = 10) {
    const N = texts.length;
    const tokenized = texts.map(tokenize);

    // Document frequency across entire corpus
    const df = {};
    tokenized.forEach(tokens => {
      const seen = new Set(tokens);
      seen.forEach(t => { df[t] = (df[t] || 0) + 1; });
    });

    const result = {};

    for (let c = 0; c < nClusters; c++) {
      const clusterTF = {};
      let clusterDocCount = 0;

      for (let i = 0; i < N; i++) {
        if (labels[i] !== c) continue;
        clusterDocCount++;
        tokenized[i].forEach(t => { clusterTF[t] = (clusterTF[t] || 0) + 1; });
      }

      if (clusterDocCount === 0) { result[c] = []; continue; }

      const scored = Object.entries(clusterTF).map(([term, count]) => {
        const idf = Math.log((N + 1) / (df[term] + 1)) + 1;
        return { term, score: (count / clusterDocCount) * idf };
      });

      scored.sort((a, b) => b.score - a.score);
      result[c] = scored.slice(0, topN).map(x => x.term);
    }

    return result;
  }

  /**
   * Get representative documents: for each cluster, return the indices of
   * documents closest to the cluster centroid (in UMAP space).
   */
  function getRepresentativeDocs(umapEmbedding, labels, nClusters, topN = 10) {
    const dim = umapEmbedding[0].length;
    const result = {};

    for (let c = 0; c < nClusters; c++) {
      const memberIndices = [];
      for (let i = 0; i < labels.length; i++) {
        if (labels[i] === c) memberIndices.push(i);
      }

      if (memberIndices.length === 0) { result[c] = []; continue; }

      // Compute centroid
      const centroid = new Float64Array(dim);
      for (const idx of memberIndices) {
        for (let d = 0; d < dim; d++) centroid[d] += umapEmbedding[idx][d];
      }
      for (let d = 0; d < dim; d++) centroid[d] /= memberIndices.length;

      // Sort by distance to centroid
      memberIndices.sort((a, b) => {
        return euclideanDistSq(umapEmbedding[a], centroid) -
               euclideanDistSq(umapEmbedding[b], centroid);
      });

      result[c] = memberIndices.slice(0, topN);
    }

    return result;
  }

  // =========================================================================
  // 2D Projection (PCA via power iteration) for Visualization
  // =========================================================================

  function projectTo2D(matrix) {
    const N = matrix.length;
    const D = matrix[0].length;

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
    umap,
    hdbscan,
    getTopTerms,
    getRepresentativeDocs,
    projectTo2D,
    cosineDistance,
    euclideanDist,
  };
})();
