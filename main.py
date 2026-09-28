# main.py
from modelo import ModeloPrincipal
from vista import VistaPrincipal
from controlador import ControladorPrincipal

def main():
    # Inicializar el Modelo
    modelo = ModeloPrincipal()
    
    # Inicializar la Vista
    vista = VistaPrincipal()
    
    # Inicializar el Controlador y conectar Modelo y Vista
    controlador = ControladorPrincipal(modelo, vista)
    
    # Arrancar la aplicación
    vista.mainloop()

if __name__ == "__main__":
    main()