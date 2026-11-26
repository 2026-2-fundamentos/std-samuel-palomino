import csv
import gzip
from pathlib import Path


def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """
    letters = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            letters.setdefault(int(row[1]), set()).add(row[0])
    return sorted((value, sorted(list(letters_set))) for value, letters_set in letters.items())
