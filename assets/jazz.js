/* Venerdì jazz da CTLF: un solo elenco per la home e per eventi.html.
   Per aggiungere una serata basta una riga qui; le date passate spariscono da sole. */
const JAZZ = [
  { d: '2026-10-23', who: 'Blanco / Fait / Lo Palo Trio', tag: 'JazzMI', line: 'Mirko Fait, sax · Beppe Blanco, piano · Andrea Lo Palo, batteria' },
  { d: '2026-10-30', who: 'Lupi Trio', tag: 'JazzMI', line: 'Sara Lupi, voce · Carmelo Tartamella, chitarra · Carlo Bavetta, contrabbasso' },
  { d: '2026-11-06', who: 'Mirko Fait Trio', tag: 'JazzMI', line: 'Mirko Fait, sax · Joe Zangaro, piano · Chiara Bianchi, contrabbasso', note: 'Il cool jazz e la bossanova degli anni ’50 e ’60.' },
  { d: '2026-11-13', who: 'Emma Ghezzi and The Rabbits', line: 'Emma Ghezzi, voce · Carmelo Tartamella, chitarra · Mirko Fait, sax', note: 'Una serata tra blues e swing.' },
  { d: '2026-11-20', who: 'Vigna Trio', tag: 'Milano Music Week', line: 'Sonia Lo Giudice, voce · Ignazio Vignali, voce e chitarra · Mirko Fait, sax', note: 'Da Napoli al Sudamerica fino agli States, tra swing e bossanova.' },
  { d: '2026-11-27', who: 'Odilla Rey Trio', line: 'Odilla Rey, voce · Carmelo Tartamella, chitarra · Mirko Fait, sax', note: 'Dal soul al blues, dal pop al jazz.' }
];
(function () {
  const MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  const oggi = new Date(); oggi.setHours(0, 0, 0, 0);
  const prossime = JAZZ.filter(j => new Date(j.d + 'T23:59:00') >= oggi);
  const giorno = j => { const t = new Date(j.d + 'T12:00:00'); return { n: t.getDate(), m: MESI[t.getMonth()] }; };

  // home: la fascia nell'hero mostra la prossima serata
  const when = document.querySelector('[data-jazz-when]');
  const who = document.querySelector('[data-jazz-who]');
  if (when && who && prossime.length) {
    const p = prossime[0], g = giorno(p);
    when.textContent = `Jazz live · venerdì ${g.n} ${g.m} · 19 e 22`;
    who.textContent = p.who;
  }

  // eventi.html: elenco delle prossime serate
  const list = document.querySelector('[data-jazz-list]');
  if (list && prossime.length) {
    list.innerHTML = prossime.map((j, i) => {
      const g = giorno(j);
      return `<li class="gig${i === 0 ? ' gig--next' : ''}">
        <div class="gig__date"><span class="date__day">Venerdì</span><span class="date__n">${g.n}</span><span class="date__m">${g.m}</span></div>
        <div class="gig__body">
          ${i === 0 ? '<span class="gig__tag">La prossima</span>' : j.tag ? `<span class="gig__tag">${j.tag}</span>` : ''}
          <h3>${j.who}</h3>
          <p class="gig__line">${j.line}</p>
          ${j.note ? `<p class="gig__note">${j.note}</p>` : ''}
        </div>
      </li>`;
    }).join('');
  }
})();
