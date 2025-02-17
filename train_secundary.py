from ultralytics import YOLO

model = YOLO("yolov8n.pt") 

# Entrenar el modelo con el dataset personalizado
model.train(data="/content/gdrive/MyDrive/entrenamiento_deteccion_secundario/data_secundary.yaml", epochs=200, batch=16)
model.save("/content/gdrive/MyDrive/entrenamiento_deteccion_secundario/modelo_palabras_checks.pt")
