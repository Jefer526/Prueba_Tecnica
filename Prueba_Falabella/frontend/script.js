// URL base de la API
const API_URL = 'http://127.0.0.1:5000/api';

// Variable global para almacenar los datos del cliente actual
let clienteActual = null;

// Evento al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    searchForm.addEventListener('submit', buscarCliente);
    
    // Cargar lista de clientes al inicio
    cargarListaClientes();
});

// Función para cargar lista de clientes
async function cargarListaClientes() {
    const container = document.getElementById('listaClientesContainer');
    
    try {
        container.innerHTML = '<p class="loading-text">Cargando clientes...</p>';
        
        const response = await fetch(`${API_URL}/listar-clientes`);
        const data = await response.json();
        
        if (response.ok && data.clientes.length > 0) {
            let html = '<div class="clientes-grid">';
            
            data.clientes.forEach(cliente => {
                const cardClass = cliente.califica_fidelizacion ? 'cliente-card fidelizacion' : 'cliente-card';
                
                html += `
                    <div class="${cardClass}" onclick="seleccionarCliente('${cliente.codigo_tipo}', '${cliente.numero_documento}')">
                        <div class="cliente-tipo">${cliente.codigo_tipo}</div>
                        <div class="cliente-nombre">${cliente.nombre_completo}</div>
                        <div class="cliente-doc">📄 ${cliente.numero_documento}</div>
                        <div class="cliente-info">
                            📧 ${cliente.correo}<br>
                            📞 ${cliente.telefono}
                        </div>
                        <div class="cliente-total">
                            💰 Último mes: ${formatearMoneda(cliente.total_ultimo_mes)}
                        </div>
                        ${cliente.califica_fidelizacion ? '<span class="badge-fidelizacion">⭐ CALIFICA FIDELIZACIÓN</span>' : ''}
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="no-clientes">No hay clientes registrados</div>';
        }
        
    } catch (error) {
        container.innerHTML = '<div class="no-clientes">Error al cargar clientes</div>';
        console.error('Error:', error);
    }
}

// Función para seleccionar un cliente desde la lista
function seleccionarCliente(tipoDoc, numeroDoc) {
    // Llenar el formulario
    document.getElementById('tipoDocumento').value = tipoDoc;
    document.getElementById('numeroDocumento').value = numeroDoc;
    
    // Scroll al formulario
    document.querySelector('.search-section').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
    
    // Hacer la búsqueda automáticamente
    setTimeout(() => {
        document.getElementById('searchForm').dispatchEvent(new Event('submit'));
    }, 500);
}

// Función para buscar cliente
async function buscarCliente(event) {
    event.preventDefault();
    
    // Obtener valores del formulario
    const tipoDocumento = document.getElementById('tipoDocumento').value;
    const numeroDocumento = document.getElementById('numeroDocumento').value;
    
    // Limpiar mensajes de error previos
    ocultarError();
    ocultarResultados();
    
    try {
        // Mostrar indicador de carga
        mostrarCargando();
        
        // Hacer petición a la API
        const response = await fetch(`${API_URL}/buscar-cliente`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tipo_documento: tipoDocumento,
                numero_documento: numeroDocumento
            })
        });
        
        ocultarCargando();
        
        const data = await response.json();
        
        if (response.ok) {
            // Guardar datos del cliente
            clienteActual = data;
            // Mostrar resultados
            mostrarResultados(data);
        } else {
            // Mostrar error
            mostrarError(data.error || 'Error al buscar el cliente');
        }
        
    } catch (error) {
        ocultarCargando();
        mostrarError('Error de conexión con el servidor. Asegúrate de que el backend esté corriendo.');
        console.error('Error:', error);
    }
}

// Función para mostrar resultados
function mostrarResultados(data) {
    const { cliente, compras, total_compras, numero_compras } = data;
    
    // Mostrar sección de resultados
    document.getElementById('resultSection').style.display = 'block';
    
    // Llenar datos del cliente
    document.getElementById('clienteTipoDoc').textContent = cliente.tipo_documento;
    document.getElementById('clienteNumDoc').textContent = cliente.numero_documento;
    document.getElementById('clienteNombre').textContent = `${cliente.nombre} ${cliente.apellido}`;
    document.getElementById('clienteCorreo').textContent = cliente.correo;
    document.getElementById('clienteTelefono').textContent = cliente.telefono;
    document.getElementById('clienteFechaRegistro').textContent = formatearFecha(cliente.fecha_registro);
    
    // Llenar resumen de compras
    document.getElementById('totalCompras').textContent = formatearMoneda(total_compras);
    document.getElementById('numeroCompras').textContent = numero_compras;
    
    // Llenar tabla de compras
    const tbody = document.getElementById('comprasTableBody');
    tbody.innerHTML = '';
    
    if (compras.length > 0) {
        compras.forEach(compra => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${formatearFecha(compra.fecha_compra)}</td>
                <td>${compra.descripcion || 'N/A'}</td>
                <td>${formatearMoneda(compra.monto)}</td>
                <td>${compra.numero_factura || 'N/A'}</td>
            `;
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No hay compras registradas</td></tr>';
    }
    
    // Scroll suave a los resultados
    document.getElementById('resultSection').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Función para exportar datos del cliente
async function exportarCliente(formato) {
    if (!clienteActual) {
        mostrarError('Primero debe buscar un cliente');
        return;
    }
    
    const numeroDocumento = clienteActual.cliente.numero_documento;
    
    try {
        mostrarCargando();
        
        const response = await fetch(`${API_URL}/exportar-cliente`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                numero_documento: numeroDocumento,
                formato: formato
            })
        });
        
        ocultarCargando();
        
        if (response.ok) {
            // Descargar archivo
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Obtener nombre del archivo del header Content-Disposition
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `cliente_${numeroDocumento}.${formato === 'excel' ? 'xlsx' : 'csv'}`;
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            mostrarExito(`Archivo ${formato.toUpperCase()} descargado exitosamente`);
        } else {
            const data = await response.json();
            mostrarError(data.error || 'Error al exportar datos');
        }
        
    } catch (error) {
        ocultarCargando();
        mostrarError('Error al exportar datos');
        console.error('Error:', error);
    }
}

// Función para generar reporte de fidelización
async function generarReporteFidelizacion() {
    try {
        mostrarCargando();
        
        const response = await fetch(`${API_URL}/reporte-fidelizacion`, {
            method: 'GET'
        });
        
        ocultarCargando();
        
        if (response.ok) {
            // Descargar archivo
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Obtener nombre del archivo
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'reporte_fidelizacion.xlsx';
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            mostrarExito('Reporte de fidelización descargado exitosamente');
        } else {
            const data = await response.json();
            mostrarError(data.mensaje || data.error || 'No hay clientes que califiquen para fidelización');
        }
        
    } catch (error) {
        ocultarCargando();
        mostrarError('Error al generar el reporte');
        console.error('Error:', error);
    }
}

// Funciones auxiliares
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(valor);
}

function formatearFecha(fecha) {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function mostrarError(mensaje) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = '❌ ' + mensaje;
    errorDiv.style.display = 'block';
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function ocultarError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function mostrarExito(mensaje) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = '✅ ' + mensaje;
    errorDiv.style.display = 'block';
    errorDiv.style.background = '#d4edda';
    errorDiv.style.color = '#155724';
    errorDiv.style.borderColor = '#c3e6cb';
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    setTimeout(() => {
        ocultarError();
        resetearEstiloError();
    }, 3000);
}

function resetearEstiloError() {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.style.background = '#f8d7da';
    errorDiv.style.color = '#721c24';
    errorDiv.style.borderColor = '#f5c6cb';
}

function ocultarResultados() {
    document.getElementById('resultSection').style.display = 'none';
    clienteActual = null;
}

function mostrarCargando() {
    const btn = document.querySelector('.btn-primary');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Buscando...';
    }
}

function ocultarCargando() {
    const btn = document.querySelector('.btn-primary');
    if (btn) {
        btn.disabled = false;
        btn.textContent = '🔎 Buscar';
    }
}