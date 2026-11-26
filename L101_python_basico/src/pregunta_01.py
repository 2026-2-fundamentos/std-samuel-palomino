import gzip
import csv
from pathlib import Path


def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo `data/data.csv.gz` y retorne el resultado como un número entero.

    Ejemplo del formato de la respuesta:

        214
    """
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        total = 0
        for row in reader:
            total += int(row[1]) 
    return total