from ultralytics import YOLO
import os
import numpy as np
import pandas as pd
import cv2
import fitz
from PIL import Image
import pytesseract
from pypdf import PdfReader
import time
from utils import utils

nic_2 = {'PAGINAS':{'PAGINA 1':['id','genero','sn'],
                    'PAGINA 2':['sn']},
          'PREGUNTAS':['TIPO_ID', 'Género:', 'PEP 1', 'PEP 2', 'PEP 3', 'PEP 4', 'PEP 5','PERSONA_NATURAL_NEGOCIO', 'OPERACIONES_INT','FATCA 1', 'FATCA 2', 'CRS 1'],
         'VALIDACION_OCR':{'sn':['Sí','No','VACIO'],
                       'id':['C','T','R','N','P'], # PARA LAS CASILLAS DE DOCUMENTO ES MEJOR DEJAR SOLO LA PRIMERA LETRA
                       'genero':['F','M']},
         'REEMPLAZOS_CLS':{10111111: 'C.C',
                           11011111: 'T.I',
                           11101111: 'R.C',
                           11110111: 'C.E',
                           11111011: 'NIT',
                           11111101: 'PS',
                           11111110: 'C.D',
                           110:'No',
                           101:'Sí'}
         }

nic_7 = {'PAGINAS':{'PAGINA 1':['id','genero','sn'],
                    'PAGINA 2':['sn']},
        'PREGUNTAS':['TIPO_ID', 'Género:','PEP 1','PERSONA_NATURAL_NEGOCIO', 'OPERACIONES_INT','FATCA','CRS'],
        'VALIDACION_OCR':{'sn':['Sí','No','VACIO'],
                       'id':['C','T','R','N'], # PARA LAS CASILLAS DE DOCUMENTO ES MEJOR DEJAR SOLO LA PRIMERA LETRA
                       'genero':['F','M']},
         'REEMPLAZOS_CLS':{1011111: 'C.C',
                           1101111: 'T.I',
                           1110111: 'R.C',
                           1111011: 'C.E',
                           1111101: 'NIT',
                           1111110: 'C.D',
                           110:'No',
                           101:'Sí'}

}

nic_9 = {'PREGUNTAS':['TIPO_ID', 'Género:', 'PEP 1', 'PEP 2', 'PEP 3', 'PEP 4', 'PEP 5','PEP 6','PERSONA_NATURAL_NEGOCIO', 'OPERACIONES_INT','FATCA','CRS'],
    'VALIDACION_OCR':{'sn':['Sí','No','VACIO'],
                       'id':['C','T','R','N','P'], # PARA LAS CASILLAS DE DOCUMENTO ES MEJOR DEJAR SOLO LA PRIMERA LETRA
                       'genero':['F','M']},
         'REEMPLAZOS_CLS':{10111111: 'C.C',
                           11011111: 'T.I',
                           11101111: 'R.C',
                           11110111: 'C.E',
                           11111011: 'NIT',
                           11111101: 'PSP',
                           11111110: 'C.D',
                           110:'No',
                           101:'Sí'}}

referencias = {'Acrobat Reader  o similar (no lo diligencie desde el navegador)' : 'nic_2',
              'INFORMACIÓN ECONÓMICA\nINFORMACIÓN FINANCIERA':'nic_7',
              'ENTREVISTA\n¿Cliente PEP?':'nic_9'}

checks = {'Acrobat Reader  o similar (no lo diligencie desde el navegador)' : nic_2,
          'INFORMACIÓN ECONÓMICA\nINFORMACIÓN FINANCIERA':nic_7,
              'ENTREVISTA\n¿Cliente PEP?':nic_9}




