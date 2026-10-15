import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, TEXT

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["catalogo_videojuegos"]

#validacion shema
esquemas = {
    "documentos": {
        "bsonType": "object",
        "required": ["titulo", "idioma", "fecha", "contenido_texto", "metadatos"],
        "properties": {
            "titulo": {"bsonType": "string", "minLength": 1},
            "idioma": {"enum": ["es", "en"]},
            "fecha": {"bsonType": "date"},
            "contenido_texto": {"bsonType": "string", "minLength": 1},
            "metadatos": {"bsonType": "object"},
            "imagenes": {"bsonType": "array", "items": {"bsonType": "objectId"}},
        },
    },
    "chunks": {
        "bsonType": "object",
        "required": ["doc_id", "chunk_index", "estrategia_chunking",
                     "chunk_texto", "embedding", "modelo"],
        "properties": {
            "doc_id": {"bsonType": "objectId"},
            "chunk_index": {"bsonType": "int", "minimum": 0},
            "estrategia_chunking": {"enum": ["fixed-size", "sentence-aware", "semantic"]},
            "chunk_texto": {"bsonType": "string", "minLength": 1},
            "embedding": {"bsonType": "array", "minItems": 384, "maxItems": 384},
            "modelo": {"bsonType": "string"},
        },
    },
}

existentes = db.list_collection_names()

for nombre, esquema in esquemas.items():
    if nombre not in existentes:
        db.create_collection(
            nombre,
            validator={"$jsonSchema": esquema},
            validationLevel="strict",
            validationAction="error",
        )
        print(f"Colección creada: {nombre}")
    else:
        print(f"Ya existe: {nombre}")

# indices 
db.documentos.create_index([("fecha", ASCENDING), ("idioma", ASCENDING)], name="idx_fecha_idioma")
db.documentos.create_index([("contenido_texto", TEXT)], name="idx_texto")
db.chunks.create_index([("doc_id", ASCENDING), ("estrategia_chunking", ASCENDING)], name="idx_doc_estrategia")
db.imagenes.create_index("doc_id", name="idx_doc_id")
db.empresas.create_index("nombre", unique=True, name="idx_nombre")
db.documentos.create_index("metadatos.empresas_ids", name="idx_empresas")
db.usuarios.create_index("correo", unique=True, name="idx_correo")
print("Índices creados")