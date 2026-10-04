/**
 * Small observable state store.
 */
export class Store {
  constructor(initial = {}) {
    this._state = { ...initial };
    this._subs = new Set();
  }
  get state() { return this._state; }
  get(key) { return this._state[key]; }
  set(patch) {
    this._state = { ...this._state, ...patch };
    this._subs.forEach(fn => fn(this._state));
  }
  subscribe(fn) { this._subs.add(fn); return () => this._subs.delete(fn); }
}

/**
 * Simple pub/sub event bus.
 */
export class Bus {
  constructor() { this._h = new Map(); }
  on(evt, fn) {
    if (!this._h.has(evt)) this._h.set(evt, new Set());
    this._h.get(evt).add(fn);
    return () => this._h.get(evt).delete(fn);
  }
  emit(evt, payload) {
    this._h.get(evt)?.forEach(fn => { try { fn(payload); } catch (e) { console.error(e); } });
    this._h.get('*')?.forEach(fn => fn({ evt, payload }));
  }
}