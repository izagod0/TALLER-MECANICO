import mysql.connector
from mysql.connector import errors
from tkinter import messagebox

ESTADOS_REPARACION = ["Pendiente", "En proceso", "Terminada", "Entregada"]

# ---------------------------------------------------------------------------
# Configuración de cada módulo
#
# campos      : campos del formulario (txt = caja de texto, cmb = lista desplegable).
#               El nombre sin prefijo es el nombre real de la columna en MySQL.
# pk          : columna que es llave primaria.
# modo_id     : "auto"  -> ID que se muestra en el formulario y se calcula solo (MAX(id)+1)
#               "campo" -> la llave primaria es uno de los campos (Vehiculos: Matricula)
# combos      : de dónde salen las opciones de cada lista desplegable cmb
#               ("clientes", "vehiculos", "mecanicos" o una lista fija)
# etiquetas   : texto que se muestra junto a cada campo
# largos      : campos de texto con caja más ancha
# opcionales  : columnas que pueden quedar vacías (las demás son obligatorias)
# fechas      : columnas con formato AAAA-MM-DD
# numericos   : columnas numéricas ("decimal" o "entero"), no pueden ser negativas
# defaults    : valores que se llenan solos al presionar Nuevo ("hoy" = fecha de hoy)
# buscar      : columnas donde busca el filtro (None = todas las de la tabla)
# select / columnas_tabla / buscar_sql / orden : consulta personalizada para la tabla de búsqueda
#               (la primera columna del select debe ser la llave primaria)
# resaltar    : (columna, columna límite): pinta de rojo la fila si valor <= límite
# acciones_extra : botones extra del formulario [(texto, clave de acción)]
# ---------------------------------------------------------------------------
CONFIG_BASE = {
    "combos": {},
    "etiquetas": {},
    "largos": [],
    "opcionales": [],
    "fechas": [],
    "numericos": {},
    "defaults": {},
    "buscar": None,
    "select": None,
    "columnas_tabla": None,
    "buscar_sql": None,
    "orden": None,
    "resaltar": None,
    "acciones_extra": [],
    "anchos_tabla": {},
    "etiqueta_busqueda": "Escribe para filtrar:",
}

TOTAL_REPARACION_SQL = (
    "r.CostoManoObra + COALESCE((SELECT SUM(rp.Cantidad * rp.PrecioUnitario) "
    "FROM ReparacionPiezas rp WHERE rp.reparacion_id = r.id), 0)"
)

