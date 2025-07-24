import { AI_API_ENDPOINT } from "$env/static/private";

export async function POST({ request, url }) {
  try {
    const yap_session_id = url.searchParams.get("yap_session_id");

    if (!yap_session_id) {
      return new Response(
        JSON.stringify({ error: "yap_session_id query parameter is required" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    const response = await fetch(
      `${AI_API_ENDPOINT}/yap/next?yap_session_id=${encodeURIComponent(yap_session_id)}`,
      {
        method: "POST",
      },
    );

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
