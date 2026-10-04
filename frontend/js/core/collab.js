/**
 * Real-time collaboration client — presence + cursor sharing + op relay.
 *
 * Uses the native WebSocket protocol. Yjs can be layered on top in a future
 * commit; for now we relay structured ops between peers and show live cursors.
 */
export class Collab {
  constructor({ docId, onPeers, onOp, onCursor }) {
    this.docId = docId;
    this.onPeers = onPeers || (() => {});
    this.onOp = onOp || (() => {});
    this.onCursor = onCursor || (() => {});
    this.clientId = null;
    this.who = null;
    this.ws = null;
    this.reconnectTimer = null;
    this.shouldClose = false;
  }

  connect() {
    const token = localStorage.getItem('office.access');
    if (!token) return;
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${proto}://${location.host}/api/collab/ws/${this.docId}?token=${encodeURIComponent(token)}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('[collab] connected');
    };

    this.ws.onmessage = (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch { return; }

      if (msg.type === 'welcome') {
        this.clientId = msg.clientId;
        this.who = msg.who;
        this.onPeers(msg.peers || {});
      } else if (msg.type === 'presence') {
        // A peer joined or left; refresh our view
        this.onPeers(this._peers || {});
      } else if (msg.type === 'cursor') {
        this.onCursor(msg.from, msg.cursor);
      } else if (msg.type === 'op') {
        this.onOp(msg);
      } else if (msg.type === 'error') {
        console.warn('[collab] server:', msg.message);
      }
    };

    this.ws.onclose = () => {
      if (this.shouldClose) return;
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };

    this.ws.onerror = () => {
      // Silently retry
    };
  }

  disconnect() {
    this.shouldClose = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    try { this.ws && this.ws.close(); } catch {}
  }

  sendOp(op) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type: 'op', op }));
  }

  sendCursor(cursor) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type: 'cursor', cursor }));
  }
}