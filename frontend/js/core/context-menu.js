/**
 * Right-click context menus (built from an array of items).
 */
export function showContextMenu(hostEl, x, y, items) {
  hostEl.innerHTML = '';
  hostEl.classList.remove('hidden');
  hostEl.style.left = `${Math.min(x, innerWidth - 220)}px`;
  hostEl.style.top  = `${Math.min(y, innerHeight - 40 - items.length * 28)}px`;

  for (const it of items) {
    if (it.sep) {
      const s = document.createElement('div'); s.className = 'sep'; hostEl.appendChild(s);
      continue;
    }
    const mi = document.createElement('div'); mi.className = 'mi';
    mi.textContent = it.label;
    if (it.shortcut) {
      const s = document.createElement('span'); s.textContent = it.shortcut;
      s.style.color = 'var(--text-muted)';
      mi.appendChild(s);
    }
    mi.onclick = () => { hideContextMenu(hostEl); it.action && it.action(); };
    hostEl.appendChild(mi);
  }

  const close = (e) => {
    if (!hostEl.contains(e.target)) { hideContextMenu(hostEl); document.removeEventListener('mousedown', close); }
  };
  setTimeout(() => document.addEventListener('mousedown', close), 0);
}

export function hideContextMenu(hostEl) {
  hostEl.classList.add('hidden');
  hostEl.innerHTML = '';
}