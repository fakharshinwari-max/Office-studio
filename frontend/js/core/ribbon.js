/**
 * Data-driven ribbon renderer — Phase 4 final.
 *
 * Config shape:
 * {
 *   tabs: [
 *     { id:'file', label:'File', kind:'file', groups: [] },   // opens Backstage
 *     { id:'home', label:'Home', keyTip:'H', groups: [ ... ] }
 *   ],
 *   contextual: [ { id, label, theme, when, groups } ]
 * }
 *
 * Every command:
 * {
 *   id, label, icon,
 *   type: 'button'|'toggle'|'dropdown'|'split'|'select'|'input'|'colorpicker'|'gallery',
 *   big, tooltip, shortcut, phase,
 *   stateKey, options:[{value,label}], dropdown:[{label,action?,sep?}], items:[...],
 *   action(ctx, value)
 * }
 */
export class Ribbon {
  constructor({ host, config, context = {}, onCommand = null }) {
    if (!host) throw new Error('Ribbon requires a host element');
    if (!config || !config.tabs) throw new Error('Ribbon requires a config with tabs');
    this.host = host;
    this.config = config;
    this.ctx = context || {};
    this.onCommand = onCommand;

    // Never start on the File tab — it opens Backstage (no groups).
    const firstNonFile = config.tabs.find(t => t.kind !== 'file');
    this.activeTabId = firstNonFile ? firstNonFile.id : (config.tabs[0]?.id || 'home');

    this.collapsed = false;
    this._openMenuEl = null;
    this.render();
  }

  setContext(patch) {
    this.ctx = { ...this.ctx, ...patch };
    this.render();
  }

  toggleCollapse() {
    this.collapsed = !this.collapsed;
    this.render();
  }

  selectTab(id) {
    const tab = this._findTab(id);
    if (!tab) return;
    if (tab.kind === 'file') {
      window.dispatchEvent(new CustomEvent('ribbon:backstage'));
      return;
    }
    this.activeTabId = id;
    this.render();
  }

  _findTab(id) {
    const all = [...(this.config.tabs || []), ...(this.config.contextual || [])];
    return all.find(t => t.id === id);
  }

  _visibleTabs() {
    const base = (this.config.tabs || []).slice();
    const contextual = (this.config.contextual || []).filter(t => {
      if (!t.when) return true;
      try { return !!t.when(this.ctx); }
      catch (e) { console.warn('[ribbon] contextual tab .when() threw:', t.id, e); return false; }
    });
    return { base, contextual };
  }

  render() {
    this._closeAnyMenu();
    this.host.innerHTML = '';
    this.host.setAttribute('role', 'toolbar');
    this.host.setAttribute('aria-label', 'Ribbon');

    const { base, contextual } = this._visibleTabs();
    const allTabs = [...base, ...contextual];
    if (!allTabs.find(t => t.id === this.activeTabId)) {
      const firstNonFile = base.find(t => t.kind !== 'file');
      this.activeTabId = firstNonFile ? firstNonFile.id : (base[0]?.id || 'home');
    }

    // ---------- Tab strip ----------
    const tabsBar = el('div', 'ribbon-tabs');
    tabsBar.setAttribute('role', 'tablist');

    for (const t of base) tabsBar.appendChild(this._renderTabButton(t, false));
    for (const t of contextual) tabsBar.appendChild(this._renderTabButton(t, true));

    // ---------- Tell Me ----------
    const tm = el('div', 'tellme-wrap');
    const input = el('input', 'tellme-input');
    input.type = 'search';
    input.placeholder = 'Tell me what you want to do…';
    input.setAttribute('aria-label', 'Tell me what you want to do');
    input.addEventListener('input', (e) => {
      window.dispatchEvent(new CustomEvent('ribbon:tellme', { detail: e.target.value }));
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { input.value = ''; input.blur(); }
    });
    tm.appendChild(input);
    tabsBar.appendChild(tm);

    this.host.appendChild(tabsBar);

    // ---------- Groups body ----------
    if (!this.collapsed) {
      const body = el('div', 'ribbon-groups');
      const activeTab = this._findTab(this.activeTabId);
      if (activeTab && activeTab.groups && activeTab.groups.length) {
        for (const g of activeTab.groups) body.appendChild(this._renderGroup(g));
      } else if (activeTab) {
        const hint = el('div', 'ribbon-empty');
        hint.textContent = 'This tab has no commands.';
        body.appendChild(hint);
      }
      this.host.appendChild(body);
    }
  }

