import csv
import gzip
from pathlib import Path


def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """
    result = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            value = int(row[1])
            codes = row[3].split(",")
            for code in codes:
                result[code] = result.get(code, 0) + value
    return dict(sorted(result.items()))
