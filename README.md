# CTLF — Two Moods. One Place.

Sito di lancio per **CTLF** (rebrand di City Life Caffè, Via Masaccio 18, Milano):
landing 3D dove **lo scroll è la giornata** — si parte con la luce del mattino
(colazione business) e si scende fino alla sera (aperitivo, luci soffuse),
con il diamante del monogramma in oro che accompagna ogni sezione.

## Come vederlo subito

**Il modo più semplice:** scaricate [`CTLF-sito-standalone.html`](CTLF-sito-standalone.html)
e apritelo con un doppio clic in Chrome o Safari. È un file unico con tutto dentro
(serve solo la connessione internet per font e librerie 3D).

In alternativa, dalla cartella del progetto:

```bash
python3 -m http.server 4173
# poi aprire http://localhost:4173
```

## Cosa contiene

| Sezione | Contenuto |
|---|---|
| Hero | Monogramma CTLF, payoff *Two Moods. One Place.* |
| Il ritmo | I quattro momenti della giornata (07:30 → sera) |
| Menù | Carta reale: panini, pizza in pala, focacce, aperitivo |
| Vision & Due anime | Il racconto del brand — da Bruce Wayne a Batman |
| Eventi & Corporate | Meeting, aperitivi aziendali, eventi privati nel weekend |
| Convenzioni | Formule per le aziende della zona CityLife |
| Instagram | Gli ultimi post di @ctlfmilano a scorrimento, il più recente per primo |
| Prenota | Form che prepara un messaggio WhatsApp precompilato |

## File

- `index.html` — il sito (sorgente unico: HTML + CSS + JS)
- `assets/` — logo oro, maschera del monogramma, favicon (estratti dal brand book)
- `CTLF-sito-standalone.html` — versione monofile da condividere
- `scripts/instagram_sync.py` + `.github/workflows/instagram.yml` — ogni 3 ore
  scaricano gli ultimi post di Instagram in `assets/instagram/` e riscrivono le card
  in `index.html` (fra `IG:START` e `IG:END`). Per l'aggiornamento affidabile serve il
  secret `IG_TOKEN` del repo: token long-lived dell'API Instagram (login Instagram)
  dell'account ctlfmilano. Lancio manuale: tab Actions → Instagram feed → Run workflow.

## Dati reali

Menù, prezzi, orari e contatti provengono dal locale attuale (citylifecaffe.it):
Via Masaccio 18, 20149 Milano · +39 02 8363 6159 · WhatsApp +39 342 546 7527 ·
lun–ven 07:00–23:00, weekend riservato agli eventi privati.
