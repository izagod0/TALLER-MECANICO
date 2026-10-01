# vista/vista_principal.py
import tkinter as tk

class VistaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión")
        self.geometry("750x650")
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