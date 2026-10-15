/**
 * Aderhold A.R.C. Pulse Survey collector (Google Apps Script, bound to the private response Sheet).
 *
 * - doGet serves the survey page for a campaign link:  <web app URL>?code=ACME-2026Q4
 * - submitResponse() appends one anonymous row to the "Responses" tab.
 * - Only campaigns listed as active in the "Campaigns" tab accept responses.
 * - Each campaign row says which engagement it belongs to, its wave (T1 baseline, T2 midpoint,
 *   T3 follow-up), its audience (staff or leader) and, for T2/T3, which recommendations
 *   (modules M1-M12) were implemented. The survey adapts its questions to these.
 *
 * Anonymity by design: no names, emails, IP addresses or exact timestamps are stored.
 * Run setup() once from the Apps Script editor to create the tabs and header row.
 */

var RESPONSES_TAB = 'Responses';
var CAMPAIGNS_TAB = 'Campaigns';
var MAX_OPEN_TEXT = 1000;

var CAMPAIGN_HEADERS = ['code', 'display_name', 'active', 'notes', 'engagement', 'wave', 'audience', 'modules'];

function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var resp = ss.getSheetByName(RESPONSES_TAB) || ss.insertSheet(RESPONSES_TAB);
  var cols = ARC_INSTRUMENT.columns;
  var current = resp.getLastColumn() > 0 ? resp.getRange(1, 1, 1, resp.getLastColumn()).getValues()[0] : [];
  if (current.join('|') !== cols.join('|')) {
    if (resp.getLastRow() > 1) {
      // Keep old responses: rename the tab after its instrument version and start a fresh one.
      var vCol = current.indexOf('instrument_version');
      var oldV = vCol >= 0 ? String(resp.getRange(2, vCol + 1).getValue() || '') : '';
      var name = oldV ? 'Responses v' + oldV : 'Responses (earlier version)';
      if (ss.getSheetByName(name)) name += ' ' + Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd HHmm');
      resp.setName(name);
      resp = ss.insertSheet(RESPONSES_TAB, 0);
      Logger.log('Previous responses kept in tab "' + name + '". New Responses tab created for v' + ARC_INSTRUMENT.version + '.');
    } else {
      resp.clear();
    }
    resp.getRange(1, 1, 1, cols.length).setValues([cols]).setFontWeight('bold');
    resp.setFrozenRows(1);
  }
  var camp = ss.getSheetByName(CAMPAIGNS_TAB);
  if (!camp) {
    camp = ss.insertSheet(CAMPAIGNS_TAB);
    camp.setFrozenRows(1);
  }
  // Older Campaigns tabs have 4 columns: add the new headers without touching existing rows.
  var head = camp.getRange(1, 1, 1, CAMPAIGN_HEADERS.length).getValues()[0];
  for (var i = 0; i < CAMPAIGN_HEADERS.length; i++) {
    if (!head[i]) camp.getRange(1, i + 1).setValue(CAMPAIGN_HEADERS[i]).setFontWeight('bold');
  }
  // Add any missing test campaigns (one per survey version) so every flow can be tried.
  // Existing test rows from older versions get their blank engagement/wave/audience/modules filled in.
  var existing = camp.getLastRow() > 1 ? camp.getRange(2, 1, camp.getLastRow() - 1, CAMPAIGN_HEADERS.length).getValues() : [];
  var codes = existing.map(function (r) { return normalizeCode_(r[0]); });
  TEST_CAMPAIGNS.forEach(function (row) {
    var at = codes.indexOf(row[0]);
    if (at < 0) { camp.appendRow(row); return; }
    for (var j = 4; j < CAMPAIGN_HEADERS.length; j++) {
      if (existing[at][j] === '' && row[j] !== '') camp.getRange(at + 2, j + 1).setValue(row[j]);
    }
  });
}

var TEST_CAMPAIGNS = [
  ['TEST-0001', 'Test campaign', true, 'Use for trying the survey; excluded from benchmarks', 'TEST', 'T1', 'staff', ''],
  ['TEST-LEAD', 'Test leadership survey', true, 'Leadership version', 'TEST', 'T1', 'leader', ''],
  ['TEST-T2', 'Test midpoint', true, 'Midpoint with exposure check', 'TEST', 'T2', 'staff', 'M3, M6, M7'],
  ['TEST-T3', 'Test follow-up', true, 'Follow-up with perceived change', 'TEST', 'T3', 'staff', 'M3, M6, M7']];

