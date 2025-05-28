from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import face_recognition as fr
import cv2
import numpy as np
import os
from typing import List, Dict
import json

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio donde se almacenan las imágenes de referencia
REFERENCE_DIR = "Personas_Autorizadas"

def load_reference_images() -> Dict[str, np.ndarray]:
    """Carga todas las imágenes de referencia y sus encodings."""
    reference_encodings = {}
    
    for filename in os.listdir(REFERENCE_DIR):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(REFERENCE_DIR, filename)
            image = fr.load_image_file(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Obtener el encoding de la cara
            face_locations = fr.face_locations(image)
            if face_locations:
                face_encoding = fr.face_encodings(image, face_locations)[0]
                reference_encodings[filename] = face_encoding
    
    return reference_encodings

@app.post("/compare")
async def compare_faces(dni: UploadFile = File(...), selfie: UploadFile = File(...)):
    """
    Compara la cara de la foto del DNI con la de la selfie.
    """
    try:
        # Leer la imagen del DNI
        dni_contents = await dni.read()
        dni_nparr = np.frombuffer(dni_contents, np.uint8)
        dni_img = cv2.imdecode(dni_nparr, cv2.IMREAD_COLOR)
        if dni_img is None:
            return {"error": "No se pudo decodificar la imagen del DNI"}
        dni_img = cv2.cvtColor(dni_img, cv2.COLOR_BGR2RGB)

        # Leer la imagen de la selfie
        selfie_contents = await selfie.read()
        selfie_nparr = np.frombuffer(selfie_contents, np.uint8)
        selfie_img = cv2.imdecode(selfie_nparr, cv2.IMREAD_COLOR)
        if selfie_img is None:
            return {"error": "No se pudo decodificar la imagen de la selfie"}
        selfie_img = cv2.cvtColor(selfie_img, cv2.COLOR_BGR2RGB)

        # Asegurarse de que las imágenes sean de 8 bits
        dni_img = dni_img.astype(np.uint8)
        selfie_img = selfie_img.astype(np.uint8)

        # Detectar cara en la imagen del DNI
        dni_face_locations = fr.face_locations(dni_img)
        if not dni_face_locations:
            return {"error": "No se detectó ninguna cara en la imagen del DNI"}
        dni_face_encoding = fr.face_encodings(dni_img, dni_face_locations)[0]

        # Detectar cara en la selfie
        selfie_face_locations = fr.face_locations(selfie_img)
        if not selfie_face_locations:
            return {"error": "No se detectó ninguna cara en la selfie"}
        selfie_face_encoding = fr.face_encodings(selfie_img, selfie_face_locations)[0]

        # Comparar las dos caras
        result = fr.compare_faces([dni_face_encoding], selfie_face_encoding, tolerance=0.6)[0]
        distance = fr.face_distance([dni_face_encoding], selfie_face_encoding)[0]

        return {
            "match": bool(result),
            "distance": float(distance)
        }
    except Exception as e:
        return {"error": f"Error al procesar las imágenes: {str(e)}"}

@app.get("/reference-images")
async def get_reference_images():
    """Obtiene la lista de imágenes de referencia disponibles."""
    images = []
    for filename in os.listdir(REFERENCE_DIR):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            images.append(filename)
    return {"images": images} 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 