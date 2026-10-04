/**
 * API client. Handles auth tokens, refresh, and provides typed helpers.
 */
const TOKEN_KEY = 'office.access';
const REFRESH_KEY = 'office.refresh';
const API_BASE = '';  // same-origin by default

class Api {
  get accessToken() { return localStorage.getItem(TOKEN_KEY); }
  get refreshToken() { return localStorage.getItem(REFRESH_KEY); }

  setTokens(access, refresh) {
    if (access) localStorage.setItem(TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  }
  clearTokens() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  async _fetch(path, opts = {}) {
    const headers = new Headers(opts.headers || {});
    if (this.accessToken) headers.set('Authorization', `Bearer ${this.accessToken}`);
    if (opts.body && !(opts.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    const res = await fetch(API_BASE + path, { ...opts, headers });

    if (res.status === 401 && this.refreshToken) {
      const refreshed = await this._tryRefresh();
      if (refreshed) {
        headers.set('Authorization', `Bearer ${this.accessToken}`);
        return fetch(API_BASE + path, { ...opts, headers });
      }
    }
    if (!res.ok) {
      let detail = res.statusText;
      try { detail = (await res.json()).detail || detail; } catch {}
      const err = new Error(detail); err.status = res.status; throw err;
    }
    return res;
  }

  async _tryRefresh() {
    try {
      const res = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });
      if (!res.ok) return false;
      const j = await res.json();
      this.setTokens(j.access_token, j.refresh_token);
      return true;
    } catch { return false; }
  }

  async login(email, password) {
    const body = new URLSearchParams({ username: email, password });
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    });
    if (!res.ok) throw new Error('Login failed');
    const j = await res.json();
    this.setTokens(j.access_token, j.refresh_token);
    return j;
  }

  async register(email, password, name = '') {
    const res = await this._fetch('/api/auth/register', {
      method: 'POST', body: JSON.stringify({ email, password, name }),
    });
    const j = await res.json();
    this.setTokens(j.access_token, j.refresh_token);
    return j;
  }

  async listDocs(kind) {
    const q = kind ? `?kind=${encodeURIComponent(kind)}` : '';
    const res = await this._fetch('/api/docs' + q);
    return res.json();
  }
  async getDoc(id)   { const r = await this._fetch(`/api/docs/${id}`); return r.json(); }
  async createDoc(kind, name, data = {}) {
    const r = await this._fetch('/api/docs', { method: 'POST', body: JSON.stringify({ kind, name, data }) });
    return r.json();
  }
  async updateDoc(id, name, data) {
    const r = await this._fetch(`/api/docs/${id}`, { method: 'PUT', body: JSON.stringify({ kind: 'any', name, data }) });
    return r.json();
  }
  async deleteDoc(id) { await this._fetch(`/api/docs/${id}`, { method: 'DELETE' }); }

  async exportDoc(kind, fmt, model, name) {
    const res = await this._fetch(`/api/export/${kind}/${fmt}`, {
      method: 'POST', body: JSON.stringify({ model, name }),
    });
    return res.blob();
  }

  async importFile(kind, file) {
    const fd = new FormData(); fd.append('file', file);
    const res = await this._fetch(`/api/import/${kind}`, { method: 'POST', body: fd });
    return res.json();
  }

  async downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }
}

export const api = new Api();