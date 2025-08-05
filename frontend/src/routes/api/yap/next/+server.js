import { AI_API_ENDPOINT } from "$env/static/private";

export async function POST({ request, url }) {
  try {
    const yap_session_id = url.searchParams.get("yap_session_id");
    const language = url.searchParams.get("language");

    if (!yap_session_id) {
      return new Response(
        JSON.stringify({ error: "yap_session_id query parameter is required" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    let backendUrl = `${AI_API_ENDPOINT}/yap/next?yap_session_id=${encodeURIComponent(yap_session_id)}`;
    if (language) {
      backendUrl += `&language=${encodeURIComponent(language)}`;
    }

    const response = await fetch(backendUrl, {
      method: "POST",
    });

    const result = await response.json();
    return new Response(JSON.stringify(result), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      },
    );
  }
}
