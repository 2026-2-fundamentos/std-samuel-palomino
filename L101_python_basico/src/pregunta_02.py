import csv
import gzip
from pathlib import Path


def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        letter_count = {}
        for row in reader:
            letter = row[0]
            letter_count[letter] = letter_count.get(letter, 0) + 1
    return sorted(letter_count.items())
