import os
from io import StringIO
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, TEXT

env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.is_file():
    env_lines = []
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip().lower() == "mongo_uri":
            line = f"{key.strip()}={value.strip()}"
        env_lines.append(line)
    load_dotenv(stream=StringIO("\n".join(env_lines)))
else:
    load_dotenv()

# Conexión a MongoDB Atlas mediante la variable de entorno
mongo_uri = os.getenv("MONGO_URI") or os.getenv("mongo_uri")
if not mongo_uri:
    raise ValueError("ERROR: Configura MONGO_URI en el archivo .env (MONGO_URI=...)")

client = MongoClient(mongo_uri)
db_name = os.getenv("DB_NAME", "catalogo_videojuegos")
db = client[db_name]

print(f"Conectado exitosamente a la base de datos: '{db_name}'")

# Definición de esquemas de validación ($jsonSchema)
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
        "required": ["doc_id", "chunk_index", "estrategia_chunking", "chunk_texto", "embedding", "modelo"],
        "properties": {
            "doc_id": {"bsonType": "objectId"},
            "chunk_index": {"bsonType": "int", "minimum": 0},
            "estrategia_chunking": {"enum": ["fixed-size", "sentence-aware", "semantic"]},
            "chunk_texto": {"bsonType": "string", "minLength": 1},
            "embedding": {"bsonType": "array", "minItems": 384, "maxItems": 384},
            "modelo": {"bsonType": "string"},
        },
    },
    "imagenes": {
        "bsonType": "object",
        "required": ["doc_id", "ruta_archivo", "embedding", "modelo"],
        "properties": {
            "doc_id": {"bsonType": "objectId"},
            "ruta_archivo": {"bsonType": "string"},
            "descripcion": {"bsonType": "string"},
            "etiquetas": {"bsonType": "array", "items": {"bsonType": "string"}},
            "embedding": {"bsonType": "array", "minItems": 512, "maxItems": 512},
            "modelo": {"bsonType": "string"}
        }
    },
    "usuarios": {
        "bsonType": "object",
        "required": ["nombre", "correo", "historial_consultas"],
        "properties": {
            "nombre": {"bsonType": "string"},
            "correo": {"bsonType": "string"},
            "historial_consultas": {"bsonType": "array"}
        }
    }
}

# Creación de colecciones con $jsonSchema
existentes = db.list_collection_names()

for nombre, esquema in esquemas.items():
    if nombre not in existentes:
        db.create_collection(
            nombre,
            validator={"$jsonSchema": esquema},
            validationLevel="strict",
            validationAction="error",
        )
        print(f"Colección creada con éxito: {nombre}")
    else:
        print(f"La colección ya existe: {nombre}")

# Creación de Índices
print("\nCreando índices...")
db.documentos.create_index([("fecha", ASCENDING), ("idioma", ASCENDING)], name="idx_fecha_idioma")
db.documentos.create_index([("contenido_texto", TEXT)], name="idx_texto")
db.chunks.create_index([("doc_id", ASCENDING), ("estrategia_chunking", ASCENDING)], name="idx_doc_estrategia")
db.imagenes.create_index("doc_id", name="idx_doc_id")
db.usuarios.create_index("correo", unique=True, name="idx_correo")

print(" Todos los índices han sido creados correctamente.")