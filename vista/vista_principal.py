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
        self.ocultar_menu()

    def _crear_menu(self):
        self.barra_menu = tk.Menu(self)
        self.menu_file = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="File", menu=self.menu_file)
        
    def ocultar_menu(self):
        self.config(menu="")
        
    def mostrar_menu(self):
        self.config(menu=self.barra_menu)

    def limpiar_contenido(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def crear_panel_login(self, comando_login):
        frame_login = tk.Frame(self.frame_contenido, bg="white")
        frame_login.pack(expand=True)
        
        tk.Label(frame_login, text="Inicio de Sesión", font=("Arial", 16, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=20)
        
        tk.Label(frame_login, text="Usuario:", bg="white").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        txt_user = tk.Entry(frame_login)
        txt_user.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame_login, text="Contraseña:", bg="white").grid(row=2, column=0, pady=5, padx=5, sticky="e")
        txt_pass = tk.Entry(frame_login, show="*")
        txt_pass.grid(row=2, column=1, pady=5, padx=5)
        
        btn_login = tk.Button(frame_login, text="Ingresar", command=lambda: comando_login(txt_user.get(), txt_pass.get()))
        btn_login.grid(row=3, column=0, columnspan=2, pady=20)