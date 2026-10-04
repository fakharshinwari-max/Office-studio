/**
 * Alt key-tips (letter badges on tabs & commands).
 * Press Alt to reveal; ESC hides.
 */
export class KeyTips {
  constructor(rootSelector = '.ribbon') {
    this.root = document.querySelector(rootSelector);
    this.active = false;
    this.badges = [];
    this._bind();
  }

  _bind() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Alt' && !this.active) {
        e.preventDefault();
        this.show();
      } else if (e.key === 'Escape' && this.active) {
        this.hide();
      }
    });
  }

  show() {
    if (!this.root) return;
    this.active = true;
    const els = this.root.querySelectorAll('.ribbon-tab, .rb');
    els.forEach((el, i) => {
      const badge = document.createElement('span');
      badge.className = 'kt-badge';
      const label = (el.textContent || '').trim()[0]?.toUpperCase() || 'A';
      badge.textContent = label + ((i % 9) + 1);
      el.style.position = 'relative';
      el.appendChild(badge);
      this.badges.push(badge);
    });
  }

  hide() {
    this.active = false;
    this.badges.forEach(b => b.remove());
    this.badges = [];
  }
}