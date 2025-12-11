# backend/app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from config import Config
from models import db, TipoDocumento, Cliente, Compra
from datetime import datetime, timedelta
import pandas as pd
import os

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
CORS(app)

# Inicializar carpeta de exportaciones
Config.init_app(app)


# ==================== ENDPOINT 1: Buscar Cliente ====================
@app.route('/api/buscar-cliente', methods=['POST'])
def buscar_cliente():
    """
    Busca un cliente por tipo y número de documento
    Body: {
        "tipo_documento": "CC",
        "numero_documento": "1234567890"
    }
    """
    try:
        data = request.get_json()
        tipo_doc = data.get('tipo_documento')
        numero_doc = data.get('numero_documento')
        
        if not tipo_doc or not numero_doc:
            return jsonify({
                'error': 'Debe proporcionar tipo_documento y numero_documento'
            }), 400
        
        # Buscar tipo de documento
        tipo_documento_obj = TipoDocumento.query.filter_by(codigo=tipo_doc).first()
        if not tipo_documento_obj:
            return jsonify({
                'error': f'Tipo de documento {tipo_doc} no válido'
            }), 400
        
        # Buscar cliente
        cliente = Cliente.query.filter_by(
            tipo_documento_id=tipo_documento_obj.id,
            numero_documento=numero_doc
        ).first()
        
        if not cliente:
            return jsonify({
                'error': 'Cliente no encontrado'
            }), 404
        
        # Obtener compras del cliente
        compras = [compra.to_dict() for compra in cliente.compras]
        
        # Calcular total de compras
        total_compras = sum(compra.monto for compra in cliente.compras)
        
        return jsonify({
            'cliente': cliente.to_dict(),
            'compras': compras,
            'total_compras': total_compras,
            'numero_compras': len(compras)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINT 2: Exportar Datos ====================
@app.route('/api/exportar-cliente', methods=['POST'])
def exportar_cliente():
    """
    Exporta los datos de un cliente a CSV o Excel
    Body: {
        "numero_documento": "1234567890",
        "formato": "csv" o "excel"
    }
    """
    try:
        data = request.get_json()
        numero_doc = data.get('numero_documento')
        formato = data.get('formato', 'csv').lower()
        
        if not numero_doc:
            return jsonify({'error': 'Debe proporcionar numero_documento'}), 400
        
        # Buscar cliente
        cliente = Cliente.query.filter_by(numero_documento=numero_doc).first()
        
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        
        # Preparar datos con pandas
        cliente_data = {
            'Tipo Documento': [cliente.tipo_documento.descripcion],
            'Número Documento': [cliente.numero_documento],
            'Nombre': [cliente.nombre],
            'Apellido': [cliente.apellido],
            'Correo': [cliente.correo],
            'Teléfono': [cliente.telefono],
            'Fecha Registro': [cliente.fecha_registro.strftime('%Y-%m-%d')]
        }
        
        df_cliente = pd.DataFrame(cliente_data)
        
        # Preparar datos de compras
        if cliente.compras:
            compras_data = []
            for compra in cliente.compras:
                compras_data.append({
                    'Fecha': compra.fecha_compra.strftime('%Y-%m-%d'),
                    'Monto': compra.monto,
                    'Descripción': compra.descripcion,
                    'Número Factura': compra.numero_factura
                })
            df_compras = pd.DataFrame(compras_data)
        else:
            df_compras = pd.DataFrame()
        
        # Crear archivo según formato
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if formato == 'excel':
            filename = f'cliente_{numero_doc}_{timestamp}.xlsx'
            filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_cliente.to_excel(writer, sheet_name='Cliente', index=False)
                if not df_compras.empty:
                    df_compras.to_excel(writer, sheet_name='Compras', index=False)
        
        else:  # CSV
            filename = f'cliente_{numero_doc}_{timestamp}.csv'
            filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)
            
            # Combinar datos
            if not df_compras.empty:
                df_cliente['Total Compras'] = df_compras['Monto'].sum()
                df_cliente['Número de Compras'] = len(df_compras)
            
            df_cliente.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINT 3: Reporte de Fidelización ====================
@app.route('/api/reporte-fidelizacion', methods=['GET'])
def reporte_fidelizacion():
    """
    Genera reporte Excel de clientes con compras > 5,000,000 COP en el último mes
    """
    try:
        # Fecha de hace 30 días
        fecha_limite = datetime.now() - timedelta(days=30)
        
        # Obtener todas las compras del último mes
        compras_recientes = Compra.query.filter(
            Compra.fecha_compra >= fecha_limite
        ).all()
        
        # Agrupar compras por cliente
        clientes_compras = {}
        for compra in compras_recientes:
            cliente_id = compra.cliente_id
            if cliente_id not in clientes_compras:
                clientes_compras[cliente_id] = {
                    'cliente': compra.cliente,
                    'compras': [],
                    'total': 0
                }
            clientes_compras[cliente_id]['compras'].append(compra)
            clientes_compras[cliente_id]['total'] += compra.monto
        
        # Filtrar clientes con más de 5,000,000 COP
        clientes_fidelizar = []
        for cliente_id, data in clientes_compras.items():
            if data['total'] > 5_000_000:
                cliente = data['cliente']
                clientes_fidelizar.append({
                    'Tipo Documento': cliente.tipo_documento.descripcion,
                    'Número Documento': cliente.numero_documento,
                    'Nombre': cliente.nombre,
                    'Apellido': cliente.apellido,
                    'Correo': cliente.correo,
                    'Teléfono': cliente.telefono,
                    'Monto Total (COP)': data['total'],
                    'Número de Compras': len(data['compras'])
                })
        
        if not clientes_fidelizar:
            return jsonify({
                'mensaje': 'No hay clientes que superen los 5,000,000 COP en el último mes'
            }), 404
        
        # Crear DataFrame con pandas
        df = pd.DataFrame(clientes_fidelizar)
        
        # Ordenar por monto total (descendente)
        df = df.sort_values('Monto Total (COP)', ascending=False)
        
        # Formatear monto como moneda
        df['Monto Total (COP)'] = df['Monto Total (COP)'].apply(
            lambda x: f"${x:,.2f}"
        )
        
        # Crear archivo Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reporte_fidelizacion_{timestamp}.xlsx'
        filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Clientes a Fidelizar', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Clientes a Fidelizar']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINT 4: Obtener Tipos de Documento ====================
