import unicodedata

# Módulos a los que puede entrar cada rol (el rol viene del campo Tipo de Usuarios)
MODULOS_POR_ROL = {
    "administrador": ["Usuarios", "Clientes", "Vehiculos", "Reparaciones", "Piezas"],
    "mecanico": ["Reparaciones", "Piezas"],
    "auxiliar": ["Clientes", "Vehiculos"],
}


def normalizar_rol(tipo):
    """'Mecánico ' -> 'mecanico' (sin acentos, minúsculas, sin espacios)."""
    if not tipo:
        return ""
    texto = unicodedata.normalize("NFD", str(tipo).strip().lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def modulos_permitidos(tipo):
    return MODULOS_POR_ROL.get(normalizar_rol(tipo), [])


def tiene_acceso(tipo, modulo):
    return modulo in modulos_permitidos(tipo)
