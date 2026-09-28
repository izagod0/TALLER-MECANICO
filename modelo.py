# modelo.py
import mysql.connector
from tkinter import messagebox

ENTIDADES = {
    "Usuarios": ["txtNombre", "txtAp", "txtAm", "txtTelefono", "txtDireccion"],
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
            columnas = ", ".join([k.replace("txt", "") for k in datos.keys()])
            placeholders = ", ".join(["%s"] * len(datos))
            
            sql = f"INSERT INTO {entidad} ({columnas}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(datos.values()))
            self.conexion.commit()
            cursor.close()
            messagebox.showinfo("Éxito", f"Datos guardados en {entidad}.")
        except Exception as e:
            messagebox.showerror("Error SQL", f"Error al insertar:\n{e}")

    def buscar_datos(self, entidad, termino=""):
        """Busca coincidencias en cualquier columna de la tabla y devuelve los registros."""
        if not self.conexion: return []
        try:
            cursor = self.conexion.cursor()
            columnas = [k.replace("txt", "") for k in self.obtener_campos(entidad)]
            str_cols = ", ".join(columnas)
            
            if termino:
                # Crea la condición OR para buscar en todas las columnas (ej: Nombre LIKE %isa% OR Ap LIKE %isa%)
                condiciones = " OR ".join([f"{col} LIKE %s" for col in columnas])
                sql = f"SELECT id, {str_cols} FROM {entidad} WHERE {condiciones}"
                # Multiplicamos el término de búsqueda por la cantidad de columnas
                valores = tuple([f"%{termino}%"] * len(columnas))
                cursor.execute(sql, valores)
            else:
                # Si está vacío, trae todo
                sql = f"SELECT id, {str_cols} FROM {entidad}"
                cursor.execute(sql)
                
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Error de búsqueda: {e}")
            return []