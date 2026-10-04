/**
 * Recovery banner: if a previous session's autosave journal contains data
 * that never reached the server, show a banner to restore it.
 */
import { storage } from './storage.js';

export async function checkRecovery({ id, currentModel, onRestore }) {
  if (!id) return;
  const j = await storage.get(id);
  if (!j || !j.data) return;

  // If the journal's timestamp is newer than the current model, offer to restore.
  // Simple heuristic: compare JSON size + savedAt.
  const savedAt = j.savedAt || 0;
  const modelAt = currentModel?.updatedAt || 0;
  if (savedAt <= modelAt) return;

  const banner = document.createElement('div');
  banner.className = 'recovery-banner';
  banner.innerHTML = `
    <span>Recovered unsaved changes from your last session.</span>
    <button class="recovery-restore primary-btn">Restore</button>
    <button class="recovery-dismiss icon-btn">✕</button>`;
  document.body.appendChild(banner);

  banner.querySelector('.recovery-restore').onclick = () => {
    onRestore(j.data);
    banner.remove();
  };
  banner.querySelector('.recovery-dismiss').onclick = () => banner.remove();
}