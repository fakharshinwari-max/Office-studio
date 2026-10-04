/** Excel ribbon configuration — Phase 4 complete. */
const P = (n) => `Available in Phase ${n}`;

export const excelRibbon = {
  tabs: [
    { id: 'file', label: 'File', kind: 'file', keyTip: 'F' },

    { id: 'home', label: 'Home', keyTip: 'H', groups: [
      { name: 'Clipboard', dialogLauncher: true, commands: [
        { id: 'paste', label: 'Paste', icon: '📋', type: 'split', big: true, shortcut: 'Ctrl+V',
          action: (ctx) => ctx.cmd('paste'),
          dropdown: [
            { label: 'Paste', action: (ctx) => ctx.cmd('paste') },
            { label: 'Paste Special…', action: (ctx) => ctx.cmd('pasteSpecial') },
          ] },
        { id: 'cut', label: 'Cut', icon: '✂️', shortcut: 'Ctrl+X', action: (ctx) => ctx.cmd('cut') },
        { id: 'copy', label: 'Copy', icon: '📑', shortcut: 'Ctrl+C', action: (ctx) => ctx.cmd('copy') },
        { id: 'formatPainter', label: 'Format Painter', icon: '🖌️', action: (ctx) => ctx.cmd('formatPainter') },
      ]},
      { name: 'Font', dialogLauncher: true, commands: [
        { id: 'fontName', label: 'Font', type: 'select', stateKey: 'font',
          options: [
            { value: 'Calibri', label: 'Calibri' },
            { value: 'Arial', label: 'Arial' },
            { value: 'Times New Roman', label: 'Times New Roman' },
            { value: 'Courier New', label: 'Courier New' },
          ],
          action: (ctx, v) => ctx.cmd('font', v) },
        { id: 'fontSize', label: 'Size', type: 'select', stateKey: 'fontSize',
          options: ['10','11','12','14','16','18'].map(s => ({ value: s, label: s })),
          action: (ctx, v) => ctx.cmd('fontSize', v) },
        { id: 'bold', label: 'Bold', icon: 'B', type: 'toggle', stateKey: 'bold', shortcut: 'Ctrl+B', action: (ctx, on) => ctx.cmd('bold', on) },
        { id: 'italic', label: 'Italic', icon: 'I', type: 'toggle', stateKey: 'italic', shortcut: 'Ctrl+I', action: (ctx, on) => ctx.cmd('italic', on) },
        { id: 'underline', label: 'Underline', icon: 'U', type: 'toggle', stateKey: 'underline', shortcut: 'Ctrl+U', action: (ctx, on) => ctx.cmd('underline', on) },
        { id: 'fill', label: 'Fill', type: 'colorpicker', stateKey: 'fill', action: (ctx, v) => ctx.cmd('fill', v) },
        { id: 'fontColor', label: 'Font Color', type: 'colorpicker', stateKey: 'color', action: (ctx, v) => ctx.cmd('color', v) },
      ]},
      { name: 'Alignment', commands: [
        { id: 'alignLeft', label: 'Left', icon: '⌫', action: (ctx) => ctx.cmd('align','left') },
        { id: 'alignCenter', label: 'Center', icon: '↔', action: (ctx) => ctx.cmd('align','center') },
        { id: 'alignRight', label: 'Right', icon: '⌦', action: (ctx) => ctx.cmd('align','right') },
        { id: 'wrapText', label: 'Wrap Text', icon: '↵', type: 'toggle', stateKey: 'wrap', action: (ctx, on) => ctx.cmd('wrap', on) },
      ]},
      { name: 'Number', commands: [
        { id: 'format', label: 'Number Format', type: 'select', stateKey: 'numfmt', options: [
          { value: 'General', label: 'General' },
          { value: '0', label: 'Number' },
          { value: '$#,##0.00', label: 'Currency' },
          { value: '0%', label: 'Percentage' },
          { value: 'mm/dd/yyyy', label: 'Short Date' },
          { value: 'h:mm:ss', label: 'Time' },
          { value: '0.00E+00', label: 'Scientific' },
        ], action: (ctx, v) => ctx.cmd('numfmt', v) },
        { id: 'pct', label: 'Percent', icon: '%', action: (ctx) => ctx.cmd('numfmt','0%') },
        { id: 'comma', label: 'Comma', icon: ',', action: (ctx) => ctx.cmd('numfmt','#,##0.00') },
      ]},
      { name: 'Styles', commands: [
        { id: 'condfmt', label: 'Conditional Formatting', icon: '🎨', action: (ctx) => ctx.cmd('condfmt') },
        { id: 'goodStyle', label: 'Good', icon: '✓', action: (ctx) => ctx.cmd('style','good') },
        { id: 'badStyle', label: 'Bad', icon: '✗', action: (ctx) => ctx.cmd('style','bad') },
        { id: 'neutralStyle', label: 'Neutral', icon: '=', action: (ctx) => ctx.cmd('style','neutral') },
      ]},
      { name: 'Cells', commands: [
        { id: 'formatCells', label: 'Format', icon: '🎛', action: (ctx) => ctx.cmd('format') },
        { id: 'insertLink', label: 'Link', icon: '🔗', shortcut: 'Ctrl+K', action: (ctx) => ctx.cmd('insertLink') },
      ]},
      { name: 'Editing', commands: [
        { id: 'autoSum', label: 'AutoSum', icon: 'Σ', type: 'dropdown', dropdown: [
          { label: 'Sum', action: (ctx) => ctx.cmd('autosum','SUM') },
          { label: 'Average', action: (ctx) => ctx.cmd('autosum','AVERAGE') },
          { label: 'Count Numbers', action: (ctx) => ctx.cmd('autosum','COUNT') },
          { label: 'Max', action: (ctx) => ctx.cmd('autosum','MAX') },
          { label: 'Min', action: (ctx) => ctx.cmd('autosum','MIN') },
        ] },
        { id: 'fill', label: 'Fill Down', icon: '↧', action: (ctx) => ctx.cmd('fillDown') },
        { id: 'clear', label: 'Clear', icon: '🧹', action: (ctx) => ctx.cmd('clearContents') },
        { id: 'sortFilter', label: 'Sort & Filter', icon: '⇅', type: 'dropdown', dropdown: [
          { label: 'Sort A → Z', action: (ctx) => ctx.cmd('sort','asc') },
          { label: 'Sort Z → A', action: (ctx) => ctx.cmd('sort','desc') },
          { label: 'Filter', action: (ctx) => ctx.cmd('filter') },
        ] },
        { id: 'findSelect', label: 'Find & Select', icon: '🔍', shortcut: 'Ctrl+F', action: (ctx) => ctx.cmd('find') },
      ]},
    ]},

    { id: 'insert', label: 'Insert', keyTip: 'N', groups: [
      { name: 'Tables', commands: [
        { id: 'pivot', label: 'PivotTable', icon: '⊞', action: (ctx) => ctx.cmd('pivot') },
      ]},
      { name: 'Charts', commands: [
        { id: 'colChart', label: 'Column', icon: '📊', action: (ctx) => ctx.cmd('insertChart','column') },
        { id: 'lineChart', label: 'Line', icon: '📈', action: (ctx) => ctx.cmd('insertChart','line') },
        { id: 'pieChart', label: 'Pie', icon: '🥧', action: (ctx) => ctx.cmd('insertChart','pie') },
        { id: 'scatterChart', label: 'Scatter', icon: '⋆', action: (ctx) => ctx.cmd('insertChart','scatter') },
      ]},
      { name: 'Sparklines', commands: [
        { id: 'sparkLine', label: 'Line', icon: '↗', action: (ctx) => ctx.cmd('sparkline') },
        { id: 'sparkColumn', label: 'Column', icon: '▮', action: (ctx) => ctx.cmd('sparkline') },
        { id: 'sparkWinLoss', label: 'Win/Loss', icon: '▥', action: (ctx) => ctx.cmd('sparkline') },
      ]},
    ]},

    { id: 'formulas', label: 'Formulas', keyTip: 'M', groups: [
      { name: 'Function Library', commands: [
        { id: 'insertFunc', label: 'Insert Function', icon: 'fx', action: (ctx) => ctx.cmd('insertFunction') },
        { id: 'autoSum2', label: 'AutoSum', icon: 'Σ', action: (ctx) => ctx.cmd('autosum','SUM') },
      ]},
      { name: 'Defined Names', commands: [
        { id: 'nameManager', label: 'Name Manager', icon: '📓', action: (ctx) => ctx.cmd('nameManager') },
        { id: 'defineName',  label: 'Define Name', icon: '🏷', action: (ctx) => ctx.cmd('defineName') },
      ]},
      { name: 'Formula Auditing', commands: [
        { id: 'tracePrecedents', label: 'Trace Precedents', icon: '←', action: (ctx) => ctx.cmd('tracePrecedents') },
        { id: 'traceDependents', label: 'Trace Dependents', icon: '→', action: (ctx) => ctx.cmd('traceDependents') },
        { id: 'showFormulas', label: 'Show Formulas', icon: '≡', type: 'toggle', stateKey: 'showFormulas', action: (ctx, on) => ctx.cmd('showFormulas', on) },
        { id: 'evaluateFormula', label: 'Evaluate Formula', icon: '🧮', action: (ctx) => ctx.cmd('evaluateFormula') },
      ]},
      { name: 'Calculation', commands: [
        { id: 'calcNow', label: 'Calculate Now', icon: '⟳', shortcut: 'F9', action: (ctx) => ctx.cmd('recalcAll') },
      ]},
    ]},

    { id: 'data', label: 'Data', keyTip: 'A', groups: [
      { name: 'Get & Transform', commands: [
        { id: 'powerQuery', label: 'Get & Transform', icon: '⬇', action: (ctx) => ctx.cmd('powerQuery') },
      ]},
      { name: 'Sort & Filter', commands: [
        { id: 'sortAsc', label: 'Sort A→Z', icon: '↑', action: (ctx) => ctx.cmd('sort','asc') },
        { id: 'sortDesc', label: 'Sort Z→A', icon: '↓', action: (ctx) => ctx.cmd('sort','desc') },
        { id: 'filter', label: 'Filter', icon: '▽', type: 'toggle', stateKey: 'filterOn', action: (ctx, on) => ctx.cmd('filter', on) },
      ]},
      { name: 'Data Tools', commands: [
        { id: 'textToCols', label: 'Text to Columns', icon: '⇥', action: (ctx) => ctx.cmd('textToCols') },
        { id: 'removeDupes', label: 'Remove Duplicates', icon: '⚏', action: (ctx) => ctx.cmd('removeDuplicates') },
        { id: 'dataValidation', label: 'Data Validation', icon: '✓', action: (ctx) => ctx.cmd('dataValidation') },
      ]},
      { name: 'Forecast', commands: [
        { id: 'goalSeek', label: 'Goal Seek', icon: '🎯', action: (ctx) => ctx.cmd('goalSeek') },
        { id: 'scenarioMgr', label: 'Scenario Manager', icon: '📋', action: (ctx) => ctx.cmd('scenarioManager') },
        { id: 'dataTable', label: 'Data Table', icon: '▦', action: (ctx) => ctx.cmd('dataTable') },
        { id: 'forecastSheet', label: 'Forecast Sheet', icon: '📈', action: (ctx) => ctx.cmd('forecastSheet') },
      ]},
      { name: 'Analysis', commands: [
        { id: 'analysisToolpak', label: 'Data Analysis', icon: '📊', action: (ctx) => ctx.cmd('analysisToolpak') },
        { id: 'solver', label: 'Solver', icon: '🔢', action: (ctx) => ctx.cmd('solver') },
      ]},
    ]},

    { id: 'view', label: 'View', keyTip: 'W', groups: [
      { name: 'Show', commands: [
        { id: 'gridlines', label: 'Gridlines', icon: '⊞', type: 'toggle', stateKey: 'gridlines', action: (ctx, on) => ctx.cmd('gridlines', on) },
        { id: 'formulaBar', label: 'Formula Bar', icon: 'fx', type: 'toggle', stateKey: 'formulaBar', action: (ctx, on) => ctx.cmd('formulaBar', on) },
        { id: 'headings', label: 'Headings', icon: 'H', type: 'toggle', stateKey: 'headings', action: (ctx, on) => ctx.cmd('headings', on) },
      ]},
      { name: 'Window', commands: [
        { id: 'freeze', label: 'Freeze Panes', icon: '❄', action: (ctx) => ctx.cmd('freeze') },
      ]},
    ]},
  ],
  contextual: [],
};