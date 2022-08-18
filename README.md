# Sudoku PDF Generator
Generator basierend auf https://pypi.org/project/py-sudoku/.
Der Generator wurde um PDF-Generierung und Anpassungsmöglichkeiten seitens des Users erweitert.

## Einstellungsmöglichkeiten
In der <i>settings.json</i> finden sich verschiedene Variablen, die man anpassen kann. Die angeführten Werte sind die Default-Werte.
Einige Sachen sind noch experimentell und müssen ausführlicher getestet werden. Zu großes Abweichen von manchen Default-Werten kann daher 
zu komischen Nebeneffekten führen.

| Variable            | Wert       | Beschreibung                                                                                                                                    |
|---------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| PDF_FILE_NAME       | "test"     | Name der generierten PDF. Haben zwei PDFs den gleichen Namen, wird der Name um eine Zahl inkrementiert.                                         |
| SUDOKU_SQUARE_SIZE  | 3          | Größe des Rasters. (Höher als 3 auf eigene Gefahr, da das Skript <i>sehr</i> lange brauchen wird.)                                              |
| SUDOKU_AMOUNT       | 500        | Anzahl zu generierender Sudokus.                                                                                                                |
| SUDOKUS_PER_PAGE    | 1          | Anzahl von Sudokus pro Seite. Wahlweise 1, 4 oder 6.                                                                                            |
| DIFFICULTY_LEVEL  | Any        | Mindestschwierigkeitsgrad der Sudokus. Wahlweise Any (alle), Easy, Medium, Hard, Very Hard. Auch Begrenzung ist möglich (z.B.: "Easy, Medium"). |
| SORT_BY_DIFFICULTY  | true       | Ob die generierten Sudokus nach Schwierigkeitsgrad (Einfach -> Schwer) sortiert werden sollen.                                                  |
| CUSTOM_FONT         | ""         | Eigene Fonts einbinden. [Details](README.md#Eigene Fonts hinzufügen).                                                                                     |
| FONT_SIZE_SINGLE_PAGE | 24         | Font-Size von Sudoku-Zahlen und Texten bei Einzelsudokus (1 pro Seite).                                                                         |
| FONT_SIZE_4_PAGE    | 18         | Font-Size von Sudoku-Zahlen und Texten bei 4-er Sudokus (4 pro Seite).                                                                          |
| FONT_SIZE_6_PAGE    | 12         | Font-Size von Sudoku-Zahlen und Texten bei 6-er Sudokus (6 pro Seite).                                                                          |
| FONT_SIZE_SOLUTIONS | 10         | Font-Size von Sudoku-Zahlen und Texten auf den Lösungsseiten.                                                                                   |
| SHOW_SOLUTIONS      | true       | Ob Lösungen mit an die PDF gehängt werden sollen.                                                                                               |
| CUSTOM_TEXT         | "Sudoku: " | Text über jedem einzelnem Sudoku.                                                                                                               |
| SHOW_DIFFICULTY_TEXT         | false      | Ob der Schwierigkeitsgrad in Klammern hinter dem Sudokutext angezeigt werden soll.                                                              |

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
Der übergebene String sollte mit dem Namen der Datei übereinstimmen, sonst wird auf den default Font zurückgegriffen.
