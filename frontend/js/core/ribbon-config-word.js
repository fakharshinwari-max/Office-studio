/**
 * Word ribbon configuration — Home / Insert / References / Mailings / Review / Layout / View.
 */
const P = (n) => `Available in Phase ${n}`;

export const wordRibbon = {
  tabs: [
    { id: 'file', label: 'File', kind: 'file', keyTip: 'F' },

    { id: 'home', label: 'Home', keyTip: 'H', groups: [
      { name: 'Clipboard', dialogLauncher: true, commands: [
        { id: 'paste', label: 'Paste', icon: '📋', type: 'split', big: true, shortcut: 'Ctrl+V',
          action: (ctx) => ctx.cmd('paste'),
          dropdown: [
            { label: 'Keep Source Formatting', action: (ctx) => ctx.cmd('paste') },
            { label: 'Merge Formatting', action: (ctx) => ctx.cmd('pasteMerge') },
            { label: 'Keep Text Only', action: (ctx) => ctx.cmd('pasteText') },
          ] },
        { id: 'cut', label: 'Cut', icon: '✂️', shortcut: 'Ctrl+X', action: (ctx) => ctx.cmd('cut') },
        { id: 'copy', label: 'Copy', icon: '📑', shortcut: 'Ctrl+C', action: (ctx) => ctx.cmd('copy') },
        { id: 'formatPainter', label: 'Format Painter', icon: '🖌️', action: (ctx) => ctx.cmd('formatPainter') },
      ]},
      { name: 'Font', dialogLauncher: true, commands: [
        { id: 'fontName', label: 'Font', type: 'select', stateKey: 'font',
          options: [
            { value: '', label: '(Default)' },
            { value: 'Calibri', label: 'Calibri' },
            { value: 'Arial', label: 'Arial' },
            { value: 'Times New Roman', label: 'Times New Roman' },
            { value: 'Georgia', label: 'Georgia' },
            { value: 'Verdana', label: 'Verdana' },
            { value: 'Courier New', label: 'Courier New' },
          ],
          action: (ctx, v) => ctx.cmd('font', v) },
        { id: 'fontSize', label: 'Size', type: 'select', stateKey: 'fontSize',
          options: ['8','9','10','11','12','14','16','18','24','36','48','72'].map(s => ({ value: s, label: s })),
          action: (ctx, v) => ctx.cmd('fontSize', v) },
        { id: 'growFont', label: 'A⁺', icon: 'A⁺', action: (ctx) => ctx.cmd('growFont') },
        { id: 'shrinkFont', label: 'A⁻', icon: 'A⁻', action: (ctx) => ctx.cmd('shrinkFont') },
        { id: 'bold', label: 'Bold', icon: 'B', type: 'toggle', stateKey: 'bold', shortcut: 'Ctrl+B', action: (ctx, on) => ctx.cmd('bold', on) },
        { id: 'italic', label: 'Italic', icon: 'I', type: 'toggle', stateKey: 'italic', shortcut: 'Ctrl+I', action: (ctx, on) => ctx.cmd('italic', on) },
        { id: 'underline', label: 'Underline', icon: 'U', type: 'toggle', stateKey: 'underline', shortcut: 'Ctrl+U', action: (ctx, on) => ctx.cmd('underline', on) },
        { id: 'strike', label: 'Strike', icon: 'S', type: 'toggle', stateKey: 'strike', action: (ctx, on) => ctx.cmd('strike', on) },
        { id: 'sub', label: 'Subscript', icon: 'ₓ', type: 'toggle', stateKey: 'sub', action: (ctx, on) => ctx.cmd('sub', on) },
        { id: 'sup', label: 'Superscript', icon: 'ˣ', type: 'toggle', stateKey: 'sup', action: (ctx, on) => ctx.cmd('sup', on) },
        { id: 'textColor', label: 'Text Color', icon: 'A', type: 'colorpicker', stateKey: 'color', action: (ctx, v) => ctx.cmd('color', v) },
        { id: 'highlight', label: 'Highlight', icon: '🖍', type: 'colorpicker', stateKey: 'highlight', action: (ctx, v) => ctx.cmd('highlight', v) },
        { id: 'clearFmt', label: 'Clear Formatting', icon: 'A̶', action: (ctx) => ctx.cmd('clearFormatting') },
      ]},
      { name: 'Paragraph', dialogLauncher: true, commands: [
        { id: 'bullets', label: 'Bullets', icon: '•', action: (ctx) => ctx.cmd('bullets') },
        { id: 'numbering', label: 'Numbering', icon: '1.', action: (ctx) => ctx.cmd('numbering') },
        { id: 'outdent', label: 'Decrease Indent', icon: '⇤', action: (ctx) => ctx.cmd('outdent') },
        { id: 'indent', label: 'Increase Indent', icon: '⇥', action: (ctx) => ctx.cmd('indent') },
        { id: 'alignLeft', label: 'Left', icon: '⯇', shortcut: 'Ctrl+L', action: (ctx) => ctx.cmd('align','left') },
        { id: 'alignCenter', label: 'Center', icon: '☰', shortcut: 'Ctrl+E', action: (ctx) => ctx.cmd('align','center') },
        { id: 'alignRight', label: 'Right', icon: '⯈', shortcut: 'Ctrl+R', action: (ctx) => ctx.cmd('align','right') },
        { id: 'alignJustify', label: 'Justify', icon: '☷', shortcut: 'Ctrl+J', action: (ctx) => ctx.cmd('align','justify') },
        { id: 'lineSpacing', label: 'Line Spacing', icon: '≡', type: 'dropdown', dropdown: [
          { label: '1.0',  action: (ctx) => ctx.cmd('lineSpacing','1') },
          { label: '1.15', action: (ctx) => ctx.cmd('lineSpacing','1.15') },
          { label: '1.5',  action: (ctx) => ctx.cmd('lineSpacing','1.5') },
          { label: '2.0',  action: (ctx) => ctx.cmd('lineSpacing','2') },
        ] },
      ]},
      { name: 'Styles', dialogLauncher: true, commands: [
        { id: 'styleNormal', label: 'Normal', icon: 'N', action: (ctx) => ctx.cmd('style','p') },
        { id: 'styleH1', label: 'Heading 1', icon: 'H1', action: (ctx) => ctx.cmd('style','h1') },
        { id: 'styleH2', label: 'Heading 2', icon: 'H2', action: (ctx) => ctx.cmd('style','h2') },
        { id: 'styleH3', label: 'Heading 3', icon: 'H3', action: (ctx) => ctx.cmd('style','h3') },
        { id: 'styleQuote', label: 'Quote', icon: '❝', action: (ctx) => ctx.cmd('style','blockquote') },
        { id: 'styleCode', label: 'Code', icon: '</>', action: (ctx) => ctx.cmd('style','code') },
      ]},
      { name: 'Editing', dialogLauncher: true, commands: [
        { id: 'find', label: 'Find', icon: '🔍', shortcut: 'Ctrl+F', action: (ctx) => ctx.cmd('find') },
        { id: 'replace', label: 'Replace', icon: '⇄', shortcut: 'Ctrl+H', action: (ctx) => ctx.cmd('replace') },
        { id: 'selectAll', label: 'Select All', icon: '⬚', shortcut: 'Ctrl+A', action: (ctx) => ctx.cmd('selectAll') },
      ]},
    ]},

    { id: 'insert', label: 'Insert', keyTip: 'N', groups: [
      { name: 'Pages', commands: [
        { id: 'coverPage', label: 'Cover Page', icon: '📄', action: (ctx) => ctx.cmd('insertCover') },
        { id: 'blankPage', label: 'Blank Page', icon: '📄', action: (ctx) => ctx.cmd('insertBlankPage') },
        { id: 'pageBreak', label: 'Page Break', icon: '⏎', shortcut: 'Ctrl+Enter', action: (ctx) => ctx.cmd('insertPageBreak') },
      ]},
      { name: 'Tables', commands: [
        { id: 'table', label: 'Table', icon: '▦', type: 'dropdown', dropdown: [
          { label: 'Insert 2 × 2', action: (ctx) => ctx.cmd('insertTable', [2,2]) },
          { label: 'Insert 3 × 3', action: (ctx) => ctx.cmd('insertTable', [3,3]) },
          { label: 'Insert 4 × 4', action: (ctx) => ctx.cmd('insertTable', [4,4]) },
          { label: 'Insert 5 × 5', action: (ctx) => ctx.cmd('insertTable', [5,5]) },
        ] },
      ]},
      { name: 'Illustrations', commands: [
        { id: 'picture', label: 'Pictures', icon: '🖼️', action: (ctx) => ctx.cmd('insertImage') },
        { id: 'equation', label: 'Equation', icon: '∑', action: (ctx) => ctx.cmd('insertEquation') },
      ]},
      { name: 'Links', commands: [
        { id: 'link', label: 'Link', icon: '🔗', shortcut: 'Ctrl+K', action: (ctx) => ctx.cmd('insertLink') },
      ]},
      { name: 'Comments', commands: [
        { id: 'newComment', label: 'Comment', icon: '💬', action: (ctx) => ctx.cmd('newComment') },
        { id: 'insertFootnote', label: 'Footnote', icon: '¹', action: (ctx) => ctx.cmd('insertFootnote') },
      ]},
      { name: 'Text', commands: [
        { id: 'fieldDialog', label: 'Field', icon: 'f', action: (ctx) => ctx.cmd('insertFieldDialog') },
        { id: 'dateTime', label: 'Date & Time', icon: '📅', action: (ctx) => ctx.cmd('insertDateTime') },
        { id: 'symbol', label: 'Symbol', icon: 'Ω', action: (ctx) => ctx.cmd('insertSymbol') },
      ]},
    ]},

    { id: 'references', label: 'References', keyTip: 'S', groups: [
      { name: 'Table of Contents', commands: [
        { id: 'insertTOC', label: 'Table of Contents', icon: '📑', action: (ctx) => ctx.cmd('insertTOC') },
        { id: 'updateTOC', label: 'Update Table', icon: '↻', action: (ctx) => ctx.cmd('updateTOC') },
      ]},
      { name: 'Captions', commands: [
        { id: 'insertCaption', label: 'Insert Caption', icon: '🏷', action: (ctx) => ctx.cmd('insertCaption') },
      ]},
    ]},

    { id: 'mailings', label: 'Mailings', keyTip: 'M', groups: [
      { name: 'Start Mail Merge', commands: [
        { id: 'mailMergeStart', label: 'Start Mail Merge', icon: '✉', action: (ctx) => ctx.cmd('mailMergeStart') },
      ]},
    ]},

    { id: 'review', label: 'Review', keyTip: 'R', groups: [
      { name: 'Comments', commands: [
        { id: 'newComment2', label: 'New Comment', icon: '💬', action: (ctx) => ctx.cmd('newComment') },
      ]},
      { name: 'Tracking', commands: [
        { id: 'trackChanges', label: 'Track Changes', icon: '📝', type: 'toggle', stateKey: 'tracking', action: (ctx, on) => ctx.cmd('trackChanges', on) },
        { id: 'displayReview', label: 'Display for Review', icon: '👁', type: 'dropdown', dropdown: [
          { label: 'All Markup',    action: (ctx) => ctx.cmd('displayReview','all') },
          { label: 'Simple Markup', action: (ctx) => ctx.cmd('displayReview','simple') },
          { label: 'No Markup',     action: (ctx) => ctx.cmd('displayReview','none') },
          { label: 'Original',      action: (ctx) => ctx.cmd('displayReview','original') },
        ] },
      ]},
      { name: 'Changes', commands: [
        { id: 'acceptAll', label: 'Accept All', icon: '✓', action: (ctx) => ctx.cmd('acceptAll') },
        { id: 'rejectAll', label: 'Reject All', icon: '✗', action: (ctx) => ctx.cmd('rejectAll') },
      ]},
    ]},

    { id: 'layout', label: 'Layout', keyTip: 'P', groups: [
      { name: 'Page Setup', dialogLauncher: true, commands: [
        { id: 'margins', label: 'Margins', icon: '⬜', type: 'dropdown', dropdown: [
          { label: 'Normal (1")',  action: (ctx) => ctx.cmd('setMargins', 96) },
          { label: 'Narrow (0.5")', action: (ctx) => ctx.cmd('setMargins', 48) },
          { label: 'Wide (1.5")',   action: (ctx) => ctx.cmd('setMargins', 144) },
        ] },
        { id: 'orientation', label: 'Orientation', icon: '⟳', type: 'dropdown', dropdown: [
          { label: 'Portrait',  action: (ctx) => ctx.cmd('setOrientation','portrait') },
          { label: 'Landscape', action: (ctx) => ctx.cmd('setOrientation','landscape') },
        ] },
        { id: 'size', label: 'Size', icon: '📄', type: 'dropdown', dropdown: [
          { label: 'Letter', action: (ctx) => ctx.cmd('setPageSize','Letter') },
          { label: 'A4',     action: (ctx) => ctx.cmd('setPageSize','A4') },
        ] },
      ]},
      { name: 'Page Background', commands: [
        { id: 'watermark', label: 'Watermark', icon: '💧', action: (ctx) => ctx.cmd('watermarkDialog') },
      ]},
    ]},

    { id: 'view', label: 'View', keyTip: 'W', groups: [
      { name: 'Views', commands: [
        { id: 'focusMode', label: 'Focus', icon: '🎯', action: (ctx) => ctx.cmd('focusMode') },
      ]},
      { name: 'Zoom', commands: [
        { id: 'zoom', label: 'Zoom', icon: '🔍', action: (ctx) => ctx.cmd('zoomDialog') },
        { id: 'zoom100', label: '100%', icon: '100', action: (ctx) => ctx.cmd('setZoom', 100) },
      ]},
      { name: 'Fields', commands: [
        { id: 'updateFields', label: 'Update Fields', icon: '↻', shortcut: 'F9', action: (ctx) => ctx.cmd('updateFields') },
      ]},
    ]},
  ],
  contextual: [
    {
      id: 'table-design', label: 'Table Design', theme: 'word',
      when: (ctx) => !!ctx.hasTable,
      groups: [
        { name: 'Table Style Options', commands: [
          { id: 'headerRow', label: 'Header Row', icon: 'H', type: 'toggle', stateKey: 'tblHeader', action: () => {} },
        ]},
      ],
    },
  ],
};