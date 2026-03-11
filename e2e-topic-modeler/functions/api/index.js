/**
 * E2E Topic Modeler — Cloudflare Pages Function
 * Proxies POST requests to the Anthropic Claude API, injecting the API key from environment.
 *
 * Pages Functions route:  POST /api  →  this handler
 * The ANTHROPIC_API_KEY must be set in the Pages project's environment variables (encrypted).
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

  // Parse the incoming request
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'Invalid JSON body' }, 400);
  }

  // Validate that messages are present
  if (!body.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
    return jsonResponse({ error: 'messages array is required' }, 400);
  }

  // Check that the API key is configured
  if (!env.ANTHROPIC_API_KEY) {
    return jsonResponse({ error: 'Server misconfiguration: API key not set' }, 500);
  }

  // Build the upstream request
  const upstreamBody = {
    model: body.model || 'claude-sonnet-4-5-20250514',
    max_tokens: body.max_tokens || 1024,
    messages: body.messages,
  };

  if (body.system) {
    upstreamBody.system = body.system;
  }
  if (body.temperature !== undefined) {
    upstreamBody.temperature = body.temperature;
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(upstreamBody),
    });

    const result = await response.json();

    return new Response(JSON.stringify(result), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders(),
      },
    });
  } catch (err) {
    return jsonResponse({ error: 'Upstream API request failed', detail: err.message }, 502);
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
