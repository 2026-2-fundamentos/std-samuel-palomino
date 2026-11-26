import csv
import gzip
from pathlib import Path


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
    result = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            letter = row[0]
            metrics = row[4].split(",")
            for item in metrics:
                key, value = item.split(":")
                result[letter] = result.get(letter, 0) + int(value)
    return dict(sorted(result.items()))
