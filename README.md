# GameRAG - Plataforma NoSQL de Lore y Guías de Videojuegos

Proyecto para el curso de Bases de Datos NoSQL.

## Configuración del entorno
1. Crear un entorno virtual e instalar dependencias:
   pip install -r requirements.txt
2. Configurar las credenciales de MongoDB Atlas en `.env`, por ejemplo:
   `MONGO_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>/`
   También se puede definir `DB_NAME`; por defecto se usa `catalogo_videojuegos`.
3. Ejecutar el script de inicialización:
   python scripts/init_db.py