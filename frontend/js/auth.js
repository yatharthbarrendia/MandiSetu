/**
 * MandiSetu Authentication & Session Service
 */

const USER_KEY = "mandisetu_user";
const TOKEN_KEY = "mandisetu_access_token";
const REFRESH_KEY = "mandisetu_refresh_token";

export function getCurrentUser() {
  const data = localStorage.getItem(USER_KEY);
  if (!data) return null;
  try {
    return JSON.parse(data);
  } catch (e) {
    return null;
  }
}

export function isAuthenticated() {
  return !!localStorage.getItem(TOKEN_KEY) && !!getCurrentUser();
}

export function saveSession(user, tokens) {
  if (tokens.access_token) localStorage.setItem(TOKEN_KEY, tokens.access_token);
  if (tokens.refresh_token) localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

export function hasRole(...roles) {
  const user = getCurrentUser();
  if (!user || !user.role) return false;
  return roles.map(r => r.toLowerCase()).includes(user.role.toLowerCase());
}

export function logout() {
  clearSession();
  window.location.href = "/";
}

export function requireAuth(allowedRoles = []) {
  if (!isAuthenticated()) {
    window.location.href = "/";
    return false;
  }
  if (allowedRoles.length > 0 && !hasRole(...allowedRoles)) {
    alert("Unauthorized: Your role does not have access to this section.");
    window.location.href = "/dashboard";
    return false;
  }
  return true;
}
