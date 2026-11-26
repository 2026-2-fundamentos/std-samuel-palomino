import gzip
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
]


def clean_date(date_str):
    """Convierte una fecha a formato AAAA-MM-DD, si es posible."""
    date_str = str(date_str).strip().replace("-", "/")
    parts = date_str.split("/")
    if len(parts) == 3:
        if len(parts[0]) == 4:
            year, month, day = parts[0], parts[1], parts[2]
        else:
            day, month, year = parts[0], parts[1], parts[2]
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    return date_str


def clean_monto(monto_str):
    """Convierte un monto a un número entero, eliminando símbolos y separadores."""
    monto_str = str(monto_str).replace("$", "").replace(",", "").strip()
    try:
        return int(float(monto_str))
    except ValueError:
        return None

    
def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """
    root = Path(__file__).resolve().parents[1]
    source_file = root / "data" / "solicitudes_de_credito.csv.gz"
    output_file = root / "submission" / "solicitudes_de_credito.csv"

    with gzip.open(source_file, "rt", encoding="utf-8") as file:
        df = pd.read_csv(file, sep=";", dtype="string")

    df = df[REQUIRED_COLUMNS]
    df.dropna(inplace=True, subset=[col for col in REQUIRED_COLUMNS if col != "comuna_ciudadano"])

    text_columns = ["sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito"]
    for col in text_columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.lower()
            .str.strip()
            .str.replace("-", " ", regex=False)
            .str.replace("_", " ", regex=False)
            .apply(lambda x: " ".join(x.split()))
        )

    df["estrato"] = pd.to_numeric(df["estrato"], errors="coerce").astype("Int64")

    df["monto_del_credito"] = df["monto_del_credito"].apply(clean_monto).astype("Int64")

    # Convertir la columna de fecha a un formato uniforme (AAAA-MM-DD)
    # Algunas fechas están en formato DD/MM/AAAA, otras en MM/DD/AAAA, y algunas en AAAA-MM-DD.
    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].apply(clean_date)

    df.drop_duplicates(inplace=True)
    df.to_csv(output_file, sep=";", index=False)

    return df