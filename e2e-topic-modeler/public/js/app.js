/**
 * E2E Topic Modeler — Main Application Logic
 * Orchestrates CSV upload, the three-stage pipeline, results display, and CSV export.
 */

(() => {
  'use strict';

  // =========================================================================
  // State
  // =========================================================================

  let rawData = [];        // Array of { id, text, ...extra columns }
  let extraColumns = [];   // Column names beyond id and text
  let clusterResult = null; // { labels, centroids, k, matrix, vocabulary, repDocs, topTerms, points2d }
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

  // =========================================================================
  // CSV Parsing
  // =========================================================================

  function parseCSV(text) {
    const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
    if (lines.length < 2) throw new Error('CSV must have a header row and at least one data row.');

    // Parse header
    const headers = parseCSVLine(lines[0]).map(h => h.trim().toLowerCase());

    // Validate required columns
    const idIdx = headers.indexOf('id');
    const textIdx = headers.indexOf('text');
    if (idIdx === -1) throw new Error('CSV must contain an "id" column.');
    if (textIdx === -1) throw new Error('CSV must contain a "text" column.');

    // Track extra columns
    extraColumns = headers.filter((h, i) => i !== idIdx && i !== textIdx);

    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = parseCSVLine(lines[i]);
      if (cols.length < headers.length) continue;

      const row = { id: cols[idIdx].trim(), text: cols[textIdx].trim() };
      // Keep extra columns
      headers.forEach((h, j) => {
        if (j !== idIdx && j !== textIdx) row[h] = cols[j];
      });

      if (row.text.length > 0) data.push(row);
    }

    if (data.length === 0) throw new Error('No valid data rows found in CSV.');
    return data;
  }

  /**
   * Parse a single CSV line respecting quoted fields.
   */
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

        // Reset downstream state
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

  // Drop zone events
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

  // Cluster mode toggle
  clusterModeSelect.addEventListener('change', () => {
    clusterKGroup.style.display = clusterModeSelect.value === 'manual' ? 'inline-flex' : 'none';
  });

  // =========================================================================
  // Pipeline Orchestration
  // =========================================================================

  btnRun.addEventListener('click', runPipeline);

  async function runPipeline() {
    if (rawData.length === 0) return;
    hideError();
    btnRun.disabled = true;
    pipelineProgress.classList.add('visible');
    resultsSection.classList.remove('visible');
    clusterViz.classList.remove('visible');

    try {
      // ---- Stage 1: Embedding & Clustering ----
      setStage(0);
      updateProgress('Building TF-IDF vectors...', 0);

      // Run TF-IDF in a microtask to allow UI update
      await tick();
      const texts = rawData.map(d => d.text);
      const { matrix, vocabulary } = Clustering.buildTFIDF(texts);
      updateProgress('TF-IDF complete. Determining clusters...', 20);
      await tick();

      let k;
      if (clusterModeSelect.value === 'auto') {
        updateProgress('Auto-detecting optimal number of clusters (this may take a moment)...', 25);
        await tick();
        k = Clustering.autoDetectK(matrix, 2, Math.min(15, Math.floor(rawData.length / 5)));
        updateProgress(`Optimal k=${k} detected. Running k-means...`, 40);
      } else {
        k = parseInt(clusterKInput.value, 10) || 5;
        k = Math.max(2, Math.min(k, 20, Math.floor(rawData.length / 2)));
        updateProgress(`Running k-means with k=${k}...`, 35);
      }
      await tick();

      const { labels, centroids } = Clustering.kmeans(matrix, k);
      updateProgress('Clustering complete. Selecting representative documents...', 60);
      await tick();

      const repDocs = Clustering.getRepresentativeDocs(matrix, labels, centroids, 10);
      const topTerms = Clustering.getTopTerms(matrix, labels, vocabulary, k, 10);

      // 2D projection for visualisation
      updateProgress('Projecting clusters for visualization...', 75);
      await tick();
      const points2d = Clustering.projectTo2D(matrix);

      clusterResult = { labels, centroids, k, matrix, vocabulary, repDocs, topTerms, points2d };

      updateProgress('Stage 1 complete.', 100);
      completeStage(0);
      await tick();

      // Draw cluster visualisation
      drawClusterViz();

      // ---- Stage 2: Topic Naming ----
      setStage(1);
      topicInfo = [];

      for (let c = 0; c < k; c++) {
        updateProgress(`Naming topic ${c + 1} of ${k}...`, Math.round((c / k) * 100));
        const repTexts = repDocs[c].map(i => rawData[i].text);
        const terms = topTerms[c];

        const info = await ClaudeAPI.nameTopicDemocratic(repTexts, terms, c, (msg) => {
          updateProgress(msg, Math.round(((c + 0.5) / k) * 100));
        });

        topicInfo.push({ id: c, name: info.name, description: info.description, keywords: info.keywords });
      }

      updateProgress('All topics named.', 100);
      completeStage(1);
      await tick();

      // ---- Stage 3: Document Classification ----
      setStage(2);
      classifications = {};

      // First, assign documents that are already clustered and near centroid
      // using the k-means labels as initial classification
      // Then refine with Claude for all documents in batches
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
          console.warn(`Batch ${b + 1} classification failed, using cluster label:`, err);
          // Fallback: use k-means label
          for (let i = start; i < end; i++) {
            const docId = rawData[i].id;
            if (!classifications[docId]) {
              const label = clusterResult.labels[i];
              classifications[docId] = topicInfo[label] ? topicInfo[label].name : `Topic ${label + 1}`;
            }
          }
        }
      }

      // Fill any missing classifications with k-means labels
      rawData.forEach((d, i) => {
        if (!classifications[d.id]) {
          const label = clusterResult.labels[i];
          classifications[d.id] = topicInfo[label] ? topicInfo[label].name : `Topic ${label + 1}`;
        }
      });

      updateProgress('Classification complete.', 100);
      completeStage(2);
      await tick();

      // ---- Render Results ----
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

  /** Yield to the event loop so the browser can repaint. */
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

    // Find bounds
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

    // Draw points
    points.forEach((p, i) => {
      const x = padding + ((p.x - minX) / rangeX) * (W - 2 * padding);
      const y = padding + ((p.y - minY) / rangeY) * (H - 2 * padding);
      const color = COLORS[labels[i] % COLORS.length];

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.7;
      ctx.fill();
      ctx.globalAlpha = 1;
    });

    // Legend
    const k = clusterResult.k;
    const legendX = W - 160;
    let legendY = 20;

    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.fillRect(legendX - 10, legendY - 10, 160, k * 22 + 16);
    ctx.strokeStyle = '#dee2e6';
    ctx.strokeRect(legendX - 10, legendY - 10, 160, k * 22 + 16);

    for (let c = 0; c < k; c++) {
      const color = COLORS[c % COLORS.length];
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(legendX, legendY + 6, 5, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#343a40';
      ctx.font = '12px -apple-system, sans-serif';
      const label = topicInfo[c] ? topicInfo[c].name : `Cluster ${c + 1}`;
      ctx.fillText(label.slice(0, 18), legendX + 12, legendY + 10);
      legendY += 22;
    }
  }

  // =========================================================================
  // Results Rendering
  // =========================================================================

  function renderResults() {
    resultsSection.classList.add('visible');

    // Topic cards
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

    // Re-draw viz with topic names now available
    drawClusterViz();

    // Documents table (show first 100)
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

    // Scroll to results
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
