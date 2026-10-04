/**
 * AI Assistant slide-in panel — available in Writer, Sheets, Slides.
 *
 * Usage:
 *   const ai = new AIPanel({ app: 'word', getSelection: () => '...', applyResult: (text) => {...} });
 *   ai.toggle();   // show / hide
 */
export class AIPanel {
  constructor({ app, getSelection, applyResult }) {
    this.app = app;
    this.getSelection = getSelection || (() => '');
    this.applyResult = applyResult || (() => {});
    this.configured = null;
    this._build();
    this._checkStatus();
  }

  toggle() { this.el.classList.toggle('open'); }
  show()   { this.el.classList.add('open'); }
  hide()   { this.el.classList.remove('open'); }

  async _checkStatus() {
    try {
      const r = await fetch('/api/ai/status');
      const j = await r.json();
      this.configured = j.configured && j.enabled;
      const badge = this.el.querySelector('.ai-status');
      if (!j.enabled) {
        badge.textContent = 'AI disabled on server';
        badge.className = 'ai-status ai-status-off';
      } else if (!j.configured) {
        badge.textContent = 'AI not configured';
        badge.className = 'ai-status ai-status-warn';
      } else {
        badge.textContent = 'Ready · ' + j.provider;
        badge.className = 'ai-status ai-status-ok';
      }
    } catch {
      this.configured = false;
    }
  }

  _build() {
    const el = document.createElement('aside');
    el.className = 'ai-panel';
    el.setAttribute('aria-label', 'AI Assistant');
    el.innerHTML = `
      <header class="ai-head">
        <strong>✨ AI Assistant</strong>
        <span class="ai-status">checking…</span>
        <button class="ai-close icon-btn" title="Close">✕</button>
      </header>
      <div class="ai-actions"></div>
      <textarea class="ai-input" rows="4" placeholder="Ask anything, or describe what you want…"></textarea>
      <div class="ai-row">
        <button class="ai-run primary-btn">Ask</button>
        <button class="ai-clear icon-btn" title="Clear">🗑</button>
      </div>
      <div class="ai-output" aria-live="polite"></div>`;
    document.body.appendChild(el);
    this.el = el;

    el.querySelector('.ai-close').onclick = () => this.hide();
    el.querySelector('.ai-clear').onclick = () => {
      el.querySelector('.ai-output').textContent = '';
      el.querySelector('.ai-input').value = '';
    };
    el.querySelector('.ai-run').onclick = () => this._runFromTextarea();

    this._buildActions(el.querySelector('.ai-actions'));
  }

  _buildActions(host) {
    const actions = {
      word: [
        ['summarize', 'Summarize'],
        ['rewrite',   'Rewrite'],
        ['expand',    'Expand'],
        ['fix',       'Fix grammar'],
        ['tone',      'Change tone…'],
        ['translate', 'Translate…'],
        ['outline',   'Create outline'],
        ['continue',  'Continue writing'],
      ],
      sheets: [
        ['formula',   'Formula from English'],
        ['explain',   'Explain this formula'],
        ['insights',  'Insights'],
        ['chart',     'Suggest a chart'],
        ['clean',     'Data cleanup steps'],
      ],
      slides: [
        ['deck',      'Generate a deck'],
        ['rewrite',   'Rewrite bullets'],
        ['notes',     'Speaker notes'],
        ['theme',     'Suggest a theme'],
      ],
    }[this.app] || [];

    for (const [id, label] of actions) {
      const b = document.createElement('button');
      b.className = 'ai-action';
      b.textContent = label;
      b.onclick = () => this._run(id);
      host.appendChild(b);
    }
  }

  _runFromTextarea() {
    const text = this.el.querySelector('.ai-input').value.trim();
    if (!text) return;
    this._call({ action: 'summarize', context: text, options: {} });
  }

  async _run(action) {
    const ctx = this.getSelection() || '';
    const options = {};

    if (action === 'tone') {
      options.tone = prompt('Tone (professional / casual / friendly / formal):', 'professional') || 'professional';
    }
    if (action === 'translate') {
      options.to = prompt('Translate to which language?', 'Spanish') || 'Spanish';
    }

    let payloadContext = ctx;
    if (!payloadContext && (action === 'summarize' || action === 'rewrite' || action === 'expand')) {
      payloadContext = prompt('No text selected. Paste text to send to the AI:') || '';
    }
    if (!payloadContext) {
      this._print('Nothing to send. Select text first.');
      return;
    }

    await this._call({ action, context: payloadContext, options });
  }

  async _call({ action, context, options }) {
    if (!this.configured) {
      await this._checkStatus();
      if (!this.configured) {
        this._print('AI is not configured on this server. Add AI_PROVIDER / AI_API_KEY to .env and restart.');
        return;
      }
    }
    this._print('Thinking…', true);
    try {
      const r = await fetch(`/api/ai/${this.app}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app: this.app, action, context, options }),
      });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error(j.detail || r.statusText);
      }
      const j = await r.json();
      this._print(j.text);
    } catch (e) {
      this._print('Error: ' + e.message);
    }
  }

  _print(text, thinking = false) {
    const out = this.el.querySelector('.ai-output');
    out.textContent = '';
    const wrap = document.createElement('div');
    wrap.className = 'ai-response';
    wrap.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
    out.appendChild(wrap);

    if (!thinking) {
      const applyBtn = document.createElement('button');
      applyBtn.className = 'ai-apply primary-btn';
      applyBtn.textContent = 'Insert into document';
      applyBtn.onclick = () => this.applyResult(text);
      out.appendChild(applyBtn);

      const copyBtn = document.createElement('button');
      copyBtn.className = 'ai-copy icon-btn';
      copyBtn.textContent = '📋';
      copyBtn.title = 'Copy';
      copyBtn.onclick = () => navigator.clipboard.writeText(text);
      out.appendChild(copyBtn);
    }
  }
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}