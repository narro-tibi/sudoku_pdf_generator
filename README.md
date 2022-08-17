# Sudoku PDF Generator
Generator basierend auf https://pypi.org/project/py-sudoku/.
Der Generator wurde um PDF-Generierung und Anpassungsmöglichkeiten seitens des Users erweitert.

## Einstellungsmöglichkeiten
In der <i>settings.json</i> finden sich verschiedene Variablen, die man anpassen kann. Die angeführten Werte sind die Default-Werte.
Einige Sachen sind noch experimentell und müssen ausführlicher getestet werden. Zu großes Abweichen von manchen Default-Werten kann daher 
zu komischen Nebeneffekten führen.

| Variable              | Wert | Beschreibung                                                                                                    |
|-----------------------| --- |-----------------------------------------------------------------------------------------------------------------|
| PDF_FILE_NAME         | "test" | Name der generierten PDF. Haben zwei PDFs den gleichen Namen, wird der Name um eine Zahl inkrementiert.         |
| SUDOKU_SQUARE_SIZE    | 3 | Größe des Rasters.                                                                                              |
| SUDOKU_AMOUNT         | 500 | Anzahl zu generierender Sudokus.                                                                                |
| SUDOKUS_PER_PAGE      |  1 | Anzahl von Sudokus pro Seite. Wahlweise 1, 4 oder 6.                                                            |
| MIN_DIFFICULTY_LEVEL  |  0.62 | Mindestschwierigkeitsgrad der Sudokus.                                                                          |
| MAX_DIFFICULTY_LEVEL  |  0.76 | Maximalschwierigkeitsgrad der Sudokus (Anm.: nicht über 0.8 gehen, wenn man einzigartige Sudokus haben möchte). |
| CUSTOM_FONT           | "" | Eigene Fonts einbinden. <i>Noch nicht durchgetestet!</i>                                                        |
| FONT_SIZE_SINGLE_PAGE |  24 | Font-Size von Sudoku-Zahlen und Texten bei Einzelsudokus (1 pro Seite).                                         |
| FONT_SIZE_4_PAGE      |  18 | Font-Size von Sudoku-Zahlen und Texten bei 4-er Sudokus (4 pro Seite).                                          |
| FONT_SIZE_6_PAGE      |  12 | Font-Size von Sudoku-Zahlen und Texten bei 6-er Sudokus (6 pro Seite).                                          |
| FONT_SIZE_SOLUTIONS   |  10 | Font-Size von Sudoku-Zahlen und Texten auf den Lösungsseiten.                                                   |
| SHOW_SOLUTIONS        |  true | Ob Lösungen mit an die PDF gehängt werden sollen.                                                               |
| CUSTOM_TEXT           | "Sudoku: " | Text über jedem einzelnem Sudoku.                                                                               |

## How To
Einfach folgendes Skript im Ordner ausführen:
```bash
python3 main.py
```

Optional kann man die Anzahl gewünschter Sudokus auch als extra Argument mitgeben. Zu Testzwecken nützlich, oder wenn es mal schnell gehen soll.
```bash
python3 main.py <Menge>
```

### Eigene Fonts hinzufügen
Der default Font ist Helvetica. Eigene Fonts müssen als TTF-Files im <i>fonts</i>-Ordner hinterlegt werden. 
Der übergebene String sollte mit dem Namen der Datei übereinstimmen | sonst wird auf den default Font zurückgegriffen.
