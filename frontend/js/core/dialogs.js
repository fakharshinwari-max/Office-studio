/**
 * Reusable modal dialog helpers.
 */
export function openDialog({ title, content, buttons, host }) {
  host.innerHTML = '';
  host.classList.remove('hidden');

  const dlg = document.createElement('div');
  dlg.className = 'dialog';
  dlg.setAttribute('role', 'dialog');
  dlg.setAttribute('aria-modal', 'true');

  const head = document.createElement('div');
  head.className = 'dlg-head';
  head.textContent = title;
  dlg.appendChild(head);

  const body = document.createElement('div');
  body.className = 'dlg-body';
  if (typeof content === 'string') body.innerHTML = content;
  else if (content instanceof HTMLElement) body.appendChild(content);
  dlg.appendChild(body);

  const foot = document.createElement('div');
  foot.className = 'dlg-foot';

  const closeAll = () => { host.classList.add('hidden'); host.innerHTML = ''; };

  for (const b of buttons || [{ label: 'Close' }]) {
    const btn = document.createElement('button');
    btn.textContent = b.label;
    if (b.primary) btn.className = 'primary-btn';
    btn.onclick = () => {
      if (!b.onClick || b.onClick(body, closeAll) !== false) {
        if (b.close !== false) closeAll();
      }
    };
    foot.appendChild(btn);
  }
  dlg.appendChild(foot);

  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAll();
  });

  host.appendChild(dlg);
  return { close: closeAll, body };
}

export function prompt2({ title, fields, host }) {
  return new Promise((resolve) => {
    const wrap = document.createElement('div');
    const inputs = {};
    for (const f of fields) {
      const l = document.createElement('label');
      l.style.display = 'block'; l.style.marginBottom = '8px';
      l.textContent = f.label;
      const inp = document.createElement('input');
      inp.type = f.type || 'text';
      inp.value = f.value ?? '';
      inp.style.cssText = 'display:block;width:100%;margin-top:4px;padding:4px 8px;border:1px solid var(--border);border-radius:4px;background:var(--surface-2);';
      inputs[f.name] = inp;
      l.appendChild(inp);
      wrap.appendChild(l);
    }
    const d = openDialog({
      title, content: wrap, host,
      buttons: [
        { label: 'Cancel', onClick: (_, close) => { close(); resolve(null); } },
        { label: 'OK', primary: true, onClick: (_, close) => {
            const out = {};
            for (const k in inputs) out[k] = inputs[k].value;
            close(); resolve(out);
          }},
      ],
    });
  });
}