@app.route('/api/tipos-documento', methods=['GET'])
def obtener_tipos_documento():
    """
    Obtiene la lista de tipos de documento disponibles
    """
    try:
        tipos = TipoDocumento.query.all()
        return jsonify({
            'tipos_documento': [
                {'codigo': tipo.codigo, 'descripcion': tipo.descripcion}
                for tipo in tipos
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ==================== ENDPOINT 5: Listar Todos los Clientes ====================
@app.route('/api/listar-clientes', methods=['GET'])
def listar_clientes():
    """
    Lista todos los clientes registrados
    """
    try:
        clientes = Cliente.query.all()
        lista = []
        
        fecha_limite = datetime.now() - timedelta(days=30)
        
        for cliente in clientes:
            # Calcular compras del último mes
            compras_recientes = [c for c in cliente.compras if c.fecha_compra >= fecha_limite]
            total_reciente = sum(c.monto for c in compras_recientes)
            
            lista.append({
                'tipo_documento': cliente.tipo_documento.descripcion,
                'codigo_tipo': cliente.tipo_documento.codigo,
                'numero_documento': cliente.numero_documento,
                'nombre_completo': f"{cliente.nombre} {cliente.apellido}",
                'correo': cliente.correo,
                'telefono': cliente.telefono,
                'total_ultimo_mes': total_reciente,
                'califica_fidelizacion': total_reciente > 5_000_000
            })
        
        # Ordenar por total del último mes (descendente)
        lista.sort(key=lambda x: x['total_ultimo_mes'], reverse=True)
        
        return jsonify({
            'total': len(lista),
            'clientes': lista
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== FUNCIÓN: Inicializar Base de Datos ====================
def init_database():
    """
    Inicializa la base de datos y crea las tablas
    """
    with app.app_context():
        db.create_all()
        
        # Insertar tipos de documento si no existen
        if TipoDocumento.query.count() == 0:
            tipos = [
                TipoDocumento(codigo='CC', descripcion='Cédula de Ciudadanía'),
                TipoDocumento(codigo='NIT', descripcion='NIT'),
                TipoDocumento(codigo='PA', descripcion='Pasaporte')
            ]
            db.session.add_all(tipos)
            db.session.commit()
            print("✅ Tipos de documento creados")
        
        print("✅ Base de datos inicializada correctamente")


# ==================== MAIN ====================
if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)