function doGet(e) {
  var code = normalizeCode_((e && e.parameter && e.parameter.code) || '');
  var campaign = findCampaign_(code);
  var t = HtmlService.createTemplateFromFile('Survey');
  t.campaignCode = campaign ? campaign.code : '';
  t.displayName = campaign ? campaign.displayName : '';
  t.isOpen = !!(campaign && campaign.active);
  // Why a link is closed: 'nocode' (link has no ?code=; note: "c" is reserved by Google and must not be used), 'notfound' (code not in Campaigns tab), 'inactive'
  t.closedReason = !code ? 'nocode' : (!campaign ? 'notfound' : (campaign.active ? '' : 'inactive'));
  t.requestedCode = code;
  t.campaignJson = JSON.stringify(campaign && campaign.active ?
    { wave: campaign.wave, audience: campaign.audience, modules: campaign.modules } : {});
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
  var leader = campaign.audience === 'leader';
  var row = {};
  row.response_id = Utilities.getUuid();
  row.campaign = campaign.code;
  row.engagement = campaign.engagement;
  row.wave = campaign.wave;
  row.audience = campaign.audience;
  row.submitted_date = Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd');
  row.consent_research = payload.consentResearch ? 1 : 0;
  row.instrument_version = ARC_INSTRUMENT.version;

  var answered = 0;
  ARC_INSTRUMENT.dimensions.forEach(function (d) {
    d.items.forEach(function (it) {
      row[it.id] = intIn_(answers[it.id], 1, 5);
      if (row[it.id] !== '') answered++;
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
  if (leader) {
    row.role = 'LEAD';
  } else if (['IC', 'MGR', 'SL'].indexOf(row.role) < 0) {
    throw new Error('Please select your role.');
  }

  // Exposure check (T2/T3): only for the modules this campaign lists.
  ARC_INSTRUMENT.exposure.items.forEach(function (x) {
    var asked = campaign.wave !== 'T1' && campaign.modules.indexOf(x.module) >= 0;
    row[x.id] = asked ? intIn_(answers[x.id], 0, 1) : '';
  });
  // Perceived change (T3 only).
  ARC_INSTRUMENT.change.items.forEach(function (x) {
    row[x.id] = campaign.wave === 'T3' ? intIn_(answers[x.id], -2, 2) : '';
  });
  // Leadership module (leadership survey only).
  ARC_INSTRUMENT.leadership.items.forEach(function (x) {
    row[x.id] = !leader ? '' : (x.type === 'likert' ? intIn_(answers[x.id], 1, 5) : intIn_(answers[x.id], 1, 4));
  });

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
  var width = Math.max(3, Math.min(CAMPAIGN_HEADERS.length, sh.getLastColumn()));
  var rows = sh.getRange(2, 1, sh.getLastRow() - 1, width).getValues();
  for (var i = 0; i < rows.length; i++) {
    if (normalizeCode_(rows[i][0]) === code) {
      var r = rows[i];
      var wave = String(r[5] || 'T1').trim().toUpperCase();
      var audience = String(r[6] || 'staff').trim().toLowerCase();
      var valid = ARC_INSTRUMENT.exposure.items.map(function (x) { return x.module; });
      var modules = String(r[7] || '').toUpperCase().split(/[^A-Z0-9]+/).filter(function (m) { return valid.indexOf(m) >= 0; });
      return {
        code: code, displayName: String(r[1] || ''), active: isActive_(r[2]),
        engagement: normalizeCode_(r[4]) || code,
        wave: ['T1', 'T2', 'T3'].indexOf(wave) >= 0 ? wave : 'T1',
        audience: audience === 'leader' ? 'leader' : 'staff',
        modules: modules
      };
    }
  }
  return null;
}

/** An integer between lo and hi, or '' (blank) for anything else. */
function intIn_(v, lo, hi) {
  if (v === '' || v === null || v === undefined) return '';
  var n = Number(v);
  return (Math.floor(n) === n && n >= lo && n <= hi) ? n : '';
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
  camp.getRange(2, 1, camp.getLastRow() - 1, 1).getValues().forEach(function (r, i) {
    var c = findCampaign_(normalizeCode_(r[0]));
    if (!c) return;
    Logger.log('Row ' + (i + 2) + ': code="' + c.code + '" active=' + c.active + ' engagement=' + c.engagement +
      ' wave=' + c.wave + ' audience=' + c.audience + (c.modules.length ? ' modules=' + c.modules.join(',') : ''));
  });
  var url = ScriptApp.getService().getUrl() || '';
  if (/\/dev$/.test(url)) {
    // When run from the editor, Google reports the private /dev test URL, which only the owner can open.
    Logger.log('NOTE: the editor reports the private test URL (ends in /dev). Respondents need the public /exec URL.');
    Logger.log('Get it from Deploy > Manage deployments (Web app, Execute as: Me, Who has access: Anyone), then add ?code=TEST-0001');
  } else if (url) {
    Logger.log('Test link: ' + url + '?code=TEST-0001');
  } else {
    Logger.log('Not deployed yet: Deploy > New deployment > Web app.');
  }
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
