from ultralytics import YOLO
# Entrenamiento en Colab

model = YOLO("yolov8n.pt") 
# Entrenar el modelo con el dataset personalizado
model.train(data="/content/gdrive/MyDrive/entrenamiento_modelo_primario/sn_id_genero.pt/data_primary.yaml", epochs=200, batch=16)

model.save(r'/content/gdrive/MyDrive/entrenamiento_modelo_primario/sn_id_genero.pt')
