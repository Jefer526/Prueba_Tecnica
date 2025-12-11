# backend/config.py
import os

class Config:
    # Configuración de la base de datos SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-falabella-2024'
    
    # Configuración CORS para permitir peticiones del frontend
    CORS_HEADERS = 'Content-Type'
    
    # Configuración de archivos de exportación
    EXPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'exports')
    
    @staticmethod
    def init_app(app):
        # Crear carpeta de exportaciones si no existe
        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)