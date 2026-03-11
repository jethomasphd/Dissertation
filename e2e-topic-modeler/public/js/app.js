/**
 * E2E Topic Modeler — Main Application Logic
 *
 * Pipeline (matches dissertation methodology):
 *   1. Voyage AI embeddings → UMAP dimensionality reduction → HDBSCAN clustering
 *   2. Claude democratic topic naming (5 votes, majority wins)
 *   3. Claude document classification
 */

(() => {
  'use strict';

  // =========================================================================
  // State
  // =========================================================================

  let rawData = [];        // Array of { id, text, ...extra columns }
  let extraColumns = [];   // Column names beyond id and text
  let clusterResult = null; // { labels, nClusters, umapEmbedding, repDocs, topTerms, points2d }
  let topicInfo = [];      // [{ id, name, description, keywords }]
  let classifications = {}; // { docId: topicName }

  // =========================================================================
  // DOM References
  // =========================================================================

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const dropZone = $('#drop-zone');
  const fileInput = $('#file-input');
  const fileInfo = $('#file-info');
  const clusterConfig = $('#cluster-config');
  const clusterModeSelect = $('#cluster-mode');
  const clusterKInput = $('#cluster-k');
  const clusterKGroup = $('#cluster-k-group');
  const btnRun = $('#btn-run');
  const pipelineProgress = $('#pipeline-progress');
  const stages = $$('.pipeline-stage');
  const progressText = $('#progress-text');
  const progressBarFill = $('#progress-bar-fill');
  const clusterViz = $('#cluster-viz');
  const vizCanvas = $('#viz-canvas');
  const resultsSection = $('#results-section');
  const topicCards = $('#topic-cards');
  const resultsTableBody = $('#results-table-body');
  const btnDownload = $('#btn-download');
  const errorBanner = $('#error-banner');
  const workerUrlInput = $('#worker-url-input');
  const btnSaveUrl = $('#btn-save-url');
  const workerStatus = $('#worker-status');

  // =========================================================================
  // Worker URL Configuration
  // =========================================================================

  function initWorkerUrl() {
    const saved = localStorage.getItem('e2e_worker_url');
    if (saved) {
      workerUrlInput.value = saved;
      ClaudeAPI.setWorkerUrl(saved);
      workerStatus.textContent = 'Connected';
      workerStatus.className = 'worker-status connected';
    }
  }

  function saveWorkerUrl() {
    const url = workerUrlInput.value.trim().replace(/\/+$/, '');
    if (!url) {
      showError('Please enter your worker URL.');
      return;
    }
    localStorage.setItem('e2e_worker_url', url);
    ClaudeAPI.setWorkerUrl(url);
    workerStatus.textContent = 'Saved';
    workerStatus.className = 'worker-status connected';
    hideError();
  }

  if (btnSaveUrl) btnSaveUrl.addEventListener('click', saveWorkerUrl);
  if (workerUrlInput) {
    workerUrlInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') saveWorkerUrl();
    });
  }

  initWorkerUrl();

  // =========================================================================
  // CSV Parsing
  // =========================================================================

  function parseCSV(text) {
    const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
    if (lines.length < 2) throw new Error('CSV must have a header row and at least one data row.');

    const headers = parseCSVLine(lines[0]).map(h => h.trim().toLowerCase());

    const idIdx = headers.indexOf('id');
    const textIdx = headers.indexOf('text');
    if (idIdx === -1) throw new Error('CSV must contain an "id" column.');
    if (textIdx === -1) throw new Error('CSV must contain a "text" column.');

    extraColumns = headers.filter((h, i) => i !== idIdx && i !== textIdx);

    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = parseCSVLine(lines[i]);
      if (cols.length < headers.length) continue;

      const row = { id: cols[idIdx].trim(), text: cols[textIdx].trim() };
      headers.forEach((h, j) => {
        if (j !== idIdx && j !== textIdx) row[h] = cols[j];
      });

      if (row.text.length > 0) data.push(row);
    }

    if (data.length === 0) throw new Error('No valid data rows found in CSV.');
    return data;
  }

  function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (inQuotes) {
        if (ch === '"') {
          if (i + 1 < line.length && line[i + 1] === '"') {
            current += '"';
            i++;
          } else {
            inQuotes = false;
          }
        } else {
          current += ch;
        }
      } else {
        if (ch === '"') {
          inQuotes = true;
        } else if (ch === ',') {
          result.push(current);
          current = '';
        } else {
          current += ch;
        }
      }
    }
    result.push(current);
    return result;
  }

  // =========================================================================
  // File Upload Handling
  // =========================================================================

  function handleFile(file) {
    hideError();
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) {
      showError('Please upload a CSV file.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        rawData = parseCSV(e.target.result);
        fileInfo.textContent = `Loaded "${file.name}" — ${rawData.length} documents`;
        fileInfo.classList.add('visible');
        clusterConfig.classList.add('visible');
        btnRun.disabled = false;

        clusterResult = null;
        topicInfo = [];
        classifications = {};
        resultsSection.classList.remove('visible');
        clusterViz.classList.remove('visible');
        pipelineProgress.classList.remove('visible');
        stages.forEach(s => { s.classList.remove('active', 'completed'); });
      } catch (err) {
        showError(err.message);
      }
    };
    reader.onerror = () => showError('Failed to read the file.');
    reader.readAsText(file);
  }

  dropZone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => handleFile(fileInput.files[0]));

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFile(e.dataTransfer.files[0]);
  });

  clusterModeSelect.addEventListener('change', () => {
    clusterKGroup.style.display = clusterModeSelect.value === 'manual' ? 'inline-flex' : 'none';
  });

  // =========================================================================
  // Pipeline Orchestration
  // =========================================================================

  btnRun.addEventListener('click', runPipeline);

  async function runPipeline() {
    if (rawData.length === 0) return;

    // Validate worker URL
    if (!ClaudeAPI.getWorkerUrl()) {
      showError('Please configure your Worker URL before running the pipeline.');
      return;
    }

    hideError();
    btnRun.disabled = true;
    pipelineProgress.classList.add('visible');
    resultsSection.classList.remove('visible');
    clusterViz.classList.remove('visible');

    try {
      // ==== Stage 1: Embed → UMAP → HDBSCAN ====
      setStage(0);
      const texts = rawData.map(d => d.text);

      // Step 1a: Embed documents with Voyage AI
      updateProgress('Embedding documents with Voyage AI (voyage-3)...', 0);
      await tick();

      const rawEmbeddings = await ClaudeAPI.embedDocuments(texts, (batch, total) => {
        const pct = Math.round((batch / total) * 25);
        updateProgress(`Embedding batch ${batch} of ${total}...`, pct);
      });

      updateProgress('Normalizing embedding vectors...', 27);
      await tick();
      const matrix = Clustering.normalizeEmbeddings(rawEmbeddings);

      // Step 1b: UMAP dimensionality reduction
      updateProgress('Running UMAP dimensionality reduction...', 30);
      await tick();

      const umapResult = Clustering.umap(matrix, {
        nNeighbors: 15,
        nComponents: 5,
        minDist: 0.01,
        nEpochs: 200,
        onProgress: (step, detail) => {
          const pctMap = { knn: 35, smooth: 45, optimize: 55 };
          updateProgress(detail, pctMap[step] || 40);
        },
      });
      const umapEmbedding = umapResult.embedding;

      // Step 1c: HDBSCAN clustering
      updateProgress('Running HDBSCAN clustering...', 60);
      await tick();

      const minClusterSize = clusterModeSelect.value === 'manual'
        ? Math.max(2, parseInt(clusterKInput.value, 10) || 15)
        : Math.max(5, Math.min(Math.floor(rawData.length / 20), 25));

      const hdbResult = Clustering.hdbscan(umapEmbedding, {
        minClusterSize,
        onProgress: (step, detail) => {
          updateProgress(detail, 65);
        },
      });

      const { labels, nClusters } = hdbResult;

      if (nClusters === 0) {
        throw new Error(
          'HDBSCAN found no clusters. Try adjusting min_cluster_size ' +
          '(use manual mode with a smaller value) or adding more documents.'
        );
      }

      // Step 1d: Representative docs and term extraction
      updateProgress(`Found ${nClusters} clusters. Extracting representative documents...`, 75);
      await tick();

      const repDocs = Clustering.getRepresentativeDocs(umapEmbedding, labels, nClusters, 10);
      const topTerms = Clustering.getTopTerms(texts, labels, nClusters, 10);

      // Step 1e: 2D projection for visualization (PCA on UMAP output)
      updateProgress('Projecting clusters for visualization...', 85);
      await tick();
      const points2d = Clustering.projectTo2D(umapEmbedding);

      // Count noise points
      const noiseCount = labels.filter(l => l === -1).length;
      const clusterCount = labels.filter(l => l >= 0).length;

      clusterResult = {
        labels, nClusters, umapEmbedding, repDocs, topTerms, points2d,
        noiseCount, clusterCount,
      };

      updateProgress(
        `Stage 1 complete: ${nClusters} clusters, ${noiseCount} noise points.`,
        100
      );
      completeStage(0);
      await tick();

      drawClusterViz();

      // ==== Stage 2: Topic Naming (Claude democratic voting) ====
      setStage(1);
      topicInfo = [];

      for (let c = 0; c < nClusters; c++) {
        updateProgress(`Naming topic ${c + 1} of ${nClusters}...`, Math.round((c / nClusters) * 100));
        const repTexts = repDocs[c].map(i => rawData[i].text);
        const terms = topTerms[c] || [];

        const info = await ClaudeAPI.nameTopicDemocratic(repTexts, terms, c, (msg) => {
          updateProgress(msg, Math.round(((c + 0.5) / nClusters) * 100));
        });

        topicInfo.push({ id: c, name: info.name, description: info.description, keywords: info.keywords });
      }

      updateProgress('All topics named.', 100);
      completeStage(1);
      await tick();

      // ==== Stage 3: Document Classification (Claude) ====
      setStage(2);
      classifications = {};

      const BATCH_SIZE = 10;
      const totalBatches = Math.ceil(rawData.length / BATCH_SIZE);

      for (let b = 0; b < totalBatches; b++) {
        const start = b * BATCH_SIZE;
        const end = Math.min(start + BATCH_SIZE, rawData.length);
        const batch = rawData.slice(start, end).map(d => ({ id: d.id, text: d.text }));

        updateProgress(
          `Classifying documents: batch ${b + 1} of ${totalBatches} (${end} / ${rawData.length})`,
          Math.round((b / totalBatches) * 100)
        );

        try {
          const batchResult = await ClaudeAPI.classifyBatch(batch, topicInfo);
          Object.assign(classifications, batchResult);
        } catch (err) {
          console.warn(`Batch ${b + 1} classification failed, using HDBSCAN label:`, err);
          for (let i = start; i < end; i++) {
            const docId = rawData[i].id;
            if (!classifications[docId]) {
              const label = labels[i];
              classifications[docId] = label >= 0 && topicInfo[label]
                ? topicInfo[label].name
                : 'Unclassified';
            }
          }
        }
      }

      // Fill any missing
      rawData.forEach((d, i) => {
        if (!classifications[d.id]) {
          const label = labels[i];
          classifications[d.id] = label >= 0 && topicInfo[label]
            ? topicInfo[label].name
            : 'Unclassified';
        }
      });

      updateProgress('Classification complete.', 100);
      completeStage(2);
      await tick();

      renderResults();

    } catch (err) {
      showError(`Pipeline error: ${err.message}`);
      console.error(err);
    } finally {
      btnRun.disabled = false;
    }
  }

  // =========================================================================
  // Progress & Stage UI
  // =========================================================================

  function setStage(idx) {
    stages.forEach((s, i) => {
      s.classList.remove('active');
      if (i < idx) s.classList.add('completed');
    });
    stages[idx].classList.add('active');
  }

  function completeStage(idx) {
    stages[idx].classList.remove('active');
    stages[idx].classList.add('completed');
  }

  function updateProgress(text, pct) {
    progressText.textContent = text;
    progressBarFill.style.width = `${pct}%`;
  }

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.classList.add('visible');
  }

  function hideError() {
    errorBanner.classList.remove('visible');
  }

  function tick() {
    return new Promise(resolve => setTimeout(resolve, 20));
  }

  // =========================================================================
  // Cluster Visualization (Canvas)
  // =========================================================================

  function drawClusterViz() {
    if (!clusterResult) return;
    clusterViz.classList.add('visible');

    const canvas = vizCanvas;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = 400 * dpr;
    canvas.style.height = '400px';
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = 400;
    const padding = 40;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, W, H);

    const points = clusterResult.points2d;
    const labels = clusterResult.labels;
    const k = clusterResult.nClusters;

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    points.forEach(p => {
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    });

    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;

    const COLORS = [
      '#c9a959', '#1a1a2e', '#2ecc71', '#e74c3c', '#3498db',
      '#9b59b6', '#1abc9c', '#e67e22', '#34495e', '#e84393',
      '#00b894', '#636e72', '#fd79a8', '#6c5ce7', '#ffeaa7',
      '#dfe6e9', '#fab1a0', '#74b9ff', '#a29bfe', '#55efc4',
    ];
    const NOISE_COLOR = '#cccccc';

    // Draw points
    points.forEach((p, i) => {
      const x = padding + ((p.x - minX) / rangeX) * (W - 2 * padding);
      const y = padding + ((p.y - minY) / rangeY) * (H - 2 * padding);
      const isNoise = labels[i] === -1;
      const color = isNoise ? NOISE_COLOR : COLORS[labels[i] % COLORS.length];

      ctx.beginPath();
      ctx.arc(x, y, isNoise ? 2.5 : 4, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.globalAlpha = isNoise ? 0.3 : 0.7;
      ctx.fill();
      ctx.globalAlpha = 1;
    });

    // Legend
    const legendItems = k + (clusterResult.noiseCount > 0 ? 1 : 0);
    const legendX = W - 170;
    let legendY = 20;

    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.fillRect(legendX - 10, legendY - 10, 170, legendItems * 22 + 16);
    ctx.strokeStyle = '#dee2e6';
    ctx.strokeRect(legendX - 10, legendY - 10, 170, legendItems * 22 + 16);

    for (let c = 0; c < k; c++) {
      const color = COLORS[c % COLORS.length];
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(legendX, legendY + 6, 5, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#343a40';
      ctx.font = '12px -apple-system, sans-serif';
      const label = topicInfo[c] ? topicInfo[c].name : `Cluster ${c + 1}`;
      ctx.fillText(label.slice(0, 20), legendX + 12, legendY + 10);
      legendY += 22;
    }

    if (clusterResult.noiseCount > 0) {
      ctx.fillStyle = NOISE_COLOR;
      ctx.beginPath();
      ctx.arc(legendX, legendY + 6, 5, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#999';
      ctx.font = '12px -apple-system, sans-serif';
      ctx.fillText(`Noise (${clusterResult.noiseCount})`, legendX + 12, legendY + 10);
    }
  }

  // =========================================================================
  // Results Rendering
  // =========================================================================

  function renderResults() {
    resultsSection.classList.add('visible');

    topicCards.innerHTML = '';
    topicInfo.forEach(topic => {
      const count = rawData.filter(d => classifications[d.id] === topic.name).length;
      const card = document.createElement('div');
      card.className = 'topic-card fade-in';
      card.innerHTML = `
        <div class="topic-card-header">
          <h3>${escapeHTML(topic.name)}</h3>
          <span class="topic-count">${count} docs</span>
        </div>
        <p class="topic-description">${escapeHTML(topic.description)}</p>
        <div class="topic-keywords">
          ${topic.keywords.map(kw => `<span class="keyword-tag">${escapeHTML(kw)}</span>`).join('')}
        </div>
      `;
      topicCards.appendChild(card);
    });

    drawClusterViz();

    resultsTableBody.innerHTML = '';
    const displayDocs = rawData.slice(0, 100);
    displayDocs.forEach(d => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escapeHTML(String(d.id))}</td>
        <td title="${escapeHTML(d.text)}">${escapeHTML(d.text.slice(0, 120))}${d.text.length > 120 ? '...' : ''}</td>
        <td>${escapeHTML(classifications[d.id] || 'Unclassified')}</td>
      `;
      resultsTableBody.appendChild(tr);
    });

    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // =========================================================================
  // CSV Download
  // =========================================================================

  btnDownload.addEventListener('click', downloadCSV);

  function downloadCSV() {
    const headers = ['id', 'text', ...extraColumns, 'topic'];
    const rows = rawData.map(d => {
      const topic = classifications[d.id] || 'Unclassified';
      const extras = extraColumns.map(c => csvEscape(d[c] || ''));
      return [csvEscape(d.id), csvEscape(d.text), ...extras, csvEscape(topic)].join(',');
    });

    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'e2e_topic_results.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  function csvEscape(val) {
    const s = String(val);
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  }

  // =========================================================================
  // Helpers
  // =========================================================================

  function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // =========================================================================
  // Smooth-scroll for nav links
  // =========================================================================

  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

})();
