# vista.py
import tkinter as tk
from tkinter import ttk, messagebox

class VistaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión")
        self.geometry("750x650") # Ampliado un poco para que quepa la tabla
        self.configure(bg="white")
        
        self.frame_contenido = tk.Frame(self, bg="white")
        self.frame_contenido.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self._crear_menu()

    def _crear_menu(self):
        barra_menu = tk.Menu(self)
        menu_file = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="File", menu=menu_file)
        self.menu_file = menu_file 
        self.config(menu=barra_menu)

    def limpiar_contenido(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

class PanelFormulario(tk.Frame):
    def __init__(self, parent, titulo, campos, controlador_formulario):
        super().__init__(parent, bg="white")
        self.controlador = controlador_formulario
        self.entradas = {}
        self.campos = campos
        
        lbl_titulo = tk.Label(self, text=f"Módulo: {titulo}", bg="white", font=("Arial", 16, "bold"))
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        for i, nombre_campo in enumerate(campos):
            lbl = tk.Label(self, text=nombre_campo.replace("txt", "") + ":", bg="white", font=("Arial", 10))
            lbl.grid(row=i+1, column=0, sticky="e", padx=5, pady=2)
            
            ent = tk.Entry(self, width=30)
            ent.grid(row=i+1, column=1, sticky="w", padx=5, pady=2)
            self.entradas[nombre_campo] = ent
            
        # Frame botones
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
        
        # --- ZONA DE BÚSQUEDA Y TABLA (Oculta por defecto) ---
        self.frame_busqueda = tk.Frame(self, bg="white")
        
        # Buscador superior de la tabla
        frame_bar = tk.Frame(self.frame_busqueda, bg="white")
        frame_bar.pack(fill=tk.X, pady=5)
        tk.Label(frame_bar, text="Escribe para filtrar:", bg="white").pack(side=tk.LEFT)
        
        self.txtBuscador = tk.Entry(frame_bar, width=40)
        self.txtBuscador.pack(side=tk.LEFT, padx=5)
        # Evento: Cada vez que se suelta una tecla, filtra
        self.txtBuscador.bind("<KeyRelease>", lambda event: self.controlador.buscar_en_tiempo_real(self.txtBuscador.get()))

        # Tabla Treeview
        columnas_tabla = ["ID"] + [c.replace("txt", "") for c in campos]
        self.tabla = ttk.Treeview(self.frame_busqueda, columns=columnas_tabla, show="headings", height=8)
        
        for col in columnas_tabla:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=90, anchor=tk.CENTER)
            
        self.tabla.pack(fill=tk.BOTH, expand=True)
        # -----------------------------------------------------

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
            self.frame_busqueda.grid_forget() # Ocultar tabla
            
        elif estado == "BUSCAR":
            estado_campos = tk.DISABLED
            self.btnNuevo.config(state=tk.DISABLED)
            self.btnSalvar.config(state=tk.DISABLED)
            self.btnCancelar.config(state=tk.DISABLED)
            self.btnEditar.config(state=tk.NORMAL)
            self.btnRemover.config(state=tk.NORMAL)
            
            # Mostrar la tabla
            self.frame_busqueda.grid(row=len(self.campos)+2, column=0, columnspan=2, sticky="nsew", pady=10)
            self.txtBuscador.delete(0, tk.END) # Limpiar barra
            self.controlador.buscar_en_tiempo_real("") # Cargar lista completa

        if estado in ["CANCELAR", "SALVAR", "REMOVER", "NUEVO"]:
            for entrada in self.entradas.values():
                entrada.config(state=tk.NORMAL) 
                entrada.delete(0, tk.END)
                
        for entrada in self.entradas.values():
            entrada.config(state=estado_campos)