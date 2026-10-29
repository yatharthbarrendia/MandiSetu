/**
 * MandiSetu UI Utilities
 */

export function formatCurrency(amount) {
  if (amount === null || amount === undefined || isNaN(amount)) return "₹0";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(amount);
}

export function formatDate(dateStr) {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric"
  });
}

export function formatDateTime(dateStr) {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit"
  });
}

export function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.style.position = "fixed";
    container.style.bottom = "20px";
    container.style.right = "20px";
    container.style.zIndex = "9999";
    container.style.display = "flex";
    container.style.flexDirection = "column";
    container.style.gap = "10px";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `alert alert-${type}`;
  toast.style.boxShadow = "0 4px 6px -1px rgba(0,0,0,0.1)";
  toast.style.margin = "0";
  toast.style.minWidth = "260px";
  toast.textContent = message;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.4s ease";
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

export function renderLoading(container) {
  if (typeof container === "string") container = document.querySelector(container);
  if (!container) return;
  container.innerHTML = `
    <div class="loading-box">
      <div class="spinner"></div>
      <p>Loading data...</p>
    </div>
  `;
}

export function renderError(container, message) {
  if (typeof container === "string") container = document.querySelector(container);
  if (!container) return;
  container.innerHTML = `
    <div class="alert alert-danger" style="margin: 1.5rem 0;">
      <span>⚠️ ${message || "An error occurred while loading content."}</span>
    </div>
  `;
}

export function renderEmpty(container, message = "No records found.", icon = "📦") {
  if (typeof container === "string") container = document.querySelector(container);
  if (!container) return;
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">${icon}</div>
      <p>${message}</p>
    </div>
  `;
}
