/**
 * IndexedDB-backed autosave journal keyed by document id.
 */
const DB_NAME = 'office-studio';
const STORE = 'journal';

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'id' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export const storage = {
  async put(id, data) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).put({ id, data, savedAt: Date.now() });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },
  async get(id) {
    const db = await openDB();
    return new Promise((resolve) => {
      const tx = db.transaction(STORE, 'readonly');
      const req = tx.objectStore(STORE).get(id);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => resolve(null);
    });
  },
  async remove(id) {
    const db = await openDB();
    return new Promise((resolve) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).delete(id);
      tx.oncomplete = () => resolve();
    });
  },
  async list() {
    const db = await openDB();
    return new Promise((resolve) => {
      const tx = db.transaction(STORE, 'readonly');
      const req = tx.objectStore(STORE).getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => resolve([]);
    });
  },
};

/**
 * Autosave coordinator: debounces writes and reports status via callback.
 */
export class AutoSaver {
  constructor({ getId, getModel, save, delay = 1500 }) {
    this.getId = getId;
    this.getModel = getModel;
    this.save = save;
    this.delay = delay;
    this._timer = null;
    this._statusListeners = new Set();
  }

  onStatus(fn) { this._statusListeners.add(fn); }
  _emit(status) { this._statusListeners.forEach(fn => fn(status)); }

  schedule() {
    this._emit('Saving…');
    if (this._timer) clearTimeout(this._timer);
    this._timer = setTimeout(() => this._flush(), this.delay);
  }

  async _flush() {
    this._timer = null;
    const id = this.getId();
    const model = this.getModel();
    try {
      if (id) { try { await this.save(id, model); } catch { /* offline */ } }
      await storage.put(id || 'local-draft', model);
      this._emit('Saved');
    } catch (e) {
      this._emit('Offline');
    }
  }

  async saveNow() {
    if (this._timer) { clearTimeout(this._timer); this._timer = null; }
    return this._flush();
  }
}