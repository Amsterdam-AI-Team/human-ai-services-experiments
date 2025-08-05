import { AI_API_ENDPOINT } from "$env/static/private";

export async function POST({ request }) {
  try {
    // Handle JSON (text feedback only)
    const { feedback, session_id, concept, language } = await request.json();
    const requestBody = {
      feedback,
      ...(session_id && { session_id }),
      ...(concept && { concept }),
      ...(language && { language }),
    };

    const response = await fetch(`${AI_API_ENDPOINT}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    });

    const result = await response.json();
    return new Response(JSON.stringify(result), {
      status: response.status,
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