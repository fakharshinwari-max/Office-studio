/**
 * Built-in templates for Writer / Sheets / Slides.
 */
export const TEMPLATES = {
  word: [
    {
      id: 'blank', name: 'Blank document', icon: '📄',
      model: {
        meta: { title: 'Untitled' }, pageSetup: {},
        blocks: [{ type: 'paragraph', runs: [{ text: '', attrs: {} }], attrs: {} }],
      },
    },
    {
      id: 'resume', name: 'Resume', icon: '📋',
      model: {
        meta: { title: 'Resume' },
        blocks: [
          { type: 'heading', runs: [{ text: 'Your Name', attrs: {} }], attrs: { level: 1 } },
          { type: 'paragraph', runs: [{ text: 'Email · Phone · City', attrs: { color: '#666' } }], attrs: {} },
          { type: 'heading', runs: [{ text: 'Experience', attrs: {} }], attrs: { level: 2 } },
          { type: 'paragraph', runs: [{ text: 'Job Title — Company (2020–Present)', attrs: { bold: true } }], attrs: {} },
          { type: 'paragraph', runs: [{ text: 'Describe a key accomplishment here.', attrs: {} }], attrs: {} },
          { type: 'heading', runs: [{ text: 'Education', attrs: {} }], attrs: { level: 2 } },
          { type: 'paragraph', runs: [{ text: 'Degree, University, Year', attrs: {} }], attrs: {} },
          { type: 'heading', runs: [{ text: 'Skills', attrs: {} }], attrs: { level: 2 } },
          { type: 'paragraph', runs: [{ text: 'Skill · Skill · Skill', attrs: {} }], attrs: {} },
        ],
      },
    },
    {
      id: 'report', name: 'Report', icon: '📊',
      model: {
        meta: { title: 'Report' },
        blocks: [
          { type: 'heading', runs: [{ text: 'Report Title', attrs: {} }], attrs: { level: 1 } },
          { type: 'paragraph', runs: [{ text: 'Author · ' + new Date().toLocaleDateString(), attrs: { color: '#666' } }], attrs: {} },
          { type: 'heading', runs: [{ text: 'Executive Summary', attrs: {} }], attrs: { level: 2 } },
          { type: 'paragraph', runs: [{ text: 'Summarize the key findings.', attrs: {} }], attrs: {} },
          { type: 'heading', runs: [{ text: 'Findings', attrs: {} }], attrs: { level: 2 } },
          { type: 'paragraph', runs: [{ text: 'Detail the analysis here.', attrs: {} }], attrs: {} },
          { type: 'heading', runs: [{ text: 'Recommendations', attrs: {} }], attrs: { level: 2 } },
          { type: 'paragraph', runs: [{ text: 'List the next steps.', attrs: {} }], attrs: {} },
        ],
      },
    },
    {
      id: 'letter', name: 'Formal letter', icon: '✉️',
      model: {
        meta: { title: 'Letter' },
        blocks: [
          { type: 'paragraph', runs: [{ text: new Date().toLocaleDateString(), attrs: {} }], attrs: {} },
          { type: 'paragraph', runs: [{ text: 'Recipient Name', attrs: {} }], attrs: {} },
          { type: 'paragraph', runs: [{ text: 'Dear Recipient,', attrs: {} }], attrs: {} },
          { type: 'paragraph', runs: [{ text: 'Body of your letter goes here.', attrs: {} }], attrs: {} },
          { type: 'paragraph', runs: [{ text: 'Sincerely,', attrs: {} }], attrs: {} },
          { type: 'paragraph', runs: [{ text: 'Your Name', attrs: { bold: true } }], attrs: {} },
        ],
      },
    },
  ],
  sheets: [
    {
      id: 'blank', name: 'Blank spreadsheet', icon: '📊',
      model: { meta: { title: 'Untitled' }, sheets: [{ name: 'Sheet1', cells: {}, cf: [], validations: [], charts: [] }], namedRanges: [] },
    },
    {
      id: 'budget', name: 'Monthly budget', icon: '💰',
      model: {
        meta: { title: 'Budget' },
        sheets: [{
          name: 'Budget',
          cells: {
            'A1': { v: 'Category', s: { bold: true, fill: '#dfe9f7' } },
            'B1': { v: 'Budget', s: { bold: true, fill: '#dfe9f7' } },
            'C1': { v: 'Actual', s: { bold: true, fill: '#dfe9f7' } },
            'D1': { v: 'Difference', s: { bold: true, fill: '#dfe9f7' } },
            'A2': { v: 'Rent' }, 'B2': { v: 1500 }, 'C2': { v: 1500 },
            'D2': { f: '=C2-B2', s: { numfmt: '$#,##0.00' } },
            'A3': { v: 'Groceries' }, 'B3': { v: 400 }, 'C3': { v: 380 },
            'D3': { f: '=C3-B3', s: { numfmt: '$#,##0.00' } },
            'A4': { v: 'Utilities' }, 'B4': { v: 200 }, 'C4': { v: 220 },
            'D4': { f: '=C4-B4', s: { numfmt: '$#,##0.00' } },
            'A5': { v: 'Total', s: { bold: true } }, 'B5': { f: '=SUM(B2:B4)', s: { bold: true, numfmt: '$#,##0.00' } },
            'C5': { f: '=SUM(C2:C4)', s: { bold: true, numfmt: '$#,##0.00' } },
            'D5': { f: '=SUM(D2:D4)', s: { bold: true, numfmt: '$#,##0.00' } },
          }, cf: [], validations: [], charts: [],
        }], namedRanges: [],
      },
    },
    {
      id: 'tracker', name: 'Project tracker', icon: '📈',
      model: {
        meta: { title: 'Project Tracker' },
        sheets: [{
          name: 'Tasks',
          cells: {
            'A1': { v: 'Task', s: { bold: true, fill: '#e8f5e9' } },
            'B1': { v: 'Owner', s: { bold: true, fill: '#e8f5e9' } },
            'C1': { v: 'Status', s: { bold: true, fill: '#e8f5e9' } },
            'D1': { v: 'Due', s: { bold: true, fill: '#e8f5e9' } },
            'E1': { v: 'Progress', s: { bold: true, fill: '#e8f5e9' } },
            'A2': { v: 'Design mockups' }, 'B2': { v: 'Alex' }, 'C2': { v: 'In progress' }, 'D2': { v: '2026-01-15' }, 'E2': { v: 0.6 },
            'A3': { v: 'Backend API' }, 'B3': { v: 'Sam' }, 'C3': { v: 'Not started' }, 'D3': { v: '2026-02-01' }, 'E3': { v: 0 },
            'A4': { v: 'Testing plan' }, 'B4': { v: 'Riya' }, 'C4': { v: 'Done' }, 'D4': { v: '2026-01-05' }, 'E4': { v: 1 },
          }, cf: [
            { range: 'C2:C100', type: 'cell', criteria: '=', value: 'Done', format: { fill: '#c6efce', color: '#006100' } },
            { range: 'C2:C100', type: 'cell', criteria: '=', value: 'In progress', format: { fill: '#ffeb9c', color: '#9c6500' } },
          ], validations: [], charts: [],
        }], namedRanges: [],
      },
    },
  ],
  slides: [
    {
      id: 'blank', name: 'Blank deck', icon: '📽️',
      model: { meta: { title: 'Untitled' }, size: { w: 13.333, h: 7.5 }, theme: 'office',
               slides: [{ layout: 'blank', objects: [], notes: '', transition: null }] },
    },
    {
      id: 'pitch', name: 'Startup pitch', icon: '🎯',
      model: {
        meta: { title: 'Pitch' }, size: { w: 13.333, h: 7.5 }, theme: 'bold',
        slides: [
          { layout: 'title-content', objects: [
            { id: 'o1', type: 'text', x: 100, y: 250, w: 1080, h: 100, rot: 0, props: { text: 'Company Name', fontSize: 48, bold: true, color: '#ffffff' } },
            { id: 'o2', type: 'text', x: 100, y: 360, w: 1080, h: 60, rot: 0, props: { text: 'Tagline goes here', fontSize: 24, color: '#ffffff' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 'o3', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'The Problem', fontSize: 40, bold: true, color: '#ffffff' } },
            { id: 'o4', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: '• Pain point 1\n• Pain point 2\n• Pain point 3', fontSize: 22, color: '#ffffff' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 'o5', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'Our Solution', fontSize: 40, bold: true, color: '#ffffff' } },
            { id: 'o6', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: '• Value proposition 1\n• Value proposition 2', fontSize: 22, color: '#ffffff' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 'o7', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'The Market', fontSize: 40, bold: true, color: '#ffffff' } },
            { id: 'o8', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: '• TAM $X B\n• SAM $Y B\n• SOM $Z B', fontSize: 22, color: '#ffffff' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 'o9', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'The Ask', fontSize: 40, bold: true, color: '#ffffff' } },
            { id: 'o10', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: 'We are raising $X for Y.', fontSize: 22, color: '#ffffff' } },
          ], notes: '', transition: { name: 'fade' } },
        ],
      },
    },
    {
      id: 'lesson', name: 'Lesson plan', icon: '🎓',
      model: {
        meta: { title: 'Lesson' }, size: { w: 13.333, h: 7.5 }, theme: 'office',
        slides: [
          { layout: 'title-content', objects: [
            { id: 't1', type: 'text', x: 80, y: 250, w: 1120, h: 100, rot: 0, props: { text: 'Lesson Title', fontSize: 44, bold: true, color: '#1f1f1f' } },
            { id: 't2', type: 'text', x: 80, y: 360, w: 1120, h: 60, rot: 0, props: { text: 'Subject · Grade · Date', fontSize: 22, color: '#666' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 't3', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'Learning objectives', fontSize: 40, bold: true, color: '#1f1f1f' } },
            { id: 't4', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: '• Objective 1\n• Objective 2', fontSize: 22, color: '#1f1f1f' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 't5', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'Warm-up', fontSize: 40, bold: true, color: '#1f1f1f' } },
            { id: 't6', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: 'Quick activity to activate prior knowledge.', fontSize: 22, color: '#1f1f1f' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 't7', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'Main activity', fontSize: 40, bold: true, color: '#1f1f1f' } },
            { id: 't8', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: 'Describe the activity here.', fontSize: 22, color: '#1f1f1f' } },
          ], notes: '', transition: { name: 'fade' } },
          { layout: 'title-content', objects: [
            { id: 't9', type: 'text', x: 80, y: 60, w: 1120, h: 100, rot: 0, props: { text: 'Assessment', fontSize: 40, bold: true, color: '#1f1f1f' } },
            { id: 't10', type: 'text', x: 80, y: 200, w: 1120, h: 460, rot: 0, props: { text: 'How will you check understanding?', fontSize: 22, color: '#1f1f1f' } },
          ], notes: '', transition: { name: 'fade' } },
        ],
      },
    },
  ],
};

export function getTemplates(kind) { return TEMPLATES[kind] || []; }