ENTIDADES = {
    "Usuarios": {
        "campos": ["txtNombre", "txtUsername", "txtContrasena", "txtTipo", "txtTelefono"],
        "pk": "id",
        "modo_id": "auto",
    },
    "Clientes": {
        "campos": ["txtNombre", "txtDomicilio", "txtTelefono", "txtRFC"],
        "pk": "id",
        "modo_id": "auto",
    },
    "Vehiculos": {
        "campos": ["txtMatricula", "txtModelo", "txtMarca", "txtFecha", "cmbcliente_id"],
        "pk": "Matricula",
        "modo_id": "campo",
        "combos": {"cmbcliente_id": "clientes"},
        "etiquetas": {"txtFecha": "Fecha (AAAA-MM-DD)", "cmbcliente_id": "Cliente"},
        "fechas": ["Fecha"],
        "buscar": ["Matricula"],
        "etiqueta_busqueda": "Buscar por matrícula:",
    },
    "Reparaciones": {
        "campos": ["cmbMatricula", "cmbmecanico_id", "cmbEstado", "txtFechaEntrada",
                   "txtFechaSalida", "txtFalla", "txtDiagnostico", "txtCostoManoObra"],
        "pk": "id",
        "modo_id": "auto",
        "combos": {
            "cmbMatricula": "vehiculos",
            "cmbmecanico_id": "mecanicos",
            "cmbEstado": ESTADOS_REPARACION,
        },
        "etiquetas": {
            "cmbMatricula": "Vehículo",
            "cmbmecanico_id": "Mecánico",
            "cmbEstado": "Estado",
            "txtFechaEntrada": "Fecha entrada (AAAA-MM-DD)",
            "txtFechaSalida": "Fecha salida (AAAA-MM-DD)",
            "txtFalla": "Falla reportada",
            "txtDiagnostico": "Diagnóstico",
            "txtCostoManoObra": "Mano de obra ($)",
        },
        "largos": ["txtFalla", "txtDiagnostico"],
        "opcionales": ["mecanico_id", "FechaSalida", "Diagnostico"],
        "fechas": ["FechaEntrada", "FechaSalida"],
        "numericos": {"CostoManoObra": "decimal"},
        "defaults": {"FechaEntrada": "hoy", "Estado": "Pendiente", "CostoManoObra": "0"},
        "select": (
            "SELECT r.id, r.Matricula, CONCAT_WS(' ', v.Marca, v.Modelo), COALESCE(u.Nombre, ''), "
            "r.Estado, r.FechaEntrada, r.FechaSalida, r.Falla, " + TOTAL_REPARACION_SQL + " "
            "FROM Reparaciones r "
            "LEFT JOIN Vehiculos v ON v.Matricula = r.Matricula "
            "LEFT JOIN Usuarios u ON u.id = r.mecanico_id"
        ),
        "columnas_tabla": ["ID", "Matrícula", "Vehículo", "Mecánico", "Estado",
                           "Entrada", "Salida", "Falla", "Total"],
        "buscar_sql": ["r.id", "r.Matricula", "v.Marca", "v.Modelo", "u.Nombre",
                       "r.Estado", "r.Falla", "r.Diagnostico"],
        "orden": "r.id DESC",
        "anchos_tabla": {"ID": 45, "Matrícula": 80, "Vehículo": 130, "Mecánico": 100,
                         "Estado": 85, "Entrada": 85, "Salida": 85, "Falla": 150, "Total": 80},
        "acciones_extra": [("Piezas usadas", "PIEZAS")],
        "etiqueta_busqueda": "Buscar (matrícula, mecánico, estado, falla):",
    },
    "Piezas": {
        "campos": ["txtDescripcion", "txtPrecio", "txtStock", "txtStockMinimo"],
        "pk": "id",
        "modo_id": "auto",
        "etiquetas": {
            "txtPrecio": "Precio ($)",
            "txtStock": "Stock actual",
            "txtStockMinimo": "Stock mínimo (alerta)",
        },
        "largos": ["txtDescripcion"],
        "numericos": {"Precio": "decimal", "Stock": "entero", "StockMinimo": "entero"},
        "defaults": {"Stock": "0", "StockMinimo": "5"},
        "resaltar": ("Stock", "StockMinimo"),
        "etiqueta_busqueda": "Buscar pieza:",
    },
}


class ModeloPrincipal:
    def __init__(self):
        try:
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="taller_mecanico",
                autocommit=True,  # así siempre se ven los datos más recientes
            )
        except Exception as e:
            print(f"Error de conexión a XAMPP: {e}")
            self.conexion = None

    # ---------- Utilidades de configuración ----------
    @staticmethod
    def nombre_columna(campo):
        """Quita el prefijo txt/cmb para obtener el nombre real de la columna."""
        return campo.replace("txt", "").replace("cmb", "")

    def obtener_config(self, entidad):
        cfg = dict(CONFIG_BASE)
        cfg.update(ENTIDADES[entidad])
        return cfg

    def obtener_campos(self, entidad):
        return ENTIDADES[entidad]["campos"]

    def obtener_columnas_tabla(self, entidad):
        """Encabezados de la tabla de búsqueda (la llave primaria va primero)."""
        cfg = self.obtener_config(entidad)
        if cfg["columnas_tabla"]:
            return list(cfg["columnas_tabla"])
        columnas = [self.nombre_columna(c) for c in cfg["campos"]]
        if cfg["modo_id"] != "campo":
            columnas.insert(0, cfg["pk"])
        return columnas

    def siguiente_id(self, entidad):
        """ID que tendrá el próximo registro: si ya hay 3, regresa 4."""
        if not self.conexion:
            return ""
        try:
            cursor = self.conexion.cursor()
            cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {entidad}")
            siguiente = cursor.fetchone()[0]
            cursor.close()
            return siguiente
        except Exception as e:
            print(f"Error obteniendo siguiente ID: {e}")
            return ""

    def _rollback(self):
        try:
            self.conexion.rollback()
        except Exception:
            pass

    # ---------- Opciones de las listas desplegables ----------
    def obtener_opciones(self, fuente):
        if isinstance(fuente, (list, tuple)):
            return list(fuente)
        if fuente == "clientes":
            return self.obtener_lista_clientes()
        if fuente == "vehiculos":
            return self.obtener_lista_vehiculos()
        if fuente == "mecanicos":
            return self.obtener_lista_mecanicos()
        return []

    def _consultar(self, sql, params=()):
        if not self.conexion:
            return []
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql, params)
            filas = cursor.fetchall()
            cursor.close()
            return filas
        except Exception as e:
            print(f"Error en consulta: {e}")
            return []

    def obtener_lista_clientes(self):
        filas = self._consultar("SELECT id, Nombre FROM Clientes ORDER BY id")
        return [f"{r[0]} - {r[1]}" for r in filas]

    def obtener_lista_vehiculos(self):
        filas = self._consultar(
            "SELECT v.Matricula, v.Marca, v.Modelo, c.Nombre "
            "FROM Vehiculos v LEFT JOIN Clientes c ON c.id = v.cliente_id "
            "ORDER BY v.Matricula"
        )
        return [f"{r[0]} - {r[1]} {r[2]} ({r[3] or 'sin cliente'})" for r in filas]

    def obtener_lista_mecanicos(self):
        filas = self._consultar("SELECT id, Nombre FROM Usuarios WHERE Tipo = 'Mecanico' ORDER BY Nombre")
        return [f"{r[0]} - {r[1]}" for r in filas]

    # ---------- Operaciones CRUD (regresan True si salió bien) ----------
    def obtener_registro(self, entidad, id_registro):
        """Regresa {columna: valor_texto} con los campos del formulario, o None."""
        if not self.conexion:
            return None
        try:
            cfg = self.obtener_config(entidad)
            columnas = [self.nombre_columna(c) for c in cfg["campos"]]
            cursor = self.conexion.cursor()
            cursor.execute(f"SELECT {', '.join(columnas)} FROM {entidad} WHERE {cfg['pk']} = %s", (id_registro,))
            fila = cursor.fetchone()
            cursor.close()
            if not fila:
                return None
            return {col: "" if v is None else str(v) for col, v in zip(columnas, fila)}
        except Exception as e:
            print(f"Error obteniendo registro: {e}")
            return None

    def guardar_datos(self, entidad, datos):
        if not self.conexion:
            return False
        try:
            cfg = self.obtener_config(entidad)
            columnas = [self.nombre_columna(k) for k in datos.keys()]
            valores = [None if v == "" else v for v in datos.values()]

            if cfg["modo_id"] == "auto":
                columnas.insert(0, "id")
                valores.insert(0, self.siguiente_id(entidad))

            placeholders = ", ".join(["%s"] * len(columnas))
            sql = f"INSERT INTO {entidad} ({', '.join(columnas)}) VALUES ({placeholders})"

            cursor = self.conexion.cursor()
            cursor.execute(sql, tuple(valores))
            self.conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", f"Datos guardados en {entidad}.")
            return True
        except Exception as e:
            messagebox.showerror("Error SQL", f"Error al insertar:\n{e}")
            return False

    def actualizar_datos(self, entidad, id_registro, datos):
        if not self.conexion:
            return False
        try:
            pk = self.obtener_config(entidad)["pk"]
            set_clauses = []
            valores = []

            for k, v in datos.items():
                col = self.nombre_columna(k)
                if col.lower() != pk.lower():
                    set_clauses.append(f"{col} = %s")
                    valores.append(None if v == "" else v)

            valores.append(id_registro)
            sql = f"UPDATE {entidad} SET {', '.join(set_clauses)} WHERE {pk} = %s"

            cursor = self.conexion.cursor()
            cursor.execute(sql, tuple(valores))
            self.conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", f"Registro actualizado en {entidad}.")
            return True
        except Exception as e:
            messagebox.showerror("Error SQL", f"Error al actualizar:\n{e}")
            return False

    def eliminar_datos(self, entidad, id_registro):
        if not self.conexion:
            return False
        try:
            pk = self.obtener_config(entidad)["pk"]
            cursor = self.conexion.cursor()

            if entidad == "Reparaciones":
                # Al borrar una reparación, las piezas que usó regresan al inventario
                self.conexion.start_transaction()
                cursor.execute(
                    "UPDATE Piezas p JOIN ReparacionPiezas rp ON rp.pieza_id = p.id "
                    "SET p.Stock = p.Stock + rp.Cantidad WHERE rp.reparacion_id = %s",
                    (id_registro,),
                )
                cursor.execute("DELETE FROM ReparacionPiezas WHERE reparacion_id = %s", (id_registro,))
                cursor.execute("DELETE FROM Reparaciones WHERE id = %s", (id_registro,))
                self.conexion.commit()
            else:
                cursor.execute(f"DELETE FROM {entidad} WHERE {pk} = %s", (id_registro,))
                self.conexion.commit()

            cursor.close()
            messagebox.showinfo("Éxito", f"Registro eliminado de {entidad}.")
            return True
        except errors.IntegrityError as e:
            self._rollback()
            if e.errno == 1451:
                messagebox.showerror(
                    "No se puede eliminar",
                    "Este registro está relacionado con otros datos (por ejemplo: un cliente con "
                    "vehículos, un vehículo con reparaciones o una pieza usada en una reparación).\n\n"
                    "Elimina o reasigna primero los registros relacionados.",
                )
            else:
                messagebox.showerror("Error SQL", f"Error al eliminar:\n{e}")
            return False
        except Exception as e:
            self._rollback()
            messagebox.showerror("Error SQL", f"Error al eliminar:\n{e}")
            return False

    def buscar_datos(self, entidad, termino=""):
        if not self.conexion:
            return []
        try:
            cfg = self.obtener_config(entidad)

            if cfg["select"]:
                sql = cfg["select"]
                columnas_busqueda = cfg["buscar_sql"]
            else:
                columnas_tabla = self.obtener_columnas_tabla(entidad)
                sql = f"SELECT {', '.join(columnas_tabla)} FROM {entidad}"
                columnas_busqueda = cfg["buscar"] or columnas_tabla

            parametros = ()
            if termino:
                sql += " WHERE " + " OR ".join([f"{col} LIKE %s" for col in columnas_busqueda])
                parametros = tuple([f"%{termino}%"] * len(columnas_busqueda))
            if cfg["orden"]:
                sql += f" ORDER BY {cfg['orden']}"

            cursor = self.conexion.cursor()
            cursor.execute(sql, parametros)
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Error de búsqueda: {e}")
            return []

    # ---------- Login ----------
    def verificar_login(self, username, password):
        """Regresa un diccionario con los datos del usuario, o None si no coincide."""
        if not self.conexion:
            return None
        try:
            cursor = self.conexion.cursor()
            sql = "SELECT id, Username, Tipo FROM Usuarios WHERE Username = %s AND Contrasena = %s"
            cursor.execute(sql, (username, password))
            fila = cursor.fetchone()
            cursor.close()
            if fila:
                return {"id": fila[0], "username": fila[1], "tipo": fila[2]}
            return None
        except Exception as e:
            print(f"Error en login: {e}")
            return None

    # ---------- Piezas usadas en una reparación ----------
    def contar_stock_bajo(self):
        filas = self._consultar("SELECT COUNT(*) FROM Piezas WHERE Stock <= StockMinimo")
        return filas[0][0] if filas else 0

    def obtener_resumen_reparacion(self, id_reparacion):
        filas = self._consultar(
            "SELECT r.Matricula, COALESCE(v.Marca, ''), COALESCE(v.Modelo, ''), r.Estado "
            "FROM Reparaciones r LEFT JOIN Vehiculos v ON v.Matricula = r.Matricula "
            "WHERE r.id = %s",
            (id_reparacion,),
        )
        if not filas:
            return None
        matricula, marca, modelo, estado = filas[0]
        texto = f"Reparación #{id_reparacion}  ·  {matricula} {marca} {modelo}".strip() + f"  ·  {estado}"
        return {"texto": texto, "estado": estado}

    def obtener_piezas_disponibles(self):
        filas = self._consultar("SELECT id, Descripcion, Stock FROM Piezas WHERE Stock > 0 ORDER BY Descripcion")
        return [f"{r[0]} - {r[1]} (stock {r[2]})" for r in filas]

    def obtener_piezas_reparacion(self, id_reparacion):
        return self._consultar(
            "SELECT rp.pieza_id, p.Descripcion, rp.Cantidad, rp.PrecioUnitario, "
            "rp.Cantidad * rp.PrecioUnitario "
            "FROM ReparacionPiezas rp JOIN Piezas p ON p.id = rp.pieza_id "
            "WHERE rp.reparacion_id = %s ORDER BY p.Descripcion",
            (id_reparacion,),
        )

    def obtener_totales_reparacion(self, id_reparacion):
        """Regresa (mano_de_obra, total_piezas) como números."""
        mano = self._consultar("SELECT CostoManoObra FROM Reparaciones WHERE id = %s", (id_reparacion,))
        piezas = self._consultar(
            "SELECT COALESCE(SUM(Cantidad * PrecioUnitario), 0) FROM ReparacionPiezas WHERE reparacion_id = %s",
            (id_reparacion,),
        )
        mano_obra = float(mano[0][0] or 0) if mano else 0.0
        total_piezas = float(piezas[0][0] or 0) if piezas else 0.0
        return mano_obra, total_piezas

    def agregar_pieza_reparacion(self, id_reparacion, id_pieza, cantidad):
        """Descuenta del stock y registra la pieza en la reparación. Regresa (ok, mensaje)."""
        if not self.conexion:
            return False, "Sin conexión a la base de datos."
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT Precio FROM Piezas WHERE id = %s", (id_pieza,))
            fila = cursor.fetchone()
            if not fila:
                cursor.close()
                return False, "La pieza ya no existe."
            precio = fila[0]

            self.conexion.start_transaction()
            # El descuento solo ocurre si alcanza el stock (evita stock negativo)
            cursor.execute(
                "UPDATE Piezas SET Stock = Stock - %s WHERE id = %s AND Stock >= %s",
                (cantidad, id_pieza, cantidad),
            )
            if cursor.rowcount != 1:
                self._rollback()
                cursor.close()
                return False, "No hay suficiente stock de esa pieza."

            cursor.execute(
                "INSERT INTO ReparacionPiezas (reparacion_id, pieza_id, Cantidad, PrecioUnitario) "
                "VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE Cantidad = Cantidad + %s",
                (id_reparacion, id_pieza, cantidad, precio, cantidad),
            )
            self.conexion.commit()
            cursor.close()
            return True, ""
        except Exception as e:
            self._rollback()
            return False, f"Error SQL:\n{e}"

    def quitar_pieza_reparacion(self, id_reparacion, id_pieza):
        """Quita la pieza de la reparación y devuelve su cantidad al stock. Regresa (ok, mensaje)."""
        if not self.conexion:
            return False, "Sin conexión a la base de datos."
        try:
            cursor = self.conexion.cursor()
            self.conexion.start_transaction()
            cursor.execute(
                "SELECT Cantidad FROM ReparacionPiezas WHERE reparacion_id = %s AND pieza_id = %s",
                (id_reparacion, id_pieza),
            )
            fila = cursor.fetchone()
            if not fila:
                self._rollback()
                cursor.close()
                return False, "Esa pieza ya no está en la reparación."
            cursor.execute("UPDATE Piezas SET Stock = Stock + %s WHERE id = %s", (fila[0], id_pieza))
            cursor.execute(
                "DELETE FROM ReparacionPiezas WHERE reparacion_id = %s AND pieza_id = %s",
                (id_reparacion, id_pieza),
            )
            self.conexion.commit()
            cursor.close()
            return True, ""
        except Exception as e:
            self._rollback()
            return False, f"Error SQL:\n{e}"
