![](https://www.daserste.de/information/nachrichten-wetter/tagesschau/tagesschau-fallback-100~_v-facebook1200_f8a628.jpg)
# Tagesschau Analysis
 Diese Repository enthält den Code für eine Analyse der Tagesschau Episoden.

## Woher kommen die Daten dafür?
Die Daten wurden mithilfe eines Scrapers automatisch aus dem Archiv der Tagesschau extrahiert, der scraper ist unter scripts/scraper.py zu finden.

## Mit welchen Tools wurde die Analyse durchgeführt?
Die Analyse wurde in Python mit Pandas/NumPy durchgeführt die Graphen (zu finden unter plots/as_png) wurden in Plotly erstellt. Für die Analyse mit NLP wurde die Transformers Library von Hugginface benutzt.
