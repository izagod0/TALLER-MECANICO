import tkinter as tk
from tkinter import ttk


def _dinero(valor):
    return f"${float(valor):,.2f}"


class DialogoPiezas(tk.Toplevel):
    """Ventana para ver, agregar y quitar las piezas usadas en una reparación."""

    def __init__(self, parent, controlador, resumen):
        super().__init__(parent)
        self.controlador = controlador
        self.title("Piezas usadas en la reparación")
        self.geometry("680x560")
        self.configure(bg="white")
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.controlador.cerrar)

        tk.Label(self, text=resumen, bg="white", font=("Arial", 12, "bold")).pack(pady=(15, 5), padx=15, anchor="w")
        self.lbl_aviso = tk.Label(self, text="", bg="white", fg="#b71c1c", font=("Arial", 9))
        self.lbl_aviso.pack(padx=15, anchor="w")

        # Tabla de piezas ya usadas
        frame_tabla = tk.Frame(self, bg="white")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columnas = ("ID", "Pieza", "Cantidad", "Precio", "Subtotal")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)
        anchos = {"ID": 50, "Pieza": 250, "Cantidad": 80, "Precio": 100, "Subtotal": 100}
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=anchos[col], anchor=tk.CENTER)
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_quitar = tk.Button(self, text="Quitar pieza seleccionada", command=self.controlador.quitar)
        self.btn_quitar.pack(anchor="e", padx=15, pady=(0, 8))

        # Formulario para agregar una pieza
        frame_agregar = tk.LabelFrame(self, text=" Agregar pieza ", bg="white", padx=10, pady=8)
        frame_agregar.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_agregar, text="Pieza:", bg="white").grid(row=0, column=0, sticky="e", padx=5)
        self.cmb_piezas = ttk.Combobox(frame_agregar, width=45, state="readonly")
        self.cmb_piezas.grid(row=0, column=1, padx=5)

        tk.Label(frame_agregar, text="Cantidad:", bg="white").grid(row=0, column=2, sticky="e", padx=5)
        self.spin_cantidad = tk.Spinbox(frame_agregar, from_=1, to=9999, width=6)
        self.spin_cantidad.grid(row=0, column=3, padx=5)

        self.btn_agregar = tk.Button(frame_agregar, text="Agregar", width=10, command=self.controlador.agregar)
        self.btn_agregar.grid(row=0, column=4, padx=8)

        # Totales
        frame_totales = tk.Frame(self, bg="white")
        frame_totales.pack(fill=tk.X, padx=15, pady=10)
        self.lbl_mano = tk.Label(frame_totales, text="Mano de obra: $0.00", bg="white", font=("Arial", 10))
        self.lbl_piezas = tk.Label(frame_totales, text="Piezas: $0.00", bg="white", font=("Arial", 10))
        self.lbl_total = tk.Label(frame_totales, text="Total: $0.00", bg="white", font=("Arial", 12, "bold"))
        self.lbl_mano.pack(side=tk.LEFT, padx=(0, 20))
        self.lbl_piezas.pack(side=tk.LEFT, padx=(0, 20))
        self.lbl_total.pack(side=tk.RIGHT)

        tk.Button(self, text="Cerrar", width=12, command=self.controlador.cerrar).pack(pady=(0, 15))

        # Ventana modal (si la plataforma no deja capturar el foco, simplemente no es modal)
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass

    # ---------- Métodos que usa el controlador ----------
    def cargar_disponibles(self, opciones):
        self.cmb_piezas.config(values=opciones)
        self.cmb_piezas.set("")

    def cargar_usadas(self, filas):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for pieza_id, descripcion, cantidad, precio, subtotal in filas:
            self.tabla.insert("", tk.END, iid=str(pieza_id),
                              values=(pieza_id, descripcion, cantidad, _dinero(precio), _dinero(subtotal)))

    def mostrar_totales(self, mano_obra, total_piezas):
        self.lbl_mano.config(text=f"Mano de obra: {_dinero(mano_obra)}")
        self.lbl_piezas.config(text=f"Piezas: {_dinero(total_piezas)}")
        self.lbl_total.config(text=f"Total: {_dinero(mano_obra + total_piezas)}")

    def pieza_elegida(self):
        return self.cmb_piezas.get().strip()

    def cantidad(self):
        return self.spin_cantidad.get().strip()

    def pieza_seleccionada_en_tabla(self):
        seleccion = self.tabla.selection()
        return seleccion[0] if seleccion else None

    def reiniciar_cantidad(self):
        self.spin_cantidad.delete(0, tk.END)
        self.spin_cantidad.insert(0, "1")

    def bloquear(self, motivo):
        """Deja la ventana en modo solo lectura."""
        self.lbl_aviso.config(text=motivo)
        self.btn_agregar.config(state=tk.DISABLED)
        self.btn_quitar.config(state=tk.DISABLED)
        self.cmb_piezas.config(state=tk.DISABLED)
        self.spin_cantidad.config(state=tk.DISABLED)
