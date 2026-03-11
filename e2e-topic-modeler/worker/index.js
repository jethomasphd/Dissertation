/**
 * E2E Topic Modeler — Cloudflare Worker
 * Routes:
 *   POST /chat   → Anthropic Claude API  (topic naming & classification)
 *   POST /embed  → Voyage AI API         (document embeddings)
 *   GET  /       → Service info
 *
 * Secrets (set via `wrangler secret put`):
 *   ANTHROPIC_API_KEY
 *   VOYAGE_API_KEY
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';

    // ---- CORS preflight ----
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    // ---- Health / info ----
    if (request.method === 'GET' && path === '/') {
      return jsonResponse({
        service: 'E2E Topic Modeler API',
        routes: ['POST /chat', 'POST /embed'],
      });
    }

    // ---- Only POST beyond this point ----
    if (request.method !== 'POST') {
      return jsonResponse({ error: 'Method not allowed' }, 405);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return jsonResponse({ error: 'Invalid JSON body' }, 400);
    }

    // ---- Route ----
    if (path === '/embed') {
      return handleEmbed(body, env);
    }
    // /chat or / both go to Claude
    if (path === '/chat' || path === '/') {
      return handleChat(body, env);
    }

    return jsonResponse({ error: `Unknown route: ${path}` }, 404);
  },
};

// ===========================================================================
// Claude handler
// ===========================================================================

async function handleChat(body, env) {
  if (!body.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
    return jsonResponse({ error: 'messages array is required' }, 400);
  }
  if (!env.ANTHROPIC_API_KEY) {
    return jsonResponse({ error: 'Server misconfiguration: ANTHROPIC_API_KEY not set' }, 500);
  }

  const upstreamBody = {
    model: body.model || 'claude-sonnet-4-5-20250514',
    max_tokens: body.max_tokens || 1024,
    messages: body.messages,
  };
  if (body.system) upstreamBody.system = body.system;
  if (body.temperature !== undefined) upstreamBody.temperature = body.temperature;

  try {
    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(upstreamBody),
    });

    const result = await resp.json();
    return new Response(JSON.stringify(result), {
      status: resp.status,
      headers: { 'Content-Type': 'application/json', ...corsHeaders() },
    });
  } catch (err) {
    return jsonResponse({ error: 'Upstream Claude API request failed', detail: err.message }, 502);
  }
}

// ===========================================================================
// Voyage AI handler
// ===========================================================================

async function handleEmbed(body, env) {
  if (!body.texts || !Array.isArray(body.texts) || body.texts.length === 0) {
    return jsonResponse({ error: 'texts array is required' }, 400);
  }
  if (!env.VOYAGE_API_KEY) {
    return jsonResponse({ error: 'Server misconfiguration: VOYAGE_API_KEY not set' }, 500);
  }

  const model = body.model || 'voyage-3';

  try {
    const resp = await fetch('https://api.voyageai.com/v1/embeddings', {
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

    const result = await resp.json();

    if (!resp.ok) {
      return jsonResponse({
        error: 'Voyage API error',
        detail: result.detail || result.message || JSON.stringify(result),
      }, resp.status);
    }

    const sorted = (result.data || []).sort((a, b) => a.index - b.index);
    const embeddings = sorted.map(item => item.embedding);

    return new Response(JSON.stringify({ embeddings, model: result.model }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', ...corsHeaders() },
    });
  } catch (err) {
    return jsonResponse({ error: 'Upstream Voyage API request failed', detail: err.message }, 502);
  }
}

// ===========================================================================
// Helpers
// ===========================================================================

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function jsonResponse(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders() },
  });
}
