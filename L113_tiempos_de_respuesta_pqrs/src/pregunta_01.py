import os

import numpy as np
import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """
    df_web = pd.read_csv('data/historical_requests_web.csv.gz').drop_duplicates()
    df_letter = pd.read_csv('data/historical_requests_letter.csv.gz').drop_duplicates()
    
    df_web['channel'] = 'web'
    df_letter['channel'] = 'letter'
    
    df = pd.concat([df_web, df_letter], ignore_index=True)
    
    df['in_date'] = pd.to_datetime(df['in_date'])
    df['out_date'] = pd.to_datetime(df['out_date'])
    df['year'] = df['in_date'].dt.year
    df['day_of_week'] = df['in_date'].dt.dayofweek  
    
    if 'day_name' not in df.columns:
        df['day_name'] = df['in_date'].dt.day_name()
    
    answered_mask = df['out_date'].notna()
    
    df['calendar_days'] = np.nan
    df['business_days'] = np.nan
    
    df.loc[answered_mask, 'calendar_days'] = (df.loc[answered_mask, 'out_date'] - df.loc[answered_mask, 'in_date']).dt.days
    
    # Para excluir in_date e incluir out_date, desplazamos las fechas 1 día hacia adelante
    in_dates_arr = df.loc[answered_mask, 'in_date'].values.astype('datetime64[D]') + np.timedelta64(1, 'D')
    out_dates_arr = df.loc[answered_mask, 'out_date'].values.astype('datetime64[D]') + np.timedelta64(1, 'D')
    
    df.loc[answered_mask, 'business_days'] = np.busday_count(in_dates_arr, out_dates_arr)
    
    df['on_time'] = False
    df.loc[answered_mask, 'on_time'] = df.loc[answered_mask, 'business_days'] <= 15

    channel_summary = df.groupby('channel', as_index=False).agg(
        requests=('in_date', 'count'),
        answered=('out_date', 'count'),
        pending=('out_date', lambda x: x.isna().sum()),
        median_business_days=('business_days', 'median'),
        on_time_rate=('on_time', 'mean')
    ).sort_values('channel')
    
    yearly_summary = df.groupby(['year', 'channel'], as_index=False).agg(
        requests=('in_date', 'count'),
        pending=('out_date', lambda x: x.isna().sum()),
        on_time_rate=('on_time', 'mean')
    ).sort_values(['year', 'channel'])
    
    entry_day_summary = df.groupby(['day_of_week', 'day_name'], as_index=False).agg(
        requests=('in_date', 'count'),
        median_calendar_days=('calendar_days', 'median'),
        median_business_days=('business_days', 'median')
    )
    entry_day_summary = entry_day_summary.sort_values('day_of_week').drop(columns=['day_of_week'])
    
    os.makedirs('submission', exist_ok=True)
    channel_summary.to_csv('submission/channel_summary.csv', index=False)
    yearly_summary.to_csv('submission/yearly_summary.csv', index=False)
    entry_day_summary.to_csv('submission/entry_day_summary.csv', index=False)
    
    return channel_summary, yearly_summary, entry_day_summary