  _renderTabButton(tab, isContextual) {
    const btn = el('button', 'ribbon-tab');
    btn.type = 'button';
    btn.setAttribute('role', 'tab');
    btn.setAttribute('aria-selected', String(tab.id === this.activeTabId));
    if (tab.kind === 'file') btn.classList.add('file-tab');
    if (isContextual) btn.classList.add('ribbon-tab-ctx', `ctx-${tab.theme || 'word'}`);
    if (tab.id === this.activeTabId) btn.classList.add('active');

    const lbl = el('span', 'ribbon-tab-label');
    lbl.textContent = tab.label || tab.id;
    btn.appendChild(lbl);

    if (tab.keyTip) {
      const kt = el('span', 'kt');
      kt.textContent = tab.keyTip;
      btn.appendChild(kt);
    }

    btn.onclick = () => this.selectTab(tab.id);
    btn.ondblclick = () => this.toggleCollapse();
    return btn;
  }

  _renderGroup(group) {
    const wrap = el('div', 'ribbon-group');
    wrap.setAttribute('role', 'group');
    wrap.setAttribute('aria-label', group.name || 'Group');

    const body = el('div', 'ribbon-group-body');
    for (const cmd of group.commands || []) {
      const node = this._renderCommand(cmd);
      if (node) body.appendChild(node);
    }
    wrap.appendChild(body);

    const label = el('div', 'ribbon-group-label');
    const nameSpan = el('span');
    nameSpan.textContent = group.name || '';
    label.appendChild(nameSpan);

    if (group.dialogLauncher) {
      const launcher = el('button', 'launcher');
      launcher.type = 'button';
      launcher.title = `${group.name} dialog`;
      launcher.setAttribute('aria-label', `${group.name} dialog`);
      launcher.textContent = '↘';
      launcher.onclick = () => {
        window.dispatchEvent(new CustomEvent('ribbon:dialog', { detail: { group: group.name } }));
      };
      label.appendChild(launcher);
    }
    wrap.appendChild(label);
    return wrap;
  }

  _isDisabled(cmd) {
    if (cmd.phase && !cmd.implemented) return true;
    if (typeof cmd.enabledWhen === 'function') {
      try { return !cmd.enabledWhen(this.ctx); } catch { return true; }
    }
    return false;
  }

  _renderCommand(cmd) {
    if (!cmd || cmd.hidden) return null;
    const disabled = this._isDisabled(cmd);
    const type = cmd.type || 'button';

    switch (type) {
      case 'toggle':      return this._renderToggle(cmd, disabled);
      case 'dropdown':    return this._renderDropdown(cmd, disabled);
      case 'split':       return this._renderSplit(cmd, disabled);
      case 'select':      return this._renderSelect(cmd, disabled);
      case 'input':       return this._renderInput(cmd, disabled);
      case 'colorpicker': return this._renderColor(cmd, disabled);
      case 'gallery':     return this._renderGallery(cmd, disabled);
      default:            return this._renderButton(cmd, disabled);
    }
  }

  _renderButton(cmd, disabled) {
    const b = el('button', `rb${cmd.big ? ' big' : ''}`);
    b.type = 'button';
    b.dataset.cmd = cmd.id;
    this._applyTooltip(b, cmd);
    if (disabled) {
      b.classList.add('disabled');
      b.disabled = true;
      b.setAttribute('aria-disabled', 'true');
    }
    b.appendChild(this._iconEl(cmd));
    b.appendChild(this._labelEl(cmd));
    if (!disabled) b.onclick = () => this._run(cmd);
    return b;
  }

  _renderToggle(cmd, disabled) {
    const b = el('button', `rb toggle${cmd.big ? ' big' : ''}`);
    b.type = 'button';
    b.dataset.cmd = cmd.id;
    b.setAttribute('aria-pressed', 'false');
    const on = !!this.ctx[cmd.stateKey || cmd.id];
    if (on) { b.classList.add('on'); b.setAttribute('aria-pressed', 'true'); }
    this._applyTooltip(b, cmd);
    if (disabled) { b.classList.add('disabled'); b.disabled = true; }
    b.appendChild(this._iconEl(cmd));
    b.appendChild(this._labelEl(cmd));
    if (!disabled) b.onclick = () => {
      const next = !b.classList.contains('on');
      b.classList.toggle('on', next);
      b.setAttribute('aria-pressed', String(next));
      this.ctx[cmd.stateKey || cmd.id] = next;
      this._run(cmd, next);
    };
    return b;
  }

  _renderDropdown(cmd, disabled) {
    const wrap = el('div', 'rb-dropdown');
    const b = el('button', `rb${cmd.big ? ' big' : ''} has-caret`);
    b.type = 'button';
    b.dataset.cmd = cmd.id;
    b.setAttribute('aria-haspopup', 'menu');
    b.setAttribute('aria-expanded', 'false');
    this._applyTooltip(b, cmd);
    if (disabled) { b.classList.add('disabled'); b.disabled = true; }
    b.appendChild(this._iconEl(cmd));
    b.appendChild(this._labelEl(cmd));
    const caret = el('span', 'caret');
    caret.setAttribute('aria-hidden', 'true');
    caret.textContent = '▾';
    b.appendChild(caret);
    if (!disabled) b.onclick = () => this._openMenu(b, cmd.dropdown || cmd.items || [], cmd);
    wrap.appendChild(b);
    return wrap;
  }

  _renderSplit(cmd, disabled) {
    const wrap = el('div', 'rb-split');
    const main = el('button', `rb${cmd.big ? ' big' : ''}`);
    main.type = 'button';
    main.dataset.cmd = cmd.id;
    this._applyTooltip(main, cmd);
    if (disabled) { main.classList.add('disabled'); main.disabled = true; }
    main.appendChild(this._iconEl(cmd));
    main.appendChild(this._labelEl(cmd));
    if (!disabled) main.onclick = () => this._run(cmd);
    wrap.appendChild(main);

    const caretBtn = el('button', 'rb-split-caret');
    caretBtn.type = 'button';
    caretBtn.setAttribute('aria-haspopup', 'menu');
    caretBtn.setAttribute('aria-label', `${cmd.label} options`);
    caretBtn.textContent = '▾';
    if (disabled) { caretBtn.classList.add('disabled'); caretBtn.disabled = true; }
    else caretBtn.onclick = (e) => { e.stopPropagation(); this._openMenu(caretBtn, cmd.dropdown || [], cmd); };
    wrap.appendChild(caretBtn);
    return wrap;
  }

  _renderSelect(cmd, disabled) {
    const wrap = el('div', 'rb-select-wrap');
    const sel = el('select', 'rb-select');
    sel.dataset.cmd = cmd.id;
    sel.setAttribute('aria-label', cmd.label);
    this._applyTooltip(sel, cmd);
    const current = this.ctx[cmd.stateKey || cmd.id];
    for (const opt of cmd.options || []) {
      const o = document.createElement('option');
      o.value = String(opt.value);
      o.textContent = opt.label ?? String(opt.value);
      if (String(opt.value) === String(current)) o.selected = true;
      sel.appendChild(o);
    }
    if (disabled) { sel.disabled = true; sel.classList.add('disabled'); }
    else sel.onchange = () => this._run(cmd, sel.value);
    wrap.appendChild(sel);
    return wrap;
  }

  _renderInput(cmd, disabled) {
    const inp = el('input', 'rb-input');
    inp.type = cmd.inputType || 'text';
    if (cmd.width) inp.style.width = cmd.width + 'px';
    if (cmd.min != null) inp.min = cmd.min;
    if (cmd.max != null) inp.max = cmd.max;
    if (cmd.placeholder) inp.placeholder = cmd.placeholder;
    inp.dataset.cmd = cmd.id;
    inp.setAttribute('aria-label', cmd.label);
    this._applyTooltip(inp, cmd);
    inp.value = this.ctx[cmd.stateKey || cmd.id] ?? '';
    if (disabled) { inp.disabled = true; inp.classList.add('disabled'); }
    else {
      inp.onchange = () => this._run(cmd, inp.value);
      if (cmd.onInput) inp.oninput = () => this._run(cmd, inp.value);
    }
    return inp;
  }

  _renderColor(cmd, disabled) {
    const inp = el('input', 'rb-color');
    inp.type = 'color';
    inp.dataset.cmd = cmd.id;
    inp.setAttribute('aria-label', cmd.label);
    this._applyTooltip(inp, cmd);
    inp.value = this.ctx[cmd.stateKey || cmd.id] || '#000000';
    if (disabled) { inp.disabled = true; inp.classList.add('disabled'); }
    else inp.oninput = () => this._run(cmd, inp.value);
    return inp;
  }

  _renderGallery(cmd, disabled) {
    return this._renderDropdown({ ...cmd, dropdown: cmd.items || [] }, disabled);
  }

  _iconEl(cmd) {
    const ico = el('span', 'ico');
    ico.setAttribute('aria-hidden', 'true');
    ico.textContent = cmd.icon || '•';
    return ico;
  }
  _labelEl(cmd) {
    const lbl = el('span', 'lbl');
    lbl.textContent = cmd.label || cmd.id;
    return lbl;
  }
  _applyTooltip(node, cmd) {
    const parts = [];
    if (cmd.tooltip) parts.push(cmd.tooltip);
    else parts.push(cmd.label || cmd.id);
    if (cmd.shortcut) parts.push(`(${cmd.shortcut})`);
    if (cmd.phase && !cmd.implemented) parts.push(`— Available in Phase ${cmd.phase}`);
    node.title = parts.join(' ');
  }

  _openMenu(anchor, items, cmd) {
    this._closeAnyMenu();
    if (!items || !items.length) return;
    const menu = el('div', 'rb-menu');
    menu.setAttribute('role', 'menu');
    for (const it of items) {
      if (it.sep) { menu.appendChild(el('div', 'sep')); continue; }
      const mi = el('button', 'mi');
      mi.type = 'button';
      mi.setAttribute('role', 'menuitem');
      const lbl = el('span');
      lbl.textContent = it.label || it.value || '';
      mi.appendChild(lbl);
      if (it.shortcut) {
        const s = el('span', 'mi-shortcut');
        s.textContent = it.shortcut;
        mi.appendChild(s);
      }
      mi.onclick = (e) => {
        e.stopPropagation();
        this._closeAnyMenu();
        if (typeof it.action === 'function') {
          try { it.action(this.ctx); }
          catch (err) { console.error('[menu action]', it.label, err); }
        } else {
          this._run(cmd, it.value);
        }
      };
      menu.appendChild(mi);
    }
    anchor.parentElement.style.position = 'relative';
    anchor.parentElement.appendChild(menu);
    anchor.setAttribute('aria-expanded', 'true');
    this._openMenuEl = { menu, anchor };

    const close = (ev) => {
      if (menu.contains(ev.target) || anchor.contains(ev.target)) return;
      this._closeAnyMenu();
      document.removeEventListener('mousedown', close, true);
    };
    setTimeout(() => document.addEventListener('mousedown', close, true), 0);
  }

  _closeAnyMenu() {
    if (this._openMenuEl) {
      this._openMenuEl.menu.remove();
      this._openMenuEl.anchor.setAttribute('aria-expanded', 'false');
      this._openMenuEl = null;
    }
  }

  _run(cmd, value) {
    const payload = { id: cmd.id, cmd, value, ctx: this.ctx };
    if (typeof cmd.action === 'function') {
      try { cmd.action(this.ctx, value); }
      catch (e) { console.error('[ribbon command]', cmd.id, e); }
    }
    if (typeof this.onCommand === 'function') this.onCommand(payload);
    window.dispatchEvent(new CustomEvent('ribbon:command', { detail: payload }));
  }
}

function el(tag, cls = '') {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  return n;
}