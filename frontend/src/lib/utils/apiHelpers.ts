// API helper functions for different endpoints
export type EndpointType = "analyze" | "chat" | "yap" | "yapStart" | "yapNext" | "feedback" | "feedback-transcribe";

export interface ApiResponse {
  data: any;
  error: string | null;
  isLoading: boolean;
}

export async function sendToEndpoint(
  endpoint: EndpointType,
  data: any,
  language?: string,
): Promise<any> {
  const endpointMap = {
    analyze: "/api/analyze",
    chat: "/api/chat",
    yap: "/api/yap",
    yapStart: "/api/yap/start",
    yapNext: "/api/yap/next",
    feedback: "/api/feedback",
    "feedback-transcribe": "/api/feedback-transcribe",
  };

  const url = endpointMap[endpoint];

  if (!url) {
    throw new Error(`Unknown endpoint: ${endpoint}`);
  }

  const requestInit: RequestInit = {
    method: "POST",
  };

  // Handle different data types based on endpoint
  if (endpoint === "chat" || endpoint === "feedback" || endpoint === "feedback-transcribe") {
    // chat, feedback, and feedback-transcribe endpoints support both JSON and FormData modes
    if (data instanceof FormData) {
      // Multipart mode - add language to FormData if provided
      if (language) {
        data.append("language", language);
      }
      requestInit.body = data;
    } else {
      // JSON mode - add language to data object if provided
      const requestData = language ? { ...data, language } : data;
      requestInit.headers = { "Content-Type": "application/json" };
      requestInit.body = JSON.stringify(requestData);
    }
  } else if (endpoint === "yapStart") {
    // JSON for yapStart - add language to data object if provided
    const requestData = language ? { ...data, language } : data;
    requestInit.headers = { "Content-Type": "application/json" };
    requestInit.body = JSON.stringify(requestData);
  } else if (endpoint === "yapNext") {
    // yapNext needs query parameter handling
    const { yap_session_id } = data;
    if (yap_session_id) {
      const url = new URL(endpointMap[endpoint], window.location.origin);
      url.searchParams.set("yap_session_id", yap_session_id);
      if (language) {
        url.searchParams.set("language", language);
      }
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
    // FormData for audio endpoints (analyze, yap) - add language if provided
    if (language) {
      data.append("language", language);
    }
    requestInit.body = data;
  }

  const response = await fetch(url, requestInit);
  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.error || "Request failed");
  }

  return result;
}
