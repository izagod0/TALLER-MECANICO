# modelo.py
import mysql.connector
from tkinter import messagebox

ENTIDADES = {
    "Usuarios": ["txtNombre", "txtUsername", "txtContrasena", "txtTipo"],
    "Clientes": ["txtNombre", "txtAp", "txtAm"],
    "Vehiculos": ["txtMatricula", "txtModelo", "txtMarca"],
    "Reparaciones": ["txtFechaEntrada", "txtFechaSalida", "txtFalla", "txtnumero_piezas"],
    "Piezas": ["txtDescripcion", "txtStock"]
}

class ModeloPrincipal:
    def __init__(self):
        try:
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="", 
                database="taller_mecanico"
            )
        except Exception as e:
            print(f"Error de conexión a XAMPP: {e}")
            self.conexion = None

    def obtener_campos(self, entidad):
        return ENTIDADES.get(entidad, [])

    def guardar_datos(self, entidad, datos):
        if not self.conexion: return
        try:
            cursor = self.conexion.cursor()
            columnas = ", ".join([k.replace("txt", "").replace("cmb", "") for k in datos.keys()])
            placeholders = ", ".join(["%s"] * len(datos))
            
            sql = f"INSERT INTO {entidad} ({columnas}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(datos.values()))
            self.conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", f"Datos guardados en {entidad}.")
        except Exception as e:
            messagebox.showerror("Error SQL", f"Error al insertar:\n{e}")

    def actualizar_datos(self, entidad, id_registro, datos):
        """Actualiza un registro existente mediante su ID."""
        if not self.conexion: return
        try:
            cursor = self.conexion.cursor()
            set_clauses = []
            valores = []
            
            for k, v in datos.items():
                col = k.replace("txt", "").replace("cmb", "")
                if col.lower() != "id":
                    set_clauses.append(f"{col} = %s")
                    valores.append(v)
            
            set_str = ", ".join(set_clauses)
            valores.append(id_registro)
            
            sql = f"UPDATE {entidad} SET {set_str} WHERE id = %s"
            cursor.execute(sql, tuple(valores))
            self.conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", f"Registro actualizado en {entidad}.")
        except Exception as e:
            messagebox.showerror("Error SQL", f"Error al actualizar:\n{e}")

    def eliminar_datos(self, entidad, id_registro):
        """Elimina un registro mediante su ID."""
        if not self.conexion: return
        try:
            cursor = self.conexion.cursor()
            sql = f"DELETE FROM {entidad} WHERE id = %s"
            cursor.execute(sql, (id_registro,))
            self.conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", f"Registro eliminado de {entidad}.")
        except Exception as e:
            messagebox.showerror("Error SQL", f"Error al eliminar:\n{e}")

    def buscar_datos(self, entidad, termino=""):
        if not self.conexion: return []
        try:
            cursor = self.conexion.cursor()
            campos = self.obtener_campos(entidad)
            columnas = [k.replace("txt", "").replace("cmb", "") for k in campos]
            
            tiene_id = any(col.lower() == "id" for col in columnas)
            cols_sql = ", ".join(columnas) if tiene_id else "id, " + ", ".join(columnas)
            
            if termino:
                condiciones = " OR ".join([f"{col} LIKE %s" for col in columnas])
                sql = f"SELECT {cols_sql} FROM {entidad} WHERE {condiciones}"
                valores = tuple([f"%{termino}%"] * len(columnas))
                cursor.execute(sql, valores)
            else:
                sql = f"SELECT {cols_sql} FROM {entidad}"
                cursor.execute(sql)
                
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Error de búsqueda: {e}")
            return []