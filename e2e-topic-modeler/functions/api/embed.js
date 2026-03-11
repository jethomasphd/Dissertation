/**
 * E2E Topic Modeler — Voyage AI Embedding Proxy
 * Pages Function route:  POST /api/embed  →  this handler
 *
 * Proxies embedding requests to the Voyage AI API, injecting the API key from environment.
 * The VOYAGE_API_KEY must be set in the Pages project's environment variables (encrypted).
 *
 * Request body:  { "texts": ["doc1", "doc2", ...], "model": "voyage-3" }
 * Response body: { "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...], ...] }
 */

// ---- CORS preflight ----
export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: corsHeaders(),
  });
}

// ---- Main handler (POST only) ----
export async function onRequestPost(context) {
  const { request, env } = context;

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'Invalid JSON body' }, 400);
  }

  if (!body.texts || !Array.isArray(body.texts) || body.texts.length === 0) {
    return jsonResponse({ error: 'texts array is required' }, 400);
  }

  if (!env.VOYAGE_API_KEY) {
    return jsonResponse({ error: 'Server misconfiguration: VOYAGE_API_KEY not set' }, 500);
  }

  const model = body.model || 'voyage-3';

  try {
    const response = await fetch('https://api.voyageai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.VOYAGE_API_KEY}`,
      },
      body: JSON.stringify({
        model,
        input: body.texts,
        input_type: body.input_type || 'document',
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      return jsonResponse({
        error: 'Voyage API error',
        detail: result.detail || result.message || JSON.stringify(result),
      }, response.status);
    }

    // Extract just the embedding vectors, sorted by index
    const sorted = (result.data || []).sort((a, b) => a.index - b.index);
    const embeddings = sorted.map(item => item.embedding);

    return new Response(JSON.stringify({ embeddings, model: result.model }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders(),
      },
    });
  } catch (err) {
    return jsonResponse({ error: 'Upstream Voyage API request failed', detail: err.message }, 502);
  }
}

// ---- Helpers ----

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function jsonResponse(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(),
    },
  });
}
