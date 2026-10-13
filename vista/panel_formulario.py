import tkinter as tk
from tkinter import ttk

class PanelFormulario(tk.Frame):
    def __init__(self, parent, titulo, campos, controlador_formulario, columnas_tabla, cfg):
        super().__init__(parent, bg="white")
        self.controlador = controlador_formulario
        self.entradas = {}
        self.campos = campos

        mostrar_id = cfg["modo_id"] == "auto"
        etiquetas = cfg.get("etiquetas", {})
        largos = cfg.get("largos", [])

        lbl_titulo = tk.Label(self, text=f"Módulo: {titulo}", bg="white", font=("Arial", 16, "bold"))
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        fila0 = 1

        # Campo ID (solo lectura): muestra el ID que tendrá el nuevo registro
        self.entrada_id = None
        if mostrar_id:
            tk.Label(self, text="ID:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.entrada_id = tk.Entry(self, width=30, state="readonly")
            self.entrada_id.grid(row=1, column=1, sticky="w", padx=5, pady=2)
            fila0 = 2

        for i, nombre_campo in enumerate(campos):
            fila = fila0 + i
            nombre_limpio = nombre_campo.replace("txt", "").replace("cmb", "")
            texto_etiqueta = etiquetas.get(nombre_campo, nombre_limpio)

            lbl = tk.Label(self, text=texto_etiqueta + ":", bg="white", font=("Arial", 10))
            lbl.grid(row=fila, column=0, sticky="e", padx=5, pady=2)

            if "tipo" in nombre_campo.lower():
                ent = ttk.Combobox(self, width=28, values=["Administrador", "Mecanico", "Auxiliar"], state="readonly")
            elif "contrasena" in nombre_campo.lower() or "password" in nombre_campo.lower():
                ent = tk.Entry(self, width=30, show="*")
            elif nombre_campo.startswith("cmb"):
                ent = ttk.Combobox(self, width=42, state="readonly")
            else:
                ent = tk.Entry(self, width=50 if nombre_campo in largos else 30)

            ent.grid(row=fila, column=1, sticky="w", padx=5, pady=2)
            self.entradas[nombre_campo] = ent

        frame_botones = tk.Frame(self, bg="white")
        frame_botones.grid(row=fila0 + len(campos), column=0, columnspan=2, pady=15)

        self.btnNuevo = tk.Button(frame_botones, text="Nuevo", width=10, command=lambda: self.controlador.accion("NUEVO"))
        self.btnSalvar = tk.Button(frame_botones, text="Salvar", width=10, command=lambda: self.controlador.accion("SALVAR"))
        self.btnCancelar = tk.Button(frame_botones, text="Cancelar", width=10, command=lambda: self.controlador.accion("CANCELAR"))
        self.btnEditar = tk.Button(frame_botones, text="Editar", width=10, command=lambda: self.controlador.accion("EDITAR"))
        self.btnRemover = tk.Button(frame_botones, text="Remover", width=10, command=lambda: self.controlador.accion("REMOVER"))
        self.btnBuscar = tk.Button(frame_botones, text="Buscar", width=10, command=lambda: self.controlador.accion("BUSCAR"))

        self.btnNuevo.grid(row=0, column=0, padx=5)
        self.btnSalvar.grid(row=0, column=1, padx=5)
        self.btnCancelar.grid(row=0, column=2, padx=5)
        self.btnEditar.grid(row=0, column=3, padx=5)
        self.btnRemover.grid(row=0, column=4, padx=5)
        self.btnBuscar.grid(row=0, column=5, padx=5)

        # Botones extra del módulo (ej. "Piezas usadas" en Reparaciones): se activan al buscar
        self.botones_extra = []
        for i, (texto, clave) in enumerate(cfg.get("acciones_extra", [])):
            btn = tk.Button(frame_botones, text=texto, width=13, command=lambda c=clave: self.controlador.accion(c))
            btn.grid(row=0, column=6 + i, padx=5)
            self.botones_extra.append(btn)

        self.fila_busqueda = fila0 + len(campos) + 1
        self.frame_busqueda = tk.Frame(self, bg="white")

        frame_bar = tk.Frame(self.frame_busqueda, bg="white")
        frame_bar.pack(fill=tk.X, pady=5)
        tk.Label(frame_bar, text=cfg.get("etiqueta_busqueda", "Escribe para filtrar:"), bg="white").pack(side=tk.LEFT)

        self.txtBuscador = tk.Entry(frame_bar, width=40)
        self.txtBuscador.pack(side=tk.LEFT, padx=5)
        self.txtBuscador.bind("<KeyRelease>", lambda event: self.controlador.buscar_en_tiempo_real(self.txtBuscador.get()))

        frame_tabla = tk.Frame(self.frame_busqueda, bg="white")
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        self.tabla = ttk.Treeview(frame_tabla, columns=columnas_tabla, show="headings", height=7)
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)

        anchos = cfg.get("anchos_tabla", {})
        for col in columnas_tabla:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=anchos.get(col, 90), anchor=tk.CENTER)

        self.tabla.tag_configure("bajo", background="#fdecea", foreground="#b71c1c")

        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        if cfg.get("resaltar"):
            tk.Label(self.frame_busqueda, text="Las filas en rojo tienen stock igual o menor al mínimo.",
                     bg="white", fg="#b71c1c", font=("Arial", 9)).pack(anchor="w", pady=(4, 0))

        self.actualizar_estado("INICIAL")

    def mostrar_id(self, valor):
        """Escribe el ID en la caja de solo lectura."""
        if self.entrada_id is None:
            return
        self.entrada_id.config(state=tk.NORMAL)
        self.entrada_id.delete(0, tk.END)
        self.entrada_id.insert(0, str(valor))
        self.entrada_id.config(state="readonly")

    def actualizar_estado(self, estado):
        estado_campos = tk.DISABLED
        estado_extra = tk.DISABLED

        if estado in ["NUEVO", "EDITAR"]:
            estado_campos = tk.NORMAL
            self.btnNuevo.config(state=tk.DISABLED)
            self.btnSalvar.config(state=tk.NORMAL)
            self.btnCancelar.config(state=tk.NORMAL)
            self.btnEditar.config(state=tk.DISABLED)
            self.btnRemover.config(state=tk.DISABLED)

        elif estado in ["SALVAR", "CANCELAR", "REMOVER", "INICIAL"]:
            estado_campos = tk.DISABLED
            self.btnNuevo.config(state=tk.NORMAL)
            self.btnSalvar.config(state=tk.DISABLED)
            self.btnCancelar.config(state=tk.DISABLED)
            self.btnEditar.config(state=tk.DISABLED)
            self.btnRemover.config(state=tk.DISABLED)
            self.frame_busqueda.grid_forget()

        elif estado == "BUSCAR":
            estado_campos = tk.DISABLED
            estado_extra = tk.NORMAL
            self.btnNuevo.config(state=tk.DISABLED)
            self.btnSalvar.config(state=tk.DISABLED)
            self.btnCancelar.config(state=tk.DISABLED)
            self.btnEditar.config(state=tk.NORMAL)
            self.btnRemover.config(state=tk.NORMAL)

            self.frame_busqueda.grid(row=self.fila_busqueda, column=0, columnspan=2, sticky="nsew", pady=10)
            self.txtBuscador.delete(0, tk.END)
            self.controlador.buscar_en_tiempo_real("")

        for boton in self.botones_extra:
            boton.config(state=estado_extra)

        if estado in ["CANCELAR", "SALVAR", "REMOVER", "NUEVO"]:
            self.mostrar_id("")
            for entrada in self.entradas.values():
                if isinstance(entrada, ttk.Combobox):
                    entrada.config(state="normal")
                    entrada.set("")
                else:
                    entrada.config(state=tk.NORMAL)
                    entrada.delete(0, tk.END)

        for entrada in self.entradas.values():
            if isinstance(entrada, ttk.Combobox):
                entrada.config(state="readonly" if estado_campos == tk.NORMAL else tk.DISABLED)
            else:
                entrada.config(state=estado_campos)
