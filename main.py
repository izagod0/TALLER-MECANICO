# main.py
from modelo import ModeloPrincipal
from vista.vista_principal import VistaPrincipal
from controlador import ControladorPrincipal

def main():
    # Inicializar el Modelo
    modelo = ModeloPrincipal()
    
    # Inicializar la Vista Principal
    vista = VistaPrincipal()
    
    # Inicializar el Controlador Principal
    controlador = ControladorPrincipal(modelo, vista)
    
    # Arrancar la aplicación
    vista.mainloop()

if __name__ == "__main__":
    main()