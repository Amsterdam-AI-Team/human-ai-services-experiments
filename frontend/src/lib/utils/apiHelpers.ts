// API helper functions for different endpoints
export type EndpointType = "analyze" | "chat" | "yap" | "yapStart" | "yapNext";

export interface ApiResponse {
  data: any;
  error: string | null;
  isLoading: boolean;
}

export async function sendToEndpoint(
  endpoint: EndpointType,
  data: any,
): Promise<any> {
  const endpointMap = {
    analyze: "/api/analyze",
    chat: "/api/chat",
    yap: "/api/yap",
    yapStart: "/api/yap/start",
    yapNext: "/api/yap/next",
  };

  const url = endpointMap[endpoint];

  if (!url) {
    throw new Error(`Unknown endpoint: ${endpoint}`);
  }

  const requestInit: RequestInit = {
    method: "POST",
  };

  // Handle different data types based on endpoint
  if (endpoint === "chat") {
    // chat endpoint supports both JSON and FormData modes
    if (data instanceof FormData) {
      // Multipart mode - don't set Content-Type (let browser set it)
      requestInit.body = data;
    } else {
      // JSON mode
      requestInit.headers = { "Content-Type": "application/json" };
      requestInit.body = JSON.stringify(data);
    }
  } else if (endpoint === "yapStart") {
    // JSON for yapStart
    requestInit.headers = { "Content-Type": "application/json" };
    requestInit.body = JSON.stringify(data);
  } else if (endpoint === "yapNext") {
    // yapNext needs query parameter handling
    const { yap_session_id } = data;
    if (yap_session_id) {
      const url = new URL(endpointMap[endpoint], window.location.origin);
      url.searchParams.set("yap_session_id", yap_session_id);
      return fetch(url.toString(), { method: "POST" }).then((response) => {
        if (!response.ok) {
          return response.json().then((result) => {
            throw new Error(result.error || "Request failed");
          });
        }
        return response.json();
      });
    } else {
      throw new Error("yap_session_id is required for yapNext endpoint");
    }
  } else {
    // FormData for audio endpoints (analyze, yap)
    requestInit.body = data;
  }

  const response = await fetch(url, requestInit);
  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.error || "Request failed");
  }

  return result;
}
