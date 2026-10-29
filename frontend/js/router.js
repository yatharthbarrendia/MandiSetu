/**
 * MandiSetu Client-side Routing & Navigation Helper
 */

export function getQueryParams() {
  const params = {};
  const search = window.location.search.substring(1);
  if (!search) return params;
  
  const pairs = search.split("&");
  for (const pair of pairs) {
    const [key, value] = pair.split("=");
    if (key) {
      params[decodeURIComponent(key)] = decodeURIComponent(value || "");
    }
  }
  return params;
}

export function navigateTo(path, params = {}) {
  const qs = new URLSearchParams(params).toString();
  const url = qs ? `${path}?${qs}` : path;
  window.location.href = url;
}
