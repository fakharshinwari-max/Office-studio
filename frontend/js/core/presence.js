/**
 * Renders presence avatars and remote cursors into the DOM.
 */
export class Presence {
  constructor(hostEl) {
    this.host = hostEl || document.body;
    this.el = document.createElement('div');
    this.el.className = 'presence-bar';
    (document.querySelector('.title-right') || this.host).appendChild(this.el);
    this.peers = {};
  }

  update(peers) {
    this.peers = peers || {};
    this.el.innerHTML = '';
    for (const [cid, who] of Object.entries(this.peers)) {
      const dot = document.createElement('span');
      dot.className = 'presence-dot';
      dot.style.background = who.color || '#888';
      dot.textContent = (who.name || '?').trim().charAt(0).toUpperCase();
      dot.title = who.name || 'Anonymous';
      this.el.appendChild(dot);
    }
  }

  showCursor(clientId, cursor, who) {
    if (!cursor) return;
    const id = 'cursor-' + clientId;
    let el = document.getElementById(id);
    if (!el) {
      el = document.createElement('div');
      el.id = id;
      el.className = 'remote-cursor';
      el.style.background = (who && who.color) || '#888';
      document.body.appendChild(el);
    }
    el.style.left = cursor.x + 'px';
    el.style.top = cursor.y + 'px';
    clearTimeout(el._hide);
    el._hide = setTimeout(() => el.remove(), 4000);
  }
}