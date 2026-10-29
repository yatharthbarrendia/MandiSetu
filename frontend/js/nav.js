/**
 * MandiSetu Shared Navigation Bar Component
 * Automatically injects the top header and role-based navigation tabs.
 */
import { getCurrentUser, logout } from "./auth.js";
import { getLanguage, setLanguage, t, applyTranslations } from "./i18n.js";
import { api } from "./api.js";

export function renderNav(activeModuleId = "") {
  const user = getCurrentUser();
  const currentLang = getLanguage();

  const headerHtml = `
    <header class="app-header">
      <div class="brand-wrapper">
        <span class="brand-logo-icon">🌾</span>
        <div class="brand-text">
          <a href="/dashboard" style="text-decoration:none; color:inherit;">
            <h1>MandiSetu <span style="font-size:0.75rem; background:var(--accent-saffron); padding:2px 6px; border-radius:4px; margin-left:4px;">SIH26132</span></h1>
          </a>
          <span class="brand-subtitle" data-i18n="app_tagline">AI Market-Intelligence & Linkages (Govt. of Maharashtra)</span>
        </div>
      </div>

      <div class="header-actions">
        <div class="lang-selector">
          <select id="app-lang-select" aria-label="Select Language">
            <option value="en" ${currentLang === 'en' ? 'selected' : ''}>English</option>
            <option value="hi" ${currentLang === 'hi' ? 'selected' : ''}>हिन्दी (Hindi)</option>
            <option value="mr" ${currentLang === 'mr' ? 'selected' : ''}>मराठी (Marathi)</option>
          </select>
        </div>

        ${user ? `
          <div class="user-badge">
            <span class="badge badge-${user.role.toLowerCase()}">${user.role}</span>
            <span style="font-weight:600;">${user.full_name || user.email}</span>
            <span style="color:#94a3b8; font-size:0.75rem;">(${user.district || 'Maharashtra'})</span>
          </div>
          <button id="nav-logout-btn" class="btn btn-secondary btn-sm" title="Logout">
            🚪 <span data-i18n="logout">Logout</span>
          </button>
        ` : `
          <a href="/" class="btn btn-accent btn-sm" data-i18n="login">Login</a>
        `}
      </div>
    </header>

    ${user ? `
      <nav class="nav-container">
        <ul class="nav-tabs" id="nav-menu-tabs">
          ${getRoleNavLinks(user.role, activeModuleId)}
        </ul>
      </nav>
    ` : ''}
  `;

  const headerPlaceholder = document.getElementById("app-nav-header");
  if (headerPlaceholder) {
    headerPlaceholder.innerHTML = headerHtml;
  } else {
    const div = document.createElement("div");
    div.id = "app-nav-header";
    div.innerHTML = headerHtml;
    document.body.prepend(div);
  }

  // Attach event handlers
  const langSelect = document.getElementById("app-lang-select");
  if (langSelect) {
    langSelect.addEventListener("change", async (e) => {
      await setLanguage(e.target.value);
      applyTranslations();
      renderNav(activeModuleId);
    });
  }

  const logoutBtn = document.getElementById("nav-logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      logout();
    });
  }

  applyTranslations();
}

function getRoleNavLinks(role, activeModuleId) {
  role = (role || "").toLowerCase();

  const links = [
    { id: "dashboard", label: "Dashboard", url: "/dashboard", icon: "📊" },
    { id: "module-01", label: "Profile & Users", url: "/modules/module-01/module1.html", icon: "👤" },
    { id: "module-02", label: "Price Discovery", url: "/modules/module-02/module2.html", icon: "📈" },
    { id: "module-03", label: "Net Realization", url: "/modules/module-03/module3.html", icon: "💰" },
    { id: "module-04", label: "Produce Listing", url: "/modules/module-04/module4.html", icon: "📦" },
    { id: "module-05", label: "Offers & Demand", url: "/modules/module-05/module5.html", icon: "🤝" },
    { id: "module-06", label: "Transactions", url: "/modules/module-06/module6.html", icon: "📑" },
    { id: "module-07", label: "Sale Window AI", url: "/modules/module-07/module7.html", icon: "⏱️" },
    { id: "module-08", label: "Buyer Trust", url: "/modules/module-08/module8.html", icon: "🛡️" },
    { id: "module-09", label: "Logistics", url: "/modules/module-09/module9.html", icon: "🚚" },
    { id: "module-10", label: "Disputes", url: "/modules/module-10/module10.html", icon: "⚖️" },
    { id: "module-11", label: "Quality Grading", url: "/modules/module-11/module11.html", icon: "🔬" },
    { id: "module-12", label: "Weather Risk", url: "/modules/module-12/module12.html", icon: "🌦️" },
    { id: "module-13", label: "Admin Analytics", url: "/modules/module-13/module13.html", icon: "🏛️" }
  ];

  return links.map(link => {
    const isActive = activeModuleId === link.id ? "active" : "";
    return `<li><a href="${link.url}" class="${isActive}">${link.icon} ${link.label}</a></li>`;
  }).join("");
}
