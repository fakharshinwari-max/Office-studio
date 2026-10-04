/**
 * Command-pattern undo/redo history.
 *
 * Commands are `{ do(), undo(), label }`.
 * Push a command AFTER you have already performed the change — `do()` is
 * called only during redo.
 */
export class History {
  constructor(maxDepth = 500) {
    this.undoStack = [];
    this.redoStack = [];
    this.maxDepth = maxDepth;
    this._batch = null;
    this._listeners = new Set();
  }

  onChange(fn) { this._listeners.add(fn); return () => this._listeners.delete(fn); }
  _emit() { this._listeners.forEach(fn => fn({ canUndo: this.canUndo(), canRedo: this.canRedo() })); }

  /** Push an already-applied command. */
  push(cmd) {
    if (this._batch) { this._batch.push(cmd); return; }
    this.undoStack.push(cmd);
    if (this.undoStack.length > this.maxDepth) this.undoStack.shift();
    this.redoStack.length = 0;
    this._emit();
  }

  beginBatch(label = 'Batch') { this._batch = []; this._batchLabel = label; }
  endBatch() {
    if (!this._batch) return;
    const cmds = this._batch; this._batch = null;
    if (!cmds.length) return;
    this.undoStack.push({
      label: this._batchLabel,
      do: () => cmds.forEach(c => c.do()),
      undo: () => [...cmds].reverse().forEach(c => c.undo()),
    });
    this.redoStack.length = 0;
    this._emit();
  }

  canUndo() { return this.undoStack.length > 0; }
  canRedo() { return this.redoStack.length > 0; }

  undo() {
    const cmd = this.undoStack.pop();
    if (!cmd) return false;
    try { cmd.undo(); } catch (e) { console.error('undo failed', e); }
    this.redoStack.push(cmd);
    this._emit();
    return true;
  }

  redo() {
    const cmd = this.redoStack.pop();
    if (!cmd) return false;
    try { cmd.do(); } catch (e) { console.error('redo failed', e); }
    this.undoStack.push(cmd);
    this._emit();
    return true;
  }

  clear() { this.undoStack.length = 0; this.redoStack.length = 0; this._emit(); }
}