# data/populate_db.py
import sys
import os

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db
from models import TipoDocumento, Cliente, Compra
from datetime import datetime, timedelta
import random

def limpiar_base_datos():
    """Limpia todas las tablas"""
    with app.app_context():
        Compra.query.delete()
        Cliente.query.delete()
        TipoDocumento.query.delete()
        db.session.commit()
        print("✅ Base de datos limpiada")


def poblar_tipos_documento():
    """Crea los tipos de documento"""
    with app.app_context():
        tipos = [
            TipoDocumento(codigo='CC', descripcion='Cédula de Ciudadanía'),
            TipoDocumento(codigo='NIT', descripcion='NIT'),
            TipoDocumento(codigo='PA', descripcion='Pasaporte')
        ]
        db.session.add_all(tipos)
        db.session.commit()
        print("✅ Tipos de documento creados")


def poblar_clientes():
    """Crea clientes de prueba"""
    with app.app_context():
        # Obtener tipos de documento
        tipo_cc = TipoDocumento.query.filter_by(codigo='CC').first()
        tipo_nit = TipoDocumento.query.filter_by(codigo='NIT').first()
        tipo_pa = TipoDocumento.query.filter_by(codigo='PA').first()
        
        clientes = [
            # Clientes que superarán los 5M (para fidelización)
            Cliente(
                tipo_documento_id=tipo_cc.id,
                numero_documento='1234567890',
                nombre='Juan',
                apellido='Pérez García',
                correo='juan.perez@email.com',
                telefono='3101234567',
                fecha_registro=datetime.now() - timedelta(days=180)
            ),
            Cliente(
                tipo_documento_id=tipo_cc.id,
                numero_documento='9876543210',
                nombre='María',
                apellido='González López',
                correo='maria.gonzalez@email.com',
                telefono='3109876543',
                fecha_registro=datetime.now() - timedelta(days=150)
            ),
            Cliente(
                tipo_documento_id=tipo_nit.id,
                numero_documento='900123456-1',
                nombre='Distribuidora',
                apellido='El Éxito SAS',
                correo='compras@exito.com',
                telefono='6012345678',
                fecha_registro=datetime.now() - timedelta(days=365)
            ),
            
            # Clientes con compras menores (no califican para fidelización)
            Cliente(
                tipo_documento_id=tipo_cc.id,
                numero_documento='1122334455',
                nombre='Carlos',
                apellido='Rodríguez Méndez',
                correo='carlos.rodriguez@email.com',
                telefono='3201122334',
                fecha_registro=datetime.now() - timedelta(days=90)
            ),
            Cliente(
                tipo_documento_id=tipo_pa.id,
                numero_documento='AB123456',
                nombre='John',
                apellido='Smith',
                correo='john.smith@email.com',
                telefono='3157890123',
                fecha_registro=datetime.now() - timedelta(days=60)
            ),
            Cliente(
                tipo_documento_id=tipo_cc.id,
                numero_documento='5566778899',
                nombre='Ana',
                apellido='Martínez Silva',
                correo='ana.martinez@email.com',
                telefono='3145566778',
                fecha_registro=datetime.now() - timedelta(days=120)
            ),
            
            # Cliente con compras antiguas (no califican por fecha)
            Cliente(
                tipo_documento_id=tipo_cc.id,
                numero_documento='4455667788',
                nombre='Luis',
                apellido='Ramírez Torres',
                correo='luis.ramirez@email.com',
                telefono='3194455667',
                fecha_registro=datetime.now() - timedelta(days=200)
            ),
        ]
        
        db.session.add_all(clientes)
        db.session.commit()
        print(f"✅ {len(clientes)} clientes creados")
        
        return clientes


def poblar_compras():
    """Crea compras de prueba"""
    with app.app_context():
        clientes = Cliente.query.all()
        
        productos = [
            'Laptop Dell Inspiron 15',
            'iPhone 14 Pro Max',
            'Samsung Galaxy S23',
            'Smart TV LG 55"',
            'PlayStation 5',
            'Xbox Series X',
            'iPad Air',
            'MacBook Pro',
            'AirPods Pro',
            'Nintendo Switch',
            'Monitor Samsung 27"',
            'Teclado Mecánico Logitech',
            'Mouse Gamer Razer',
            'Impresora HP LaserJet',
            'Cámara Canon EOS',
            'Audífonos Sony WH-1000XM5',
            'Tablet Samsung Galaxy Tab',
            'Smartwatch Apple Watch',
            'Refrigerador LG',
            'Lavadora Samsung'
        ]
        
        compras = []
        
        # Cliente 1: Juan Pérez (superará los 5M en último mes)
        cliente1 = Cliente.query.filter_by(numero_documento='1234567890').first()
        for i in range(8):
            compra = Compra(
                cliente_id=cliente1.id,
                fecha_compra=datetime.now() - timedelta(days=random.randint(1, 25)),
                monto=random.uniform(800_000, 1_200_000),
                descripcion=random.choice(productos),
                numero_factura=f'FC-2024-{1000 + i}'
            )
            compras.append(compra)
        
        # Cliente 2: María González (superará los 5M en último mes)
        cliente2 = Cliente.query.filter_by(numero_documento='9876543210').first()
        for i in range(6):
            compra = Compra(
                cliente_id=cliente2.id,
                fecha_compra=datetime.now() - timedelta(days=random.randint(1, 28)),
                monto=random.uniform(1_000_000, 1_500_000),
                descripcion=random.choice(productos),
                numero_factura=f'FC-2024-{2000 + i}'
            )
            compras.append(compra)
        
        # Cliente 3: Distribuidora El Éxito (superará los 5M en último mes)
        cliente3 = Cliente.query.filter_by(numero_documento='900123456-1').first()
        for i in range(4):
            compra = Compra(
                cliente_id=cliente3.id,
                fecha_compra=datetime.now() - timedelta(days=random.randint(5, 20)),
                monto=random.uniform(2_000_000, 3_500_000),
                descripcion=f'Lote de {random.choice(productos)}',
                numero_factura=f'FC-2024-{3000 + i}'
            )
            compras.append(compra)
        
        # Cliente 4: Carlos Rodríguez (NO superará los 5M)
        cliente4 = Cliente.query.filter_by(numero_documento='1122334455').first()
        for i in range(3):
            compra = Compra(
                cliente_id=cliente4.id,
                fecha_compra=datetime.now() - timedelta(days=random.randint(1, 25)),
                monto=random.uniform(500_000, 900_000),
                descripcion=random.choice(productos),
                numero_factura=f'FC-2024-{4000 + i}'
            )
            compras.append(compra)
        
        # Cliente 5: John Smith (NO superará los 5M)
        cliente5 = Cliente.query.filter_by(numero_documento='AB123456').first()
        for i in range(2):
            compra = Compra(
                cliente_id=cliente5.id,
                fecha_compra=datetime.now() - timedelta(days=random.randint(5, 20)),
                monto=random.uniform(300_000, 700_000),
                descripcion=random.choice(productos),
                numero_factura=f'FC-2024-{5000 + i}'
            )
            compras.append(compra)
        
        # Cliente 6: Ana Martínez (compras moderadas)
        cliente6 = Cliente.query.filter_by(numero_documento='5566778899').first()
        for i in range(4):
            compra = Compra(
                cliente_id=cliente6.id,
                fecha_compra=datetime.now() - timedelta(days=random.randint(2, 28)),
                monto=random.uniform(600_000, 1_000_000),
                descripcion=random.choice(productos),
                numero_factura=f'FC-2024-{6000 + i}'
            )
            compras.append(compra)
        
        # Cliente 7: Luis Ramírez (compras ANTIGUAS, NO califican por fecha)
        cliente7 = Cliente.query.filter_by(numero_documento='4455667788').first()
        for i in range(10):
            compra = Compra(
                cliente_id=cliente7.id,
                fecha_compra=datetime.now() - timedelta(days=random.randint(35, 120)),
                monto=random.uniform(800_000, 1_500_000),
                descripcion=random.choice(productos),
                numero_factura=f'FC-2024-{7000 + i}'
            )
            compras.append(compra)
        
        db.session.add_all(compras)
        db.session.commit()
        print(f"✅ {len(compras)} compras creadas")


def mostrar_resumen():
    """Muestra un resumen de los datos creados"""
    with app.app_context():
        print("\n" + "="*60)
        print("📊 RESUMEN DE DATOS DE PRUEBA")
        print("="*60)
        
        clientes = Cliente.query.all()
        print(f"\n👥 Total de clientes: {len(clientes)}")
        
        fecha_limite = datetime.now() - timedelta(days=30)
        
        for cliente in clientes:
            compras_recientes = [c for c in cliente.compras if c.fecha_compra >= fecha_limite]
            total_reciente = sum(c.monto for c in compras_recientes)
            
            print(f"\n  • {cliente.nombre} {cliente.apellido}")
            print(f"    Doc: {cliente.numero_documento}")
            print(f"    Compras (último mes): {len(compras_recientes)}")
            print(f"    Total (último mes): ${total_reciente:,.2f} COP")
            
            if total_reciente > 5_000_000:
                print(f"    ✅ CALIFICA para fidelización")
            else:
                print(f"    ❌ NO califica para fidelización")
        
        print("\n" + "="*60)


if __name__ == '__main__':
    print(" Iniciando población de base de datos...")
    print("\n ADVERTENCIA: Esto eliminará todos los datos existentes")
    respuesta = input("¿Desea continuar? (s/n): ")
    
    if respuesta.lower() == 's':
        limpiar_base_datos()
        poblar_tipos_documento()
        poblar_clientes()
        poblar_compras()
        mostrar_resumen()
        print("\n✅ ¡Base de datos poblada exitosamente!")
    else:
        print("\n❌ Operación cancelada")