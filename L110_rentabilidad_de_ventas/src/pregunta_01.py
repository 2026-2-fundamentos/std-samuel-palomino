import os

import numpy as np
import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
      """
      Una cadena de suministros de oficina vende mucho, pero la gerencia
      sospecha que parte de esas ventas no deja utilidad. El archivo
      `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
      el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
      (`Profit`), el descuento aplicado (`Discount`, como proporción), el
      segmento del cliente (`Customer Segment`) y la categoría del producto
      (`Product Category`). Una utilidad negativa significa que la línea se
      vendió con pérdida.

      Use estas definiciones:

      - Margen (`profit_margin`): utilidad sobre ventas.
      - Línea con pérdida: una línea cuya utilidad es negativa.
      - `loss_line_rate`: la proporción de líneas con pérdida.
      - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
         escrita como número positivo.
      - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
         `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
         hasta 10 %, y `más de 10%` en otro caso.

      Genere tres archivos en `submission/`, sin el índice de Pandas y con las
      columnas en el orden indicado:

      1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
         líneas), `orders` (pedidos distintos), `sales`, `profit`,
         `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
         `loss_line_rate` y `lost_profit`.

      2. `discount_summary.csv`, con una fila por rango de descuento, en el
         orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
         `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

      3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
         que más utilidad pierden: `Customer Segment`, `Product Category`,
         `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
         solamente segmentos con al menos 100 líneas y ordénelos por
         `lost_profit` de mayor a menor.

      La función también debe retornar las tres tablas, en el mismo orden.

      Ejemplo del formato de `discount_summary.csv`:

         discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
         0%,166,170539.05,29472.3789,0.1728,0.488,...
         ...
      """
      df = pd.read_csv('data/superstore_orders.csv.gz', sep=";", decimal=",")

      # Columnas auxiliares para facilitar los cálculos
      df['is_loss'] = df['Profit'] < 0
      df['lost_profit_val'] = np.where(df['is_loss'], -df['Profit'], 0.0)

      lines = len(df)
      sales_total = df['Sales'].sum()
      profit_total = df['Profit'].sum()
      loss_lines = df['is_loss'].sum()
      
      profitability_summary = pd.DataFrame([{
         'lines': lines,
         'orders': df['Order ID'].nunique(),
         'sales': sales_total,
         'profit': profit_total,
         'profit_margin': profit_total / sales_total if sales_total else 0.0,
         'loss_lines': loss_lines,
         'loss_line_rate': loss_lines / lines if lines else 0.0,
         'lost_profit': df['lost_profit_val'].sum()
      }])

      conditions = [
         df['Discount'] == 0,
         (df['Discount'] > 0) & (df['Discount'] <= 0.05),
         (df['Discount'] > 0.05) & (df['Discount'] <= 0.10),
         df['Discount'] > 0.10
      ]
      choices = ['0%', '1%-5%', '6%-10%', 'más de 10%']
      df['discount_band'] = pd.Categorical(np.select(conditions, choices), categories=choices, ordered=True)

      disc_grp = df.groupby('discount_band', observed=False).agg(
         lines=('Order ID', 'count'),
         sales=('Sales', 'sum'),
         profit=('Profit', 'sum'),
         loss_lines=('is_loss', 'sum'),
         lost_profit=('lost_profit_val', 'sum')
      ).reset_index()
      
      disc_grp['profit_margin'] = disc_grp['profit'] / disc_grp['sales']
      disc_grp['loss_line_rate'] = disc_grp['loss_lines'] / disc_grp['lines']
      
      discount_summary = disc_grp[[
         'discount_band', 'lines', 'sales', 'profit', 'profit_margin', 'loss_line_rate', 'lost_profit'
      ]]

      # Segmentos prioritarios (Customer Segment + Product Category)
      seg_grp = df.groupby(['Customer Segment', 'Product Category']).agg(
         lines=('Order ID', 'count'),
         sales=('Sales', 'sum'),
         profit=('Profit', 'sum'),
         lost_profit=('lost_profit_val', 'sum')
      ).reset_index()

      # Filtrar, calcular margen y ordenar
      seg_grp = seg_grp[seg_grp['lines'] >= 100].copy()
      seg_grp['profit_margin'] = seg_grp['profit'] / seg_grp['sales']
      seg_grp = seg_grp.sort_values(by='lost_profit', ascending=False).head(5)
      
      priority_segments = seg_grp[[
         'Customer Segment', 'Product Category', 'lines', 'sales', 'profit', 'profit_margin', 'lost_profit'
      ]]

      os.makedirs('submission', exist_ok=True)
      profitability_summary.to_csv('submission/profitability_summary.csv', index=False)
      discount_summary.to_csv('submission/discount_summary.csv', index=False)
      priority_segments.to_csv('submission/priority_segments.csv', index=False)

      return profitability_summary, discount_summary, priority_segments