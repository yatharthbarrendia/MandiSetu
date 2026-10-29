/**
 * MandiSetu Shared API Client
 * Automatically attaches Authorization headers, handles token refresh, and standardizes error responses.
 */

const TOKEN_KEY = "mandisetu_access_token";
const REFRESH_KEY = "mandisetu_refresh_token";

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Handle FormData (don't set Content-Type header so browser sets multipart boundary)
  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
  }

  const config = {
    ...options,
    headers
  };

  try {
    let response = await fetch(endpoint, config);

    // If 401 Unauthorized, attempt refresh once
    if (response.status === 401 && localStorage.getItem(REFRESH_KEY)) {
      const refreshed = await attemptTokenRefresh();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${localStorage.getItem(TOKEN_KEY)}`;
        config.headers = headers;
        response = await fetch(endpoint, config);
      } else {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem("mandisetu_user");
        if (window.location.pathname !== "/" && window.location.pathname !== "/index.html") {
          window.location.href = "/";
        }
      }
    }

    if (!response.ok) {
      let errDetail = `HTTP Error ${response.status}`;
      try {
        const errJson = await response.json();
        errDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
      } catch (e) {
        errDetail = await response.text();
      }
      throw new Error(errDetail);
    }

    // Return blob if response is PDF or octet-stream
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/pdf") || contentType.includes("application/octet-stream")) {
      return await response.blob();
    }

    return await response.json();
  } catch (error) {
    console.error(`[API Error] ${endpoint}:`, error);
    throw error;
  }
}

async function attemptTokenRefresh() {
  const refreshToken = localStorage.getItem(REFRESH_KEY);
  if (!refreshToken) return false;

  try {
    const res = await fetch("/api/users/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem(TOKEN_KEY, data.access_token);
      if (data.refresh_token) {
        localStorage.setItem(REFRESH_KEY, data.refresh_token);
      }
      return true;
    }
    return false;
  } catch (e) {
    return false;
  }
}

export const api = {
  get: (url, params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiRequest(qs ? `${url}?${qs}` : url, { method: "GET" });
  },
  post: (url, body = {}) => {
    return apiRequest(url, {
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body)
    });
  },
  put: (url, body = {}) => {
    return apiRequest(url, {
      method: "PUT",
      body: body instanceof FormData ? body : JSON.stringify(body)
    });
  },
  delete: (url) => {
    return apiRequest(url, { method: "DELETE" });
  }
};
