const API_URL = "http://192.168.1.17:5000/api";
let datosCompletos = [];

window.addEventListener("load", cargarDatos);

// ================================
// CARGA DE DATOS PRINCIPAL
// ================================
async function cargarDatos() {
    try {
        // Estado de la API
        const healthData = await (await fetch(`${API_URL}/health`)).json();
        if (healthData.success) {
            document
                .getElementById("apiStatus")
                .classList.replace("status-unknown", "status-online");
            document.getElementById("apiStatusText").textContent = "Conectada";
        }

        // Estadísticas
        const statsData = await (await fetch(`${API_URL}/estadisticas`)).json();
        if (statsData.success) actualizarEstadisticas(statsData.estadisticas);

        // Estado de dispositivos
        const estadoData = await (await fetch(`${API_URL}/estado`)).json();
        if (estadoData.success) actualizarEstadoDispositivos(estadoData.estado);

        // Acciones recientes
        const accionesData = await (
            await fetch(`${API_URL}/acciones?limite=150`)
        ).json();

        if (accionesData.success) {
            datosCompletos = accionesData.acciones;
            mostrarTabla(datosCompletos);
            document.getElementById("totalRegistros").textContent =
                accionesData.total;
        }

        document.getElementById("ultimaActualizacion").textContent =
            new Date().toLocaleTimeString("es-CO");
    } catch (error) {
        console.error("Error al cargar datos:", error);
        document
            .getElementById("apiStatus")
            .classList.replace("status-online", "status-offline");
        document.getElementById("apiStatusText").textContent = "Desconectada";
    }
}

// ================================
// ESTADÍSTICAS Y ESTADO
// ================================
function actualizarEstadisticas(stats) {
    document.getElementById("totalRegistros").textContent =
        stats.total_acciones || "-";

    stats.por_dispositivo.forEach((item) => {
        if (item.dispositivo === "MOTOR")
            document.getElementById("motorTotal").textContent = item.cantidad;
        if (item.dispositivo === "LED_VERDE")
            document.getElementById("ledVerdeTotal").textContent = item.cantidad;
        if (item.dispositivo === "LED_ROJO")
            document.getElementById("ledRojoTotal").textContent = item.cantidad;
    });
}

function actualizarEstadoDispositivos(estado) {
    const dispositivos = [
        { key: "motor", prefix: "motor"},
        { key: "led_verde", prefix: "ledVerde"},
        { key: "led_rojo", prefix: "ledRojo"},
    ];

    dispositivos.forEach((d) => {
        const activo = estado[d.key]?.activo || false;
        const div = document.getElementById(`${d.prefix}Status`);
        if (!div) return;

        div.className = `device-status ${activo ? "active" : "inactive"}`;
        document.getElementById(`${d.prefix}Icono`).innerHTML = activo
            ? '<i class="bi bi-toggle-on text-success"></i>'
            : '<i class="bi bi-toggle-off text-danger"></i>';
    });
}

// ================================
// TABLA DE HISTORIAL
// ================================
function mostrarTabla(datos) {
    let html = `
        <div class="table-responsive">
            <table class="table table-hover table-borderless align-middle mb-0 overflow-hidden">
                <thead class="bg-primary bg-opacity-25">
                    <tr class="text-center">
                        <th scope="col" style="width: 5%">#</th>
                        <th scope="col">Usuario</th>
                        <th scope="col">Dispositivo</th>
                        <th scope="col">Acción</th>
                        <th scope="col">Fecha y Hora</th>
                    </tr>
                </thead>
                <tbody>
    `;

    if (datos.length === 0) {
        html += `
            <tr>
                <td colspan="5" class="text-center py-4 text-muted">
                    <div class="py-3">
                        <div class="display-6 mb-2">📭</div>
                        <p class="mb-0">No hay registros coincidentes.</p>
                    </div>
                </td>
            </tr>
        `;
    } else {
        datos.forEach((a) => {
            const colorAccion =
                a.accion === "ENCENDER"
                    ? "bg-success-subtle text-dark"
                    : "bg-danger-subtle text-dark";

            const colorDispositivo =
                a.dispositivo.includes("LED_VERDE")
                    ? "bg-success-subtle text-dark"
                    : a.dispositivo.includes("LED_ROJO")
                        ? "bg-danger-subtle text-dark"
                        : "bg-secondary-subtle text-dark";

            html += `
                <tr>
                    <td class="text-center text-secondary">${a.id}</td>
                    <td class="fw-semibold">${a.usuario}</td>
                    <td class="text-center">
                        <span class="badge ${colorDispositivo} px-3 py-2 text-uppercase">
                        ${a.dispositivo.replace("_", " ")}
                        </span>
                    </td>
                    <td class="text-center">
                        <span class="badge ${colorAccion} px-3 py-2 text-uppercase">
                        ${a.accion}
                        </span>
                    </td>
                    <td class="text-center text-nowrap">${a.fecha_hora}</td>
                </tr>
            `;
        });
    }

    html += `
        </tbody>
      </table>
    </div>
  `;

    document.getElementById("tablaContainer").innerHTML = html;
}

// ================================
// FILTRO DE BÚSQUEDA
// ================================
function filtrarTabla() {
    const busqueda = document
        .getElementById("searchInput")
        .value.toLowerCase()
        .trim();

    const filtrados = datosCompletos.filter(
        (a) =>
            a.id.toString().includes(busqueda) ||
            a.usuario.toLowerCase().includes(busqueda) ||
            a.dispositivo.toLowerCase().includes(busqueda) ||
            a.accion.toLowerCase().includes(busqueda) ||
            a.fecha_hora.toLowerCase().includes(busqueda)
    );

    mostrarTabla(filtrados);
}