### MAIN LOOP ##################
dfss = creador_dfs(referencias)
start_time_global = time.time()
modelo_primario = YOLO(r'/content/gdrive/MyDrive/entrenamiento_modelo_primario/sn_id_genero.pt')
# Modelo 2
modelo_secundario = YOLO(r"/content/gdrive/MyDrive/entrenamiento_deteccion_secundario/modelo_palabras_checks.pt")
resultados =  '/content/resultados'
os.makedirs(resultados, exist_ok=True)
# se crea el excel writer
workbook1 = xlsxwriter.Workbook('si_no.xlsx')
worksheet1 = workbook1.add_worksheet()
# se declaran las rutas de las carpetas en donde esten guardadas las imagenes
carpeta_documentos = r'/content/gdrive/MyDrive/VALIDACION PEP/PRUEBA'
# se itera a traves de la carpeta imagenes
df_final = pd.DataFrame()
contador_files=0
contador_roi=0
for filename in os.listdir(carpeta_documentos):
    print(filename)
    print("******************************************")
    df = pd.DataFrame() # df se inicializa para cada documento
  # se inicializan los contadores para el control de casillas
    numero_id = 0
    numero_sn = 0
    genero = 0
  # se crea una carpeta individual para remplazar los documentos
    carpeta_individual = os.path.join(resultados,filename.replace('.pdf',""))
  # se crea la ruta para cada pdf
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(carpeta_documentos, filename)
        # Parte en la que se trabaja con texto, aca tiene que ser la validacion inicial de parametros
        reader = PdfReader(pdf_path)
        pagina1 = reader.pages[0]
        pagina2 = reader.pages[1]
        texto = pagina1.extract_text() + pagina2.extract_text()
        # Preprocesamiento : se quitan los espacios antes y despues de las oraciones
        texto = texto.split('\n')
        texto = [oracion.strip() for oracion in texto]
        texto = '\n'.join(texto)
        for key in checks.keys():
          if key in texto:
            # Aca se clasifica el documento con el diccionario de checks
            tipo_doc = checks[key]
            nombre_doc = referencias[key]
          else: pass
        # Aca se puede hacer el control de casillas
        doc = fitz.open(pdf_path)
        pagina1 = doc.load_page(0)
        pagina2 = doc.load_page(1)
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix1 = pagina1.get_pixmap(matrix=mat)
        pix2 = pagina2.get_pixmap(matrix=mat)
        img1 = Image.frombytes("RGB", \
                        [pix1.width, pix1.height], \
                        pix1.samples)
        img1 = img1.convert('L')
        imagen1 = np.array(img1)
        cv2.imwrite('imagen1.jpg',imagen1)
        img2 = Image.frombytes("RGB", \
                        [pix2.width, pix2.height], \
                        pix2.samples)
        img2 = img2.convert('L')
        imagen2 = np.array(img2)
        cv2.imwrite('imagen2.jpg',imagen2)
        # aca se evaluaria la primera imagen con el modelo de clasificaicon de deep learning
        imagenes = ['imagen1','imagen2']
        n=1
        for imagen in imagenes:
          # se lee la imagen con opencv
          imagen_lect = cv2.imread(f'{imagen}.jpg')
          # se ejecuta el primer modelo primero en la pagina 1 y en la segunda iteracion del loop para la pagina2
          resultados1 = modelo_primario(f'{imagen}.jpg')
          # se guardan las clases (pagina1 y pagina2)
          clases_primarias = resultados1[0].boxes.cls # opcional
          # control de numero de casillas para el control se pueden armar diccionarios y aqui poner un condicional. Recuerda que para hacer eso tienes que poder clasificar los documentos
          # tanto imagenes como digitales
          numero_id = len([i for i in resultados1[0].boxes.cls if i == 1]) + numero_id
          numero_sn = len([i for i in resultados1[0].boxes.cls if i == 0]) + numero_sn
          genero = len([i for i in resultados1[0].boxes.cls if i == 2]) + genero
          # se itera a traves de las detecciones de cada una de las imagenes. el ennumerate es para encontral el indice del recorte en las clases
          # es decir para ver si es id, que saque la posicion de id en las clases del modelo primario
          dict = {}
          # aca iba lo de poner las casillas en fotos
          for idx,det in enumerate(resultados1[0].boxes):
            # posicion y clase del recorte en primer nivel(si_no, id, genero)
            cajas = det.xyxy.cpu().numpy()
            X1,Y1,X2,Y2 = [int(i) for i in cajas[0]]
            roi = imagen_lect[Y1:Y2, X1:X2]
            a = roi.copy()
            clase_recorte = resultados1[0].names[int(det.cls.item())]
            dict['X1'],dict['Y1'],dict['X2'],dict['Y2'],dict['clase_casilla'] = X1,Y1,X2,Y2,str(clase_recorte)
            resultados2 = modelo_secundario(roi)
            # lo siguiente que se puede ocurrir es iterar a traves de las cajas y hacer una tupla de clase, coordenadas y luego organizar dada las coordenadas
            dict2 = {}
            df_mini = pd.DataFrame()
            if resultados2[0].boxes.data.tolist() != []:
              for dete in resultados2[0].boxes:
                cajas2 =  dete.xyxy.cpu().numpy()
                clase_recorte2 = dete.cls.item()
                x1,y1,x2,y2 = [int(i) for i in cajas2[0]]
                dict2['x1'],dict2['y1'],dict2['x2'],dict2['y2'],dict2['clase'] = x1,y1,x2,y2,clase_recorte2
                if len(dict2) == 0:
                  dict2['x1'],dict2['y1'],dict2['x2'],dict2['y2'],dict2['clase'] = 'NO RECORTE','NO RECORTE','NO RECORTE','NO RECORTE','NO RECORTE'
                df_mini = pd.concat([df_mini,pd.DataFrame([dict2])] ,ignore_index=True)
              cv2.imwrite(os.path.join(carpeta_individual,f'{filename.replace(".pdf","")}_{n}.jpg'), a)
              n = n+1
              # Se obtiene la clase del tensor
              df_mini = df_mini.sort_values(by=['x1']).reset_index().drop('index', axis='columns')
              respuesta = [int(i) for i in df_mini['clase']]
              largo_casilla = len(respuesta) - 1
              # si se encontro un check:
              if 0 in respuesta:
                respuesta_casilla = respuesta.index(0)
                if respuesta_casilla == 0:
                  ocr_row_derecha = df_mini[df_mini['clase']==0].index[0]+1
                  ocr_imagen_derecha =  roi[df_mini['y1'][ocr_row_derecha]:df_mini['y2'][ocr_row_derecha],df_mini['x1'][ocr_row_derecha]:df_mini['x2'][ocr_row_derecha]]
                  r_d = pytesseract.image_to_string(cv2.resize(ocr_imagen_derecha, (50,50), interpolation= cv2.INTER_LINEAR), lang='spa',config='--psm 8').replace("\n"," ").strip()
                  dict['ocr_derecha'] = r_d
                elif respuesta_casilla == len(respuesta)-1:
                  ocr_row_izquierda=df_mini[df_mini['clase']==0].index[0]-1
                  ocr_imagen_izquierda =  roi[df_mini['y1'][ocr_row_izquierda]:df_mini['y2'][ocr_row_izquierda],df_mini['x1'][ocr_row_izquierda]:df_mini['x2'][ocr_row_izquierda]]
                  dict['ocr_derecha'] = 'NE'
                  r_i = pytesseract.image_to_string(cv2.resize(ocr_imagen_izquierda, (80,80), interpolation= cv2.INTER_LINEAR), lang='spa',config='--psm 8').replace("\n"," ").strip()
                  dict['ocr_izquierda'] = r_i
                else:
                  ocr_row_izquierda=df_mini[df_mini['clase']==0].index[0]-1
                  ocr_imagen_izquierda =  roi[df_mini['y1'][ocr_row_izquierda]:df_mini['y2'][ocr_row_izquierda],df_mini['x1'][ocr_row_izquierda]:df_mini['x2'][ocr_row_izquierda]]
                  ocr_row_derecha = df_mini[df_mini['clase']==0].index[0]+1
                  ocr_imagen_derecha =  roi[df_mini['y1'][ocr_row_derecha]:df_mini['y2'][ocr_row_derecha],df_mini['x1'][ocr_row_derecha]:df_mini['x2'][ocr_row_derecha]]
                  r_d = pytesseract.image_to_string(cv2.resize(ocr_imagen_derecha, (80,80), interpolation= cv2.INTER_LINEAR), lang='spa',config='--psm 8').replace("\n"," ").strip()
                  r_i = pytesseract.image_to_string(cv2.resize(ocr_imagen_izquierda, (80,80), interpolation= cv2.INTER_LINEAR), lang='spa',config='--psm 8').replace("\n"," ").strip()
                  dict['ocr_derecha'] = r_d
                  dict['ocr_izquierda'] = r_i
              else:
                dict['ocr_derecha'] = 'VACIO'
                dict['ocr_izquierda'] = 'VACIO'
              dict['respuesta'], dict['largo_casilla'], dict['documento'], dict['pagina'] = respuesta,largo_casilla, filename, int(imagen.replace("imagen", " "))
              df = pd.concat([df,pd.DataFrame([dict])] ,ignore_index=True)
              df = df.sort_values(by=['pagina','Y1','X1'])
            else:
              continue
    df = df.drop(df[(df['clase_casilla']=='id')&(df['pagina']==2)].index)
    df = df.drop(df[(df['clase_casilla']=='genero')&(df['pagina']==2)].index)
    df = df.replace(tipo_doc['REEMPLAZOS_CLS'])
    df = columnas(df)
    df_row = validacion_doc_digitales(df,tipo_doc)
    df_row['TIPO DOCUMENTO'] = nombre_doc
    # nueva forma
    nombre_df = f"{nombre_doc}_df"
    globals()[nombre_df] = pd.concat([globals()[nombre_df],df_row])
    df_final = pd.concat([df_final,df_row]).reset_index(drop=True)
### Aca toca hacer el remplazo del nombre de las columnas
### Falta aislar las que tengan detecciones
# CONTROL DE TIEMP0
end_time_global = time.time()
execution_time_global = end_time_global - start_time_global
print("Tiempo de ejecución Total:", execution_time_global, "segundos")
