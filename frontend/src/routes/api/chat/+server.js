import { AI_API_ENDPOINT } from "$env/static/private";

export async function POST({ request }) {
  try {
    const contentType = request.headers.get("content-type");

    let response;
    if (contentType && contentType.includes("multipart/form-data")) {
      // Handle FormData (audio from SingleRecordingSection)
      const formData = await request.formData();
      response = await fetch(`${AI_API_ENDPOINT}/chat`, {
        method: "POST",
        body: formData,
      });
    } else {
      // Handle JSON (text messages)
      const { message, intentcode, session_id } = await request.json();
      const requestBody = {
        message,
        ...(intentcode && { intentcode }),
        ...(session_id && { session_id }),
      };

      response = await fetch(`${AI_API_ENDPOINT}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
    }

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
