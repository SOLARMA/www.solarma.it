# -*- coding: utf-8 -*-
"""Build the review package: a ZIP a non-technical reviewer can open offline.

Produces build/SOLARMA-anteprima-sito.zip containing the whole site plus an
Italian instruction sheet. The reviewer extracts it and double-clicks
index.html -- no web server, no tooling, no internet connection needed.
This works because every internal link and asset reference in the site is
relative; see the note on 404.html below.

Usage:  python3 tools/build-review-package.py
"""
import shutil
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
NAME = "SOLARMA-anteprima-sito"
OUT = BUILD / NAME

PAGES = ["index.html", "azienda.html", "impianto.html", "servizi.html",
         "contatti.html", "note-legali.html"]

# 404.html is deliberately excluded: it is the one page that keeps
# root-absolute paths (GitHub Pages serves it at whatever URL was requested),
# so it cannot render correctly from a folder on disk.

ISTRUZIONI = """\
SOLARMA S.n.c. - ANTEPRIMA DEL NUOVO SITO INTERNET
==================================================

Questa cartella contiene una copia completa del nuovo sito, da consultare sul
proprio computer prima della pubblicazione su www.solarma.it.
Non serve una connessione a internet e non serve installare nulla.


COME APRIRE IL SITO
-------------------

1. Se non lo avete gia' fatto, estraete il contenuto del file .zip:

     - Windows: clic destro sul file .zip -> "Estrai tutto..." -> "Estrai"
     - Mac:     doppio clic sul file .zip

   IMPORTANTE: il sito non funziona se si guarda dentro al file .zip senza
   averlo prima estratto. Se le pagine appaiono senza colori ne' immagini,
   quasi certamente la cartella non e' stata estratta.

2. Aprite la cartella estratta e fate doppio clic sul file:

     index.html

   Il sito si aprira' nel vostro browser abituale (Edge, Chrome, Firefox
   o Safari).

3. Da li' potete navigare normalmente usando il menu in alto:
   Home, Azienda, Impianto, Servizi, Contatti, e il pulsante IT / EN per
   passare dalla versione italiana a quella inglese.


COSA VI CHIEDIAMO DI GUARDARE
-----------------------------

  - I testi: sono corretti? C'e' qualcosa da aggiungere o da togliere?
  - I dati aziendali (sede, partita IVA, numero REA, PEC, codice SDI):
    sono esatti?
  - Il tono: e' adatto a come vogliamo presentarci ai clienti?

Dove trovate la sigla "n.d." significa che manca un dato che dobbiamo ancora
fornire (per esempio la potenza dell'impianto in kWp o la produzione annua).
Allo stesso modo, i riquadri grigi a righe indicano i punti in cui andranno
le fotografie dell'impianto, non ancora disponibili.


DIFFERENZE RISPETTO AL SITO PUBBLICATO
--------------------------------------

Trattandosi di un'anteprima sul vostro computer:

  - nella barra degli indirizzi vedrete un percorso del vostro computer
    invece di www.solarma.it;
  - gli indirizzi delle pagine terminano con ".html";
  - l'avviso sui cookie viene mostrato, ma la scelta potrebbe non essere
    ricordata da una pagina all'altra;
  - la pagina di errore "pagina non trovata" non e' inclusa nell'anteprima.

I contenuti e l'aspetto grafico sono invece identici a quelli che avra' il
sito una volta pubblicato.


COME SEGNALARE LE CORREZIONI
----------------------------

Indicate la pagina (per esempio "Azienda") e la frase da correggere, e
inviate le vostre note a info@solarma.it.
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for name in PAGES:
        shutil.copy(ROOT / name, OUT / name)
    shutil.copytree(ROOT / "en", OUT / "en")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "images").mkdir()
    shutil.copy(ROOT / "images" / "SOLARMA_logo.png", OUT / "images" / "SOLARMA_logo.png")

    (OUT / "LEGGIMI - come vedere il sito.txt").write_text(ISTRUZIONI, encoding="utf-8")

    archive = shutil.make_archive(str(BUILD / NAME), "zip", root_dir=BUILD, base_dir=NAME)
    size = pathlib.Path(archive).stat().st_size
    print("built %s (%.0f KB, %d files)"
          % (archive, size / 1024, sum(1 for f in OUT.rglob("*") if f.is_file())))


if __name__ == "__main__":
    main()
