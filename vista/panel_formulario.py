# vista/panel_formulario.py
import tkinter as tk
from tkinter import ttk

class PanelFormulario(tk.Frame):
    def __init__(self, parent, titulo, campos, controlador_formulario):
        super().__init__(parent, bg="white")
        self.controlador = controlador_formulario
        self.entradas = {}
        self.campos = campos
        
        lbl_titulo = tk.Label(self, text=f"Módulo: {titulo}", bg="white", font=("Arial", 16, "bold"))
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Generar campos del formulario
        for i, nombre_campo in enumerate(campos):
            nombre_limpio = nombre_campo.replace("txt", "").replace("cmb", "")
            lbl = tk.Label(self, text=nombre_limpio + ":", bg="white", font=("Arial", 10))
            lbl.grid(row=i+1, column=0, sticky="e", padx=5, pady=2)
            
            if "tipo" in nombre_campo.lower():
                ent = ttk.Combobox(self, width=28, values=["Administrador", "Mecanico", "Auxiliar"], state="readonly")
                ent.grid(row=i+1, column=1, sticky="w", padx=5, pady=2)
                self.entradas[nombre_campo] = ent
            elif "contrasena" in nombre_campo.lower() or "password" in nombre_campo.lower():
                ent = tk.Entry(self, width=30, show="*")
                ent.grid(row=i+1, column=1, sticky="w", padx=5, pady=2)
                self.entradas[nombre_campo] = ent
            else:
                ent = tk.Entry(self, width=30)
                ent.grid(row=i+1, column=1, sticky="w", padx=5, pady=2)
                self.entradas[nombre_campo] = ent
            
        # Botones de acción
        frame_botones = tk.Frame(self, bg="white")
        frame_botones.grid(row=len(campos)+1, column=0, columnspan=2, pady=15)
        
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
        
        # Zona de búsqueda y tabla
        self.frame_busqueda = tk.Frame(self, bg="white")
        
        frame_bar = tk.Frame(self.frame_busqueda, bg="white")
        frame_bar.pack(fill=tk.X, pady=5)
        tk.Label(frame_bar, text="Escribe para filtrar:", bg="white").pack(side=tk.LEFT)
        
        self.txtBuscador = tk.Entry(frame_bar, width=40)
        self.txtBuscador.pack(side=tk.LEFT, padx=5)
        self.txtBuscador.bind("<KeyRelease>", lambda event: self.controlador.buscar_en_tiempo_real(self.txtBuscador.get()))

        columnas_tabla = [c.replace("txt", "").replace("cmb", "") for c in campos]
        if "ID" not in [col.upper() for col in columnas_tabla]:
            columnas_tabla.insert(0, "ID")
            
        self.tabla = ttk.Treeview(self.frame_busqueda, columns=columnas_tabla, show="headings", height=8)
        
        for col in columnas_tabla:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=90, anchor=tk.CENTER)
            
        self.tabla.pack(fill=tk.BOTH, expand=True)

        self.actualizar_estado("INICIAL")

    def actualizar_estado(self, estado):
        estado_campos = tk.DISABLED
        
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
            self.btnNuevo.config(state=tk.DISABLED)
            self.btnSalvar.config(state=tk.DISABLED)
            self.btnCancelar.config(state=tk.DISABLED)
            self.btnEditar.config(state=tk.NORMAL)
            self.btnRemover.config(state=tk.NORMAL)
            
            self.frame_busqueda.grid(row=len(self.campos)+2, column=0, columnspan=2, sticky="nsew", pady=10)
            self.txtBuscador.delete(0, tk.END)
            self.controlador.buscar_en_tiempo_real("")

        if estado in ["CANCELAR", "SALVAR", "REMOVER", "NUEVO"]:
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