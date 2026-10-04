/**
 * Full-screen Backstage view (File tab).
 */
export class Backstage {
  constructor({ host, title, onNew, onOpenFile, onSave, onExport, onPrint }) {
    this.host = host;
    this.title = title;
    this.onNew = onNew;
    this.onOpenFile = onOpenFile;
    this.onSave = onSave;
    this.onExport = onExport;
    this.onPrint = onPrint;
    this.current = 'home';
    this._render();
  }

  open(section = 'home') {
    this.current = section;
    this.host.classList.remove('hidden');
    this._renderPanel();
  }
  close() { this.host.classList.add('hidden'); }

  _render() {
    this.host.innerHTML = '';

    const nav = document.createElement('nav');
    nav.className = 'bs-nav';

    const sections = [
      ['home', '🏠 Home'],
      ['new', '📄 New'],
      ['open', '📂 Open'],
      ['info', 'ℹ️ Info'],
      ['save', '💾 Save'],
      ['saveas', '💾 Save As'],
      ['print', '🖨️ Print'],
      ['export', '⬇ Export'],
      ['close', '⬅ Back'],
    ];
    for (const [id, label] of sections) {
      const b = document.createElement('button');
      b.className = 'bs-nav-item' + (id === this.current ? ' active' : '');
      b.textContent = label;
      b.onclick = () => {
        if (id === 'close') return this.close();
        if (id === 'save' && this.onSave) { this.onSave(); return this.close(); }
        this.current = id;
        this._renderPanel();
        nav.querySelectorAll('.bs-nav-item').forEach((n, i) => n.classList.toggle('active', sections[i][0] === id));
      };
      nav.appendChild(b);
    }
    this.host.appendChild(nav);

    this.panel = document.createElement('div');
    this.panel.className = 'bs-panel';
    this.host.appendChild(this.panel);
    this._renderPanel();
  }

  _renderPanel() {
    const p = this.panel;
    p.innerHTML = '';
    const h = document.createElement('h2');
    h.textContent = ({ home: 'Home', new: 'New', open: 'Open', info: 'Info',
                       saveas: 'Save As', print: 'Print', export: 'Export' }[this.current] || '');
    p.appendChild(h);

    if (this.current === 'home' || this.current === 'new') {
      const row = document.createElement('div');
      row.style.display = 'flex'; row.style.gap = '16px'; row.style.marginTop = '20px'; row.style.flexWrap = 'wrap';
      const mk = (title, sub, icon, fn) => {
        const card = document.createElement('button');
        card.style.cssText = 'min-width:180px; padding:18px; background:var(--surface-2); border:1px solid var(--border); border-radius:8px; text-align:left; cursor:pointer;';
        card.innerHTML = `<div style="font-size:28px">${icon}</div><strong>${title}</strong><div style="font-size:12px;color:var(--text-muted)">${sub}</div>`;
        card.onclick = () => { this.close(); fn && fn(); };
        return card;
      };
      row.appendChild(mk('Blank document', 'Start fresh', '📄', this.onNew));
      row.appendChild(mk('Open from device', 'DOCX, XLSX, PPTX', '📂', () => this.onOpenFile && this.onOpenFile()));
      p.appendChild(row);
    }

    if (this.current === 'info') {
      p.innerHTML += `<div style="margin-top:20px">
        <p><strong>Title:</strong> ${this.title()}</p>
        <p><strong>Author:</strong> (you)</p>
        <p><strong>Last modified:</strong> just now</p>
        <p><strong>Location:</strong> Office Studio local</p>
      </div>`;
    }

    if (this.current === 'export' || this.current === 'print') {
      const row = document.createElement('div'); row.style.display = 'flex'; row.style.gap = '12px'; row.style.flexWrap = 'wrap'; row.style.marginTop = '20px';
      const btn = (label, fmt) => {
        const b = document.createElement('button'); b.className = 'primary-btn';
        b.textContent = label;
        b.onclick = () => { this.onExport && this.onExport(fmt); this.close(); };
        return b;
      };
      row.appendChild(btn('PDF', 'pdf'));
      row.appendChild(btn('HTML', 'html'));
      p.appendChild(row);
    }
  }
}