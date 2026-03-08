/**
 * E2E Topic Modeler — Claude API Module
 * Handles all communication with the Cloudflare Worker proxy to the Claude API.
 */

const ClaudeAPI = (() => {
  'use strict';

  // The worker endpoint — when deployed to Cloudflare Pages + Worker,
  // the worker is bound at /api/.  For local dev you can override this.
  let API_ENDPOINT = '/api/';

  const MODEL = 'claude-sonnet-4-5-20250514';

  /**
   * Override the API endpoint (useful for local development).
   */
  function setEndpoint(url) {
    API_ENDPOINT = url;
  }

  /**
   * Send a message to Claude via the worker proxy.
   * @param {Object} options
   * @param {string} options.system - system prompt
   * @param {Array}  options.messages - messages array [{role, content}]
   * @param {number} [options.maxTokens=1024]
   * @param {number} [options.temperature=0.3]
   * @returns {Promise<string>} Claude's text response
   */
  async function sendMessage({ system, messages, maxTokens = 1024, temperature = 0.3 }) {
    const body = {
      model: MODEL,
      max_tokens: maxTokens,
      messages,
      temperature,
    };
    if (system) body.system = system;

    const resp = await fetch(API_ENDPOINT, {
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

    // Extract text from content blocks
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

  /**
   * Name a single topic cluster by sending representative documents to Claude
   * five times and taking a majority vote on the topic name.
   *
   * @param {string[]} repTexts - representative document texts for this cluster
   * @param {string[]} topTerms - top TF-IDF terms for this cluster
   * @param {number} clusterId
   * @param {Function} [onProgress] - called with intermediate status
   * @returns {Promise<{name: string, description: string, keywords: string[]}>}
   */
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

    // Majority vote on name (case-insensitive)
    const freq = {};
    names.forEach(n => {
      const key = n.toLowerCase();
      freq[key] = (freq[key] || 0) + 1;
    });

    let majorityKey = Object.keys(freq).sort((a, b) => freq[b] - freq[a])[0];

    // Find the result that matches the majority name
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

  /**
   * Classify a batch of documents into the discovered topics.
   *
   * @param {Array<{id: string, text: string}>} docs - batch of documents
   * @param {Array<{id: number, name: string, description: string}>} topics
   * @returns {Promise<Object<string, string>>} mapping of doc id -> topic name
   */
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

  /**
   * Robustly parse JSON from Claude's response, handling markdown fences.
   */
  function parseJSON(text) {
    // Strip markdown code fences if present
    let cleaned = text.trim();
    cleaned = cleaned.replace(/^```(?:json)?\s*\n?/i, '').replace(/\n?```\s*$/i, '');
    cleaned = cleaned.trim();

    try {
      return JSON.parse(cleaned);
    } catch {
      // Try to find JSON object or array in the text
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
    setEndpoint,
    sendMessage,
    nameTopicDemocratic,
    classifyBatch,
  };
})();
