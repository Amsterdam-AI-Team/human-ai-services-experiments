import { AI_API_ENDPOINT } from "$env/static/private";

export async function POST({ request }) {
  try {
    const formData = await request.formData();
    
    // Extract language parameter if provided
    const language = formData.get("language");
    let url = `${AI_API_ENDPOINT}/analyze?top_k=999`;
    if (language && typeof language === "string") {
      url += `&language=${encodeURIComponent(language)}`;
    }

    const response = await fetch(url, {
      method: "POST",
      body: formData,
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
