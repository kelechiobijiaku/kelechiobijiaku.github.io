const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {lagosDate, phase, countdown} = require('../events.js');
const event = JSON.parse(fs.readFileSync('data/events.json', 'utf8')).events[0];

test('historical NBA engagement stays archived without fabricating an exact date', () => {
  const nba = JSON.parse(fs.readFileSync('data/events.json', 'utf8')).events.find(e => e.id === 'nba-annual-general-conference-2026');
  assert.equal(nba.date, undefined);
  assert.equal(phase(nba, new Date('2026-11-25T12:00:00Z')), 'past');
  assert.equal(phase(nba, new Date('2027-01-01T00:00:00Z')), 'past');
  assert.match(nba.representation, /Fatai Idowu Onafowote.*invited speaker/);
  assert.match(nba.representation, /Lagos State Public Procurement Agency/);
  assert.equal(nba.registrationUrl, undefined);
});

test('event date and archive boundary use Lagos time in any visitor timezone', () => {
  for (const tz of ['UTC', 'America/Los_Angeles', 'Asia/Tokyo', 'Africa/Lagos']) {
    process.env.TZ = tz;
    assert.equal(phase(event, new Date('2026-12-01T22:59:59Z')), 'upcoming');
    assert.equal(phase(event, new Date('2026-12-01T23:00:00Z')), 'live');
    assert.equal(phase(event, new Date('2026-12-02T22:59:59.999Z')), 'live');
    assert.equal(phase(event, new Date('2026-12-02T23:00:00Z')), 'past');
    assert.equal(lagosDate(new Date('2026-12-02T23:00:00Z')), '2026-12-03');
  }
});

test('countdown ticks to the event date without inventing a session start time', () => {
  assert.deepEqual(countdown(event, new Date('2026-11-25T23:00:00Z')), {days:6,hours:0,minutes:0,seconds:0});
  assert.deepEqual(countdown(event, new Date('2026-12-01T22:59:59Z')), {days:0,hours:0,minutes:0,seconds:1});
  assert.deepEqual(countdown(event, new Date('2026-12-03T00:00:00Z')), {days:0,hours:0,minutes:0,seconds:0});
});

test('an already open page archives the event and removes registration at Lagos midnight', () => {
  const dataContext = {window:{}};
  vm.runInNewContext(fs.readFileSync('data/events-data.js','utf8'), dataContext);
  const lists = ['featured','upcoming','past'].map(kind => ({dataset:{eventList:kind},innerHTML:''}));
  const promotion = {hidden:false};
  const archiveNote = {hidden:true};
  const status = {textContent:''};
  const body = {dataset:{eventId:event.id}};
  let clock = Date.parse('2026-12-02T22:59:59Z');
  let tick;
  class FakeDate extends Date { constructor(...args) { super(...(args.length ? args : [clock])); } }
  const document = {
    body, hidden:false, addEventListener(){}, getElementById(){return null;},
    querySelectorAll(selector) {
      return ({'[data-event-list]':lists,'[data-event-status]':[status],'[data-upcoming-only]':[promotion],'[data-past-only]':[archiveNote],'.flyer-gallery figure':[],'script[type="application/ld+json"]':[],'[data-event-countdown]':[]})[selector] || [];
    }
  };
  const window = {document, SPEAKING_EVENTS_DATA:dataContext.window.SPEAKING_EVENTS_DATA, setInterval(fn){tick=fn;},addEventListener(){}};
  vm.runInNewContext(fs.readFileSync('events.js','utf8'), {window,document,Date:FakeDate,Intl,Map,location:{origin:'https://kelechiobijiaku.com'}});
  assert.match(lists[0].innerHTML,/Register to attend/);
  assert.equal(promotion.hidden,false);
  clock = Date.parse('2026-12-02T23:00:00Z');
  tick();
  assert.equal(body.dataset.eventPhase,'past');
  assert.equal(promotion.hidden,true);
  assert.equal(archiveNote.hidden,false);
  assert.doesNotMatch(lists[0].innerHTML,/Register to attend|data-event-countdown/);
  assert.match(lists[0].innerHTML,/The next conversation is taking shape/);
  assert.match(lists[2].innerHTML,/View event archive/);
  assert.doesNotMatch(lists[2].innerHTML,/Register to attend|data-event-countdown/);
});
