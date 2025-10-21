// =======================
// 🔐 Middleware de sesión
// =======================
document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("jwt_token");
    const currentPath = window.location.pathname;

    const isAuthPage = currentPath.includes("/login") || currentPath.includes("/registro");

    // Si NO hay token y NO estamos en login/registro → redirigir
    if (!token && !isAuthPage) {
        window.location.href = "/login";
        return;
    }

    // Si HAY token y estamos en login o registro → ir al dashboard
    if (token && isAuthPage) {
        window.location.href = "/dashboard";
        return;
    }

    // Si hay token, opcionalmente verificamos su validez con la API
    if (token && !isAuthPage) {
        verificarToken(token);
    }
});

// =======================
// 🧩 Función para validar token con la API
// =======================
async function verificarToken(token) {
    try {
        const response = await fetch("/api/health", {
            headers: { Authorization: `Bearer ${token}` },
        });

        if (response.status === 401 || response.status === 403) {
            // Token inválido o expirado
            cerrarSesion();
        }
    } catch (error) {
        console.error("Error al verificar token:", error);
    }
}

// =======================
// 🚪 Cerrar sesión
// =======================
function cerrarSesion() {
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("usuario_nombre");
    localStorage.removeItem("usuario_username");
    window.location.href = "/login";
}
