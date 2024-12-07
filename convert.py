from ultralytics import YOLO

model = YOLO("best.pt")
model.export(format="onnx")  # This will export the model to ONNX format
