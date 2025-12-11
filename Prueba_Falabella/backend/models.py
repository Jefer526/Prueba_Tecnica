# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TipoDocumento(db.Model):
    __tablename__ = 'tipo_documento'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)  # NIT, CC, PA
    descripcion = db.Column(db.String(50), nullable=False)  # Cedula, Pasaporte, etc.
    
    # Relación
    clientes = db.relationship('Cliente', backref='tipo_documento', lazy=True)
    
    def __repr__(self):
        return f'<TipoDocumento {self.codigo}>'


class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento_id = db.Column(db.Integer, db.ForeignKey('tipo_documento.id'), nullable=False)
    numero_documento = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    compras = db.relationship('Compra', backref='cliente', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo_documento': self.tipo_documento.descripcion,
            'numero_documento': self.numero_documento,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'correo': self.correo,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d')
        }
    
    def __repr__(self):
        return f'<Cliente {self.nombre} {self.apellido}>'


class Compra(db.Model):
    __tablename__ = 'compra'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha_compra = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(200))
    numero_factura = db.Column(db.String(50), unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha_compra': self.fecha_compra.strftime('%Y-%m-%d %H:%M:%S'),
            'monto': self.monto,
            'descripcion': self.descripcion,
            'numero_factura': self.numero_factura
        }
    
    def __repr__(self):
        return f'<Compra {self.numero_factura}>'