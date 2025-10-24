// Middleware de sesión
document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("jwt_token");
    const currentPath = window.location.pathname;

    const isAuthPage =
        currentPath.includes("/login") || currentPath.includes("/registro");

    // Si NO hay token y NO estamos en login/registro → redirigir
    if (!token && !isAuthPage) {
        window.location.href = "/login";
        return;
    }

    // Si HAY token y estamos en login o registro → ir al home
    if (token && isAuthPage) {
        window.location.href = "/";
        return;
    }

    // Si hay token, opcionalmente verificamos su validez con la API
    if (token && !isAuthPage) {
        verificarToken(token);
    }
});

// Función para validar token con la API
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

// Cerrar sesión
async function cerrarSesion() {
    const usuarioId = localStorage.getItem("usuario_id");
    const token = localStorage.getItem("jwt_token");

    if (!usuarioId) {
        console.error("No se encontró el ID del usuario en localStorage");
        return;
    }

    try {
        const response = await fetch("/api/usuarios/logout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ usuario_id: usuarioId }),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error(
                "Error al cerrar sesión en la BD:",
                data.error || data.message
            );
        } else {
            console.log("Sesión registrada como cerrada:", data.message);
        }
    } catch (error) {
        console.error("Error al conectar con la API:", error);
    }

    // Eliminar datos locales y redirigir al login
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("usuario_nombre");
    localStorage.removeItem("usuario_username");
    localStorage.removeItem("usuario_id");
    window.location.href = "/login";
}
