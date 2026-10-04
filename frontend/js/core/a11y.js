/**
 * Accessibility checker for Writer / Sheets / Slides.
 */
export function checkA11y(app) {
  const issues = [];
  const kind = app.constructor.name;

  if (kind === 'WriterApp') {
    app.page.querySelectorAll('img').forEach(img => {
      if (!img.alt) issues.push(`Image missing alt text (src: ${img.src.slice(0, 50)}…)`);
    });
    const headings = [...app.page.querySelectorAll('h1,h2,h3,h4,h5,h6')]
      .map(h => parseInt(h.tagName.slice(1), 10));
    for (let i = 1; i < headings.length; i++) {
      if (headings[i] - headings[i - 1] > 1) {
        issues.push(`Heading level skipped (h${headings[i-1]} → h${headings[i]}).`);
      }
    }
    app.page.querySelectorAll('a').forEach(a => {
      if (!a.textContent.trim()) issues.push(`Link has no accessible text (href: ${a.href.slice(0, 50)}…).`);
    });
  }

  if (kind === 'SheetsApp') {
    const cells = app._getCells();
    for (const ref in cells) {
      const val = cells[ref]?.v;
      if (typeof val === 'string' && val.length > 0 && /^[\s]+$/.test(val)) {
        issues.push(`Cell ${ref} contains only whitespace.`);
      }
    }
  }

  if (kind === 'SlidesApp') {
    app.slides.forEach((slide, i) => {
      for (const o of slide.objects) {
        if (o.type === 'image' && !o.props?.altText) issues.push(`Slide ${i+1}: image missing alt text.`);
        if (o.type === 'text' && (o.props?.fontSize || 24) < 14) issues.push(`Slide ${i+1}: text font too small (${o.props?.fontSize}pt).`);
      }
    });
  }

  return issues;
}

export function showA11yReport(issues, host) {
  const wrap = document.createElement('div');
  if (!issues.length) {
    wrap.innerHTML = '<div style="color:green;font-weight:600;">✓ No accessibility issues found.</div>';
  } else {
    wrap.innerHTML = `
      <div style="font-weight:600;margin-bottom:8px;">${issues.length} issue${issues.length > 1 ? 's' : ''} found</div>
      <ul style="padding-left:20px;font-size:13px;">${issues.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul>`;
  }
  return wrap;
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}