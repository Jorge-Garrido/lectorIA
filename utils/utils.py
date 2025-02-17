import os
import numpy as np
import pandas as pd
import cv2
import fitz
from PIL import Image

def add_count(df):
    """Crear una columna que sirva de contador para los IDS de los movimientos"""
    df['ID_CONTEO'] = range(1, len(df) + 1)
    return df

def columnas(df):
  df = df.groupby(['clase_casilla']).apply(add_count)#.reset_index(drop=True)
  df['columnas'] = df['clase_casilla'] + df['ID_CONTEO'].map(str)+'_P'+df['pagina'].map(str)
  df = df.sort_values(by=['pagina','Y1','X1'])
  return df

# Obtener las preguntas con un OCR para la validacion
# En esto faltaria la validacion por numero de casillas
def validacion_doc_digitales(df,tipo_doc):
  df_aux = pd.DataFrame()
  preguntas = []
  respuesta = []
  rows = []
  anomalia = 'NO'
  for i  in range(0,len(df)):
    respuesta.append(int(''.join(map(str, df['respuesta'][i]))))
    tipo = df['clase_casilla'][i]
    if tipo == 'id':
      if respuesta[i] in tipo_doc['REEMPLAZOS_CLS'].keys():
        rows.append(tipo_doc['REEMPLAZOS_CLS'][respuesta[i]])
      elif df['ocr_izquierda'][i][0].upper() in tipo_doc['VALIDACION_OCR'][tipo] and df['ocr_derecha'][i][0].upper() in tipo_doc['VALIDACION_OCR'][tipo]:
        rows.append([f"{df['ocr_izquierda'][i][0]}".lower(),f"{df['ocr_derecha'][i][0]}".lower()])
      elif df['ocr_izquierda'][i][0].upper() in tipo_doc['VALIDACION_OCR'][tipo]:
        rows.append(df['ocr_izquierda'][i][0])
      elif df['ocr_derecha'][i][0].upper() in tipo_doc['VALIDACION_OCR'][tipo]:
        rows.append(f"--{df['ocr_derecha'][i][0]}")
      else:
        rows.append((df['Y1'][i],df['Y2'][i],df['X1'][i],df['X2'][i]))
        anomalia = 'SI'
    else:
      if df['ocr_izquierda'][i] in tipo_doc['VALIDACION_OCR'][tipo]:
        rows.append(df['ocr_izquierda'][i])
      elif df['ocr_derecha'][i] in tipo_doc['VALIDACION_OCR'][tipo]:
        rows.append(f"--{df['ocr_derecha'][i]}")
      elif respuesta[i] in tipo_doc['REEMPLAZOS_CLS'].values():
        rows.append(df['respuesta'][i])
      else:
        rows.append((df['Y1'][i],df['Y2'][i],df['X1'][i],df['X2'][i]))
        anomalia = 'SI'
  df_auxiliar = pd.DataFrame(columns=df['columnas'].tolist())
  df_auxiliar.loc[len(df_auxiliar)] = rows
  df_auxiliar['DOCUMENTO'] = df['documento'][0]
  df_auxiliar['ANOMALIA'] = anomalia
  return df_auxiliar


def creador_dfs(referencias:dict):
  dfs_finales = []
  for (key,doc) in referencias.items():
      str_nombre = f"{referencias[key]}_df"
      globals()[str_nombre] = pd.DataFrame()
      dfs_finales.append(globals()[str_nombre])
  return dfs_finales

def pdf_a_imagen(filename, tipo_doc):
  imagenes=[]
  numero_paginas = len(tipo_doc['PAGINAS'].keys())
  doc = fitz.open(pdf_path)
  npag = 'pagina'
  n = 1
  for npagina in range(numero_paginas):
    nom_pagina = f"{npag}{n}"
    globals()[nom_pagina] = doc.load
