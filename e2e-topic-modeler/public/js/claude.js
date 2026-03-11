/**
 * E2E Topic Modeler — API Module
 * Handles all communication with the Cloudflare Worker:
 *   POST <workerUrl>/chat   → Claude API  (topic naming & classification)
 *   POST <workerUrl>/embed  → Voyage AI   (document embeddings)
 *
 * The worker URL must be set via setWorkerUrl() before making API calls.
 */

const ClaudeAPI = (() => {
  'use strict';

  let WORKER_URL  = '';          // e.g. "https://e2e-topic-modeler-api.you.workers.dev"
  const CLAUDE_MODEL = 'claude-sonnet-4-5-20250514';
  const VOYAGE_MODEL = 'voyage-3';
  const EMBED_BATCH  = 96;      // Voyage supports 128; leave headroom

  /**
   * Set the worker base URL.
   * @param {string} url - full URL without trailing slash
   */
  function setWorkerUrl(url) {
    WORKER_URL = url.replace(/\/+$/, '');
  }

  /** Return the current worker URL (for UI display). */
  function getWorkerUrl() {
    return WORKER_URL;
  }

  // =========================================================================
  // Voyage AI Embeddings
  // =========================================================================

  /**
   * Embed an array of document texts using Voyage AI (via worker proxy).
   * Automatically batches to stay within API limits.
   *
   * @param {string[]} texts
   * @param {Function} [onProgress] - (batchIndex, totalBatches)
   * @returns {Promise<number[][]>} embedding vectors
   */
  async function embedDocuments(texts, onProgress) {
    const allEmbeddings = new Array(texts.length);
    const totalBatches = Math.ceil(texts.length / EMBED_BATCH);

    for (let b = 0; b < totalBatches; b++) {
      const start = b * EMBED_BATCH;
      const end = Math.min(start + EMBED_BATCH, texts.length);
      const batch = texts.slice(start, end);

      if (onProgress) onProgress(b + 1, totalBatches);

      const resp = await fetch(`${WORKER_URL}/embed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          texts: batch,
          model: VOYAGE_MODEL,
          input_type: 'document',
        }),
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`Embedding API error (${resp.status}): ${text}`);
      }

      const data = await resp.json();

      if (data.error) {
        throw new Error(`Voyage API error: ${data.error}`);
      }

      if (!data.embeddings || data.embeddings.length !== batch.length) {
        throw new Error(`Expected ${batch.length} embeddings, got ${(data.embeddings || []).length}`);
      }

      for (let i = 0; i < data.embeddings.length; i++) {
        allEmbeddings[start + i] = data.embeddings[i];
      }
    }

    return allEmbeddings;
  }

  // =========================================================================
  // Claude Messages
  // =========================================================================

  /**
   * Send a message to Claude via the worker proxy.
   */
  async function sendMessage({ system, messages, maxTokens = 1024, temperature = 0.3 }) {
    const body = {
      model: CLAUDE_MODEL,
      max_tokens: maxTokens,
      messages,
      temperature,
    };
    if (system) body.system = system;

    const resp = await fetch(`${WORKER_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`API error (${resp.status}): ${text}`);
    }

    const data = await resp.json();

    if (data.error) {
      throw new Error(`Claude API error: ${data.error.message || JSON.stringify(data.error)}`);
    }

    if (data.content && Array.isArray(data.content)) {
      return data.content
        .filter(b => b.type === 'text')
        .map(b => b.text)
        .join('\n');
    }

    throw new Error('Unexpected API response format');
  }

  // =========================================================================
  // Stage 2: Topic Naming (democratic voting — 5 calls, majority name)
  // =========================================================================

  async function nameTopicDemocratic(repTexts, topTerms, clusterId, onProgress) {
    const systemPrompt = `You are an expert qualitative researcher performing topic modeling analysis. You will be given a set of representative documents from a single cluster along with the most frequent terms. Your job is to name the topic and provide a brief description.

Respond ONLY in valid JSON with exactly these keys:
{
  "name": "<concise topic name, 2-6 words>",
  "description": "<one-sentence description of what this topic covers>",
  "keywords": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"]
}

Do not include any text outside the JSON object.`;

    const userContent = `Here are the representative documents from Cluster ${clusterId + 1}:

${repTexts.map((t, i) => `[Doc ${i + 1}]: ${t.slice(0, 500)}`).join('\n\n')}

Top terms in this cluster: ${topTerms.join(', ')}

Please name this topic and describe what it's about.`;

    const VOTES = 5;
    const names = [];
    const results = [];

    for (let v = 0; v < VOTES; v++) {
      if (onProgress) onProgress(`Vote ${v + 1}/${VOTES} for Cluster ${clusterId + 1}`);
      try {
        const text = await sendMessage({
          system: systemPrompt,
          messages: [{ role: 'user', content: userContent }],
          maxTokens: 300,
          temperature: 0.4,
        });

        const parsed = parseJSON(text);
        if (parsed && parsed.name) {
          names.push(parsed.name.trim());
          results.push(parsed);
        }
      } catch (err) {
        console.warn(`Vote ${v + 1} for cluster ${clusterId} failed:`, err);
      }
    }

    if (results.length === 0) {
      return {
        name: `Topic ${clusterId + 1}`,
        description: 'Could not determine topic name.',
        keywords: topTerms.slice(0, 5),
      };
    }

    // Majority vote (case-insensitive)
    const freq = {};
    names.forEach(n => {
      const key = n.toLowerCase();
      freq[key] = (freq[key] || 0) + 1;
    });

    const majorityKey = Object.keys(freq).sort((a, b) => freq[b] - freq[a])[0];
    const winner = results.find(r => r.name.trim().toLowerCase() === majorityKey) || results[0];

    return {
      name: winner.name,
      description: winner.description || '',
      keywords: winner.keywords || topTerms.slice(0, 5),
    };
  }

  // =========================================================================
  // Stage 3: Document Classification
  // =========================================================================

  async function classifyBatch(docs, topics) {
    const topicList = topics.map(t => `- "${t.name}": ${t.description}`).join('\n');

    const systemPrompt = `You are a document classifier. You will be given a list of topics and a batch of documents. Classify each document into the single most appropriate topic.

Available topics:
${topicList}

Respond ONLY in valid JSON: an array of objects with "id" and "topic" keys.
Example: [{"id": "1", "topic": "Topic Name"}, {"id": "2", "topic": "Another Topic"}]

Do not include any text outside the JSON array.`;

    const docList = docs.map(d => `[ID: ${d.id}]: ${d.text.slice(0, 300)}`).join('\n\n');

    const text = await sendMessage({
      system: systemPrompt,
      messages: [{ role: 'user', content: `Classify these documents:\n\n${docList}` }],
      maxTokens: 1500,
      temperature: 0.1,
    });

    const parsed = parseJSON(text);
    if (!Array.isArray(parsed)) {
      throw new Error('Classification response was not a JSON array');
    }

    const result = {};
    parsed.forEach(item => {
      if (item.id !== undefined && item.topic) {
        result[String(item.id)] = item.topic;
      }
    });

    return result;
  }

  // =========================================================================
  // Helpers
  // =========================================================================

  function parseJSON(text) {
    let cleaned = text.trim();
    cleaned = cleaned.replace(/^```(?:json)?\s*\n?/i, '').replace(/\n?```\s*$/i, '');
    cleaned = cleaned.trim();

    try {
      return JSON.parse(cleaned);
    } catch {
      const objMatch = cleaned.match(/\{[\s\S]*\}/);
      const arrMatch = cleaned.match(/\[[\s\S]*\]/);

      if (objMatch) {
        try { return JSON.parse(objMatch[0]); } catch { /* fall through */ }
      }
      if (arrMatch) {
        try { return JSON.parse(arrMatch[0]); } catch { /* fall through */ }
      }

      console.warn('Failed to parse JSON from Claude response:', text);
      return null;
    }
  }

  // =========================================================================
  // Public API
  // =========================================================================

  return {
    setWorkerUrl,
    getWorkerUrl,
    embedDocuments,
    sendMessage,
    nameTopicDemocratic,
    classifyBatch,
  };
})();
