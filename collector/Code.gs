/**
 * Aderhold A.R.C. Pulse Survey collector (Google Apps Script, bound to the private response Sheet).
 *
 * - doGet serves the survey page for a campaign link:  <web app URL>?c=ACME-2026Q4
 * - submitResponse() appends one anonymous row to the "Responses" tab.
 * - Only campaigns listed as active in the "Campaigns" tab accept responses.
 *
 * Anonymity by design: no names, emails, IP addresses or exact timestamps are stored.
 * Run setup() once from the Apps Script editor to create the tabs and header row.
 */

var RESPONSES_TAB = 'Responses';
var CAMPAIGNS_TAB = 'Campaigns';
var MAX_OPEN_TEXT = 1000;

function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var resp = ss.getSheetByName(RESPONSES_TAB) || ss.insertSheet(RESPONSES_TAB);
  var cols = ARC_INSTRUMENT.columns;
  var current = resp.getLastColumn() > 0 ? resp.getRange(1, 1, 1, resp.getLastColumn()).getValues()[0] : [];
  if (current.join('|') !== cols.join('|')) {
    if (resp.getLastRow() > 1) {
      throw new Error('Responses tab already has data with different columns. Create a new tab for a new instrument version.');
    }
    resp.clear();
    resp.getRange(1, 1, 1, cols.length).setValues([cols]).setFontWeight('bold');
    resp.setFrozenRows(1);
  }
  var camp = ss.getSheetByName(CAMPAIGNS_TAB);
  if (!camp) {
    camp = ss.insertSheet(CAMPAIGNS_TAB);
    camp.getRange(1, 1, 1, 4).setValues([['code', 'display_name', 'active', 'notes']]).setFontWeight('bold');
    camp.getRange(2, 1, 1, 4).setValues([['TEST-0001', 'Test campaign', true, 'Use for trying the survey; excluded from benchmarks']]);
    camp.setFrozenRows(1);
  }
}

function doGet(e) {
  var code = normalizeCode_((e && e.parameter && e.parameter.c) || '');
  var campaign = findCampaign_(code);
  var t = HtmlService.createTemplateFromFile('Survey');
  t.campaignCode = campaign ? campaign.code : '';
  t.displayName = campaign ? campaign.displayName : '';
  t.isOpen = !!(campaign && campaign.active);
  // Why a link is closed: 'nocode' (link has no ?c=), 'notfound' (code not in Campaigns tab), 'inactive'
  t.closedReason = !code ? 'nocode' : (!campaign ? 'notfound' : (campaign.active ? '' : 'inactive'));
  t.requestedCode = code;
  t.instrumentJson = JSON.stringify(ARC_INSTRUMENT);
  return t.evaluate()
    .setTitle('Aderhold A.R.C. Pulse Survey')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}

/** Called from the survey page via google.script.run. Returns {ok:true} or throws. */
function submitResponse(payload) {
  if (!payload || typeof payload !== 'object') throw new Error('Empty submission.');
  if (payload.website) return { ok: true }; // honeypot field filled: silently drop bots
  var campaign = findCampaign_(normalizeCode_(payload.campaign));
  if (!campaign || !campaign.active) throw new Error('This survey link is not active.');

  var answers = payload.answers || {};
  var row = {};
  row.response_id = Utilities.getUuid();
  row.campaign = campaign.code;
  row.submitted_date = Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd');
  row.consent_research = payload.consentResearch ? 1 : 0;
  row.instrument_version = ARC_INSTRUMENT.version;

  var answered = 0;
  ARC_INSTRUMENT.dimensions.forEach(function (d) {
    d.items.forEach(function (it) {
      var v = Number(answers[it.id]);
      if (v >= 1 && v <= 5 && Math.floor(v) === v) { row[it.id] = v; answered++; } else { row[it.id] = ''; }
    });
  });
  var totalItems = ARC_INSTRUMENT.dimensions.reduce(function (n, d) { return n + d.items.length; }, 0);
  if (answered < totalItems / 2) throw new Error('Please answer at least half of the statements.');

  ARC_INSTRUMENT.behavioral.forEach(function (b) {
    var raw = answers[b.key];
    var allowed = b.options.map(function (o) { return o.value === null ? '' : String(o.value); });
    var val = (raw === undefined || raw === null) ? '' : String(raw);
    row[b.key] = allowed.indexOf(val) >= 0 ? val : '';
  });
  if (['IC', 'MGR', 'SL'].indexOf(row.role) < 0) throw new Error('Please select your role.');

  row.open_text = sanitizeText_(answers.open_text);

  var cols = ARC_INSTRUMENT.columns;
  var values = cols.map(function (c) { return row[c] === undefined ? '' : row[c]; });
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName(RESPONSES_TAB).appendRow(values);
  } finally {
    lock.releaseLock();
  }
  return { ok: true };
}

function findCampaign_(code) {
  if (!code) return null;
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CAMPAIGNS_TAB);
  if (!sh || sh.getLastRow() < 2) return null;
  var rows = sh.getRange(2, 1, sh.getLastRow() - 1, 3).getValues();
  for (var i = 0; i < rows.length; i++) {
    if (normalizeCode_(rows[i][0]) === code) {
      return { code: code, displayName: String(rows[i][1] || ''), active: isActive_(rows[i][2]) };
    }
  }
  return null;
}

/** Accepts a ticked checkbox, TRUE, Yes, Y, 1 or Open (any case, extra spaces ignored). */
function isActive_(v) {
  if (v === true) return true;
  return ['TRUE', 'YES', 'Y', '1', 'OPEN', 'ACTIVE'].indexOf(String(v).trim().toUpperCase()) >= 0;
}

/**
 * Run from the Apps Script editor (select checkSetup, click Run, then View > Logs / Execution log)
 * to see what the survey sees: tabs, campaign codes and whether each is active.
 */
function checkSetup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  Logger.log('Spreadsheet: ' + ss.getName());
  Logger.log('Tabs: ' + ss.getSheets().map(function (s) { return s.getName(); }).join(', '));
  var camp = ss.getSheetByName(CAMPAIGNS_TAB);
  if (!camp) { Logger.log('PROBLEM: no "' + CAMPAIGNS_TAB + '" tab. Run setup() first.'); return; }
  if (camp.getLastRow() < 2) { Logger.log('PROBLEM: Campaigns tab has no rows below the header.'); return; }
  camp.getRange(2, 1, camp.getLastRow() - 1, 3).getValues().forEach(function (r, i) {
    Logger.log('Row ' + (i + 2) + ': code="' + normalizeCode_(r[0]) + '" active=' + isActive_(r[2]) + ' (cell value: ' + JSON.stringify(r[2]) + ')');
  });
  var url = ScriptApp.getService().getUrl();
  Logger.log('Web app URL (current deployment): ' + (url || 'not deployed yet'));
  if (url) Logger.log('Test link: ' + url + '?c=TEST-0001');
}

function normalizeCode_(c) {
  return String(c || '').trim().toUpperCase().replace(/[^A-Z0-9_-]/g, '').slice(0, 40);
}

/** Strip control characters, cap length, and neutralize spreadsheet formula injection. */
function sanitizeText_(t) {
  var s = String(t || '').replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, ' ').trim().slice(0, MAX_OPEN_TEXT);
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
  return s;
}
