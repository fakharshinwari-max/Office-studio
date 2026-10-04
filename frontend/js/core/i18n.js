/**
 * Minimal i18n — loads JSON catalogs, applies to elements with data-i18n,
 * handles RTL for ar/ur/fa/he.
 */
const RTL_LANGS = ['ar', 'ur', 'fa', 'he'];
const SUPPORTED = ['en', 'ur', 'ar', 'ps', 'fr', 'es', 'hi', 'pt', 'zh', 'ru'];

let _catalog = {};
let _lang = 'en';

export async function initI18n() {
  const saved = localStorage.getItem('office.lang') || navigator.language.split('-')[0] || 'en';
  _lang = SUPPORTED.includes(saved) ? saved : 'en';
  document.documentElement.lang = _lang;
  document.documentElement.dir = RTL_LANGS.includes(_lang) ? 'rtl' : 'ltr';

  try {
    const r = await fetch(`/i18n/${_lang}.json`);
    _catalog = r.ok ? await r.json() : {};
  } catch { _catalog = {}; }

  applyTranslations();
}

export function t(key, fallback) {
  return _catalog[key] || fallback || key;
}

export function applyTranslations(root = document) {
  root.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key, el.textContent);
  });
  root.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.getAttribute('data-i18n-title');
    el.title = t(key, el.title);
  });
}

export function setLanguage(lang) {
  if (!SUPPORTED.includes(lang)) return;
  localStorage.setItem('office.lang', lang);
  location.reload();
}

export function currentLanguage() { return _lang; }
export function isRTL() { return RTL_LANGS.includes(_lang); }
export function supported() { return [...SUPPORTED]; }
