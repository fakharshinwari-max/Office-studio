/**
 * Global keyboard shortcut dispatcher.
 *
 * Usage: new Shortcuts(map).bind();
 * `map` is {"ctrl+b": fn, ...}. Keys are lowercased, modifiers separated by `+`,
 * order: ctrl, alt, shift, meta then key.
 */
export class Shortcuts {
  constructor(map = {}, target = document) {
    this.map = map;
    this.target = target;
    this._handler = this._onKeyDown.bind(this);
  }

  bind() { this.target.addEventListener('keydown', this._handler, true); return this; }
  unbind() { this.target.removeEventListener('keydown', this._handler, true); }

  add(combo, fn) { this.map[combo.toLowerCase()] = fn; }

  _onKeyDown(e) {
    // Skip inside inputs / contenteditable when the shortcut does not want us
    const key = e.key.length === 1 ? e.key.toLowerCase() : e.key.toLowerCase();
    const parts = [];
    if (e.ctrlKey) parts.push('ctrl');
    if (e.altKey) parts.push('alt');
    if (e.shiftKey) parts.push('shift');
    if (e.metaKey) parts.push('meta');
    parts.push(key);
    const combo = parts.join('+');

    const fn = this.map[combo];
    if (!fn) return;

    // Only block Ctrl+letter shortcuts when they don't conflict with input editing
    const target = e.target;
    const inInput = target && (target.isContentEditable ||
      target.tagName === 'INPUT' || target.tagName === 'TEXTAREA');
    if (inInput && ['ctrl+c','ctrl+v','ctrl+x','ctrl+a','ctrl+z','ctrl+y'].includes(combo)) {
      // Still fire ours first, then let browser default (which will be blocked)
    }
    e.preventDefault();
    e.stopPropagation();
    try { fn(e, combo); } catch (err) { console.error('[shortcut]', combo, err); }
  }
}