/**
 * Tell Me / Search across all ribbon commands.
 */
export class TellMe {
  constructor({ ribbonConfig, host, onRun }) {
    this.cfg = ribbonConfig;
    this.host = host;
    this.onRun = onRun;
    this._index = this._buildIndex();
    this._render();
    window.addEventListener('ribbon:tellme', (e) => this.search(e.detail));
  }

  _buildIndex() {
    const list = [];
    const push = (tab, group, cmd) => list.push({
      tab: tab.label, group: group.name, cmd,
      text: `${tab.label} ${group.name} ${cmd.label} ${cmd.id}`.toLowerCase(),
    });
    for (const t of this.cfg.tabs || []) {
      for (const g of t.groups || []) {
        for (const c of g.commands || []) push(t, g, c);
      }
    }
    for (const t of this.cfg.contextual || []) {
      for (const g of t.groups || []) {
        for (const c of g.commands || []) push(t, g, c);
      }
    }
    return list;
  }

  _render() {
    this.host.innerHTML = '';
    this.host.classList.add('hidden');
  }

  search(q) {
    q = (q || '').trim().toLowerCase();
    if (!q) return this.host.classList.add('hidden');
    const hits = this._index.filter(h => h.text.includes(q)).slice(0, 8);
    if (!hits.length) return this.host.classList.add('hidden');
    this.host.innerHTML = '';
    this.host.classList.remove('hidden');
    for (const h of hits) {
      const el = document.createElement('div');
      el.className = 'mi';
      el.innerHTML = `<span>${h.cmd.label}</span><small>${h.tab} · ${h.group}</small>`;
      el.onclick = () => {
        this.host.classList.add('hidden');
        this.onRun && this.onRun(h.cmd);
      };
      this.host.appendChild(el);
    }
  }
}