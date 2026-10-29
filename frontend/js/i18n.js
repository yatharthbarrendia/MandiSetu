/**
 * MandiSetu i18n Internationalization Engine
 * Supports English (en), Hindi (hi), and Marathi (mr).
 */

const LANG_KEY = "mandisetu_lang";
let currentLang = localStorage.getItem(LANG_KEY) || "en";
let translations = {};

export async function initI18n(lang = null) {
  if (lang) {
    currentLang = lang;
    localStorage.setItem(LANG_KEY, currentLang);
  }
  try {
    const res = await fetch(`/i18n/${currentLang}.json`);
    if (res.ok) {
      translations = await res.json();
    } else {
      console.warn(`Could not load /i18n/${currentLang}.json, falling back to en`);
      const fallback = await fetch("/i18n/en.json");
      translations = await fallback.json();
    }
  } catch (err) {
    console.error("Failed to load i18n file:", err);
  }
  applyTranslations();
  return translations;
}

export function t(key, fallback = "") {
  return translations[key] || fallback || key;
}

export function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem(LANG_KEY, lang);
  return initI18n(lang);
}

export function getLanguage() {
  return currentLang;
}

export function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(elem => {
    const key = elem.getAttribute("data-i18n");
    if (translations[key]) {
      elem.textContent = translations[key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach(elem => {
    const key = elem.getAttribute("data-i18n-placeholder");
    if (translations[key]) {
      elem.setAttribute("placeholder", translations[key]);
    }
  });
}
