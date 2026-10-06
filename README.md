# 🔧 Sistema de Gestión de Taller Mecánico

Sistema de escritorio desarrollado en **Python** con interfaz gráfica **Tkinter** y base de datos **MySQL** (XAMPP). Permite administrar usuarios, clientes, vehículos, reparaciones y piezas de un taller mecánico.

---

## 📋 Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- **Python 3.8** o superior → [Descargar Python](https://www.python.org/downloads/)
- **XAMPP** (con MySQL) → [Descargar XAMPP](https://www.apachefriends.org/es/index.html)
- **Git** → [Descargar Git](https://git-scm.com/downloads)

### Instalación de dependencias de Python

Abre una terminal y ejecuta:

```bash
pip install mysql-connector-python
```

---

## 🚀 Instalación y Configuración

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/izagod0/TALLER-MECANICO.git
cd TALLER-MECANICO
```

### Paso 2: Iniciar XAMPP

Abre el **Panel de Control de XAMPP** (como administrador) y arranca los servicios:

- ✅ **Apache**
- ✅ **MySQL**

### Paso 3: Configurar la base de datos

Abre phpMyAdmin en tu navegador:

```
http://localhost/phpmyadmin
```

Ve a la pestaña **SQL** y ejecuta **todo el siguiente bloque**:

```sql
-- ============================================
-- SISTEMA DE GESTIÓN DE TALLER MECÁNICO
-- Script de creación de base de datos
-- ============================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS taller_mecanico
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

-- Usar la base de datos
USE taller_mecanico;

-- ============================================
-- TABLA: Usuarios
-- ============================================
CREATE TABLE IF NOT EXISTS Usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Contrasena VARCHAR(100) NOT NULL,
    Tipo VARCHAR(50) NOT NULL
);

-- ============================================
-- TABLA: Clientes
-- ============================================
CREATE TABLE IF NOT EXISTS Clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Ap VARCHAR(100) NOT NULL,
    Am VARCHAR(100) NOT NULL
);

-- ============================================
-- TABLA: Vehiculos
-- ============================================
CREATE TABLE IF NOT EXISTS vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Matricula VARCHAR(50) NOT NULL,
    Modelo VARCHAR(100) NOT NULL,
    Marca VARCHAR(100) NOT NULL,
    cliente_id INT NULL,
    Color VARCHAR(50) NULL,
    FOREIGN KEY (cliente_id) REFERENCES Clientes(id) ON DELETE SET NULL
);

-- ============================================
-- TABLA: Reparaciones
-- ============================================
CREATE TABLE IF NOT EXISTS Reparaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    FechaEntrada VARCHAR(50),
    FechaSalida VARCHAR(50),
    Falla TEXT,
    numero_piezas INT
);

-- ============================================
-- TABLA: Piezas
-- ============================================
CREATE TABLE IF NOT EXISTS Piezas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Descripcion VARCHAR(200) NOT NULL,
    Stock INT NOT NULL
);

-- ============================================
-- USUARIO ADMINISTRADOR POR DEFECTO
-- ============================================
INSERT INTO Usuarios (Nombre, Username, Contrasena, Tipo)
VALUES ('Administrador', 'admin', 'admin', 'Administrador');
```

### Paso 4: Verificar la instalación

Ejecuta este comando en la pestaña SQL para verificar que todo quedó bien:

```sql
USE taller_mecanico;
SHOW TABLES;
DESCRIBE vehiculos;
```

Debes ver **5 tablas** (`Usuarios`, `Clientes`, `vehiculos`, `Reparaciones`, `Piezas`) y la tabla `vehiculos` debe tener **6 columnas**:

| Campo | Tipo | Nulo | Clave |
|-------|------|------|-------|
| id | int | NO | PRI |
| Matricula | varchar(50) | NO | |
| Modelo | varchar(100) | NO | |
| Marca | varchar(100) | NO | |
| cliente_id | int | YES | MUL |
| Color | varchar(50) | YES | |

### Paso 5: Ejecutar el programa

```bash
python main.py
```

### Credenciales de acceso por defecto

| Usuario | Contraseña |
|---------|------------|
| `admin`  | `admin`    |

---

## ⚠️ Actualización de Base de Datos (Versiones Anteriores)

Si ya tenías una versión anterior del proyecto y la tabla `vehiculos` **no tiene** las columnas `cliente_id` y `Color`, ejecuta los siguientes comandos en phpMyAdmin para actualizarla **sin perder datos**:

```sql
USE taller_mecanico;

-- Agregar columna cliente_id
ALTER TABLE vehiculos ADD COLUMN cliente_id INT NULL;

-- Agregar columna Color
ALTER TABLE vehiculos ADD COLUMN Color VARCHAR(50) NULL;

-- Agregar la clave foránea hacia Clientes
ALTER TABLE vehiculos
ADD CONSTRAINT fk_vehiculo_cliente
FOREIGN KEY (cliente_id) REFERENCES Clientes(id)
ON DELETE SET NULL;
```

Para verificar que los cambios se aplicaron:

```sql
DESCRIBE vehiculos;
```

---

## 🔧 Configuración de la Conexión

Si tu MySQL tiene contraseña o usa un puerto distinto, edita el archivo **`modelo.py`** en la sección `__init__`:

```python
self.conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",              # <-- Cambia si tu MySQL tiene contraseña
    database="taller_mecanico"
)
```

---

## 📁 Estructura del Proyecto

```
TALLER-MECANICO/
│
├── main.py                     # Punto de entrada del programa
├── modelo.py                   # Lógica de base de datos y conexión
├── controlador.py              # Lógica de control y eventos
├── .gitignore                  # Archivos ignorados por Git
├── README.md                   # Este archivo
│
└── vista/
    ├── __init__.py
    ├── vista_principal.py      # Ventana principal y login
    └── panel_formulario.py     # Formulario genérico de módulos
```

---

## 🛠️ Solución de Problemas Comunes

### ❌ Error: "MySQL shutdown unexpectedly" en XAMPP

Si MySQL no arranca, sigue estos pasos:

1. Cierra XAMPP completamente.
2. Abre el Administrador de Tareas (`Ctrl + Shift + Esc`) y finaliza cualquier proceso llamado `mysqld.exe`.
3. Ve a la carpeta `C:\xampp\mysql\`.
4. Renombra la carpeta `data` a `data_old`.
5. Copia la carpeta `backup` y renómbrala a `data`.
6. Copia tus bases de datos desde `data_old` hacia la nueva carpeta `data`.
7. Copia el archivo `ibdata1` desde `data_old` hacia `data`.
8. Abre XAMPP como administrador e inicia MySQL.

### ❌ Error: "Unknown column 'cliente_id' in 'field list'"

Significa que la tabla `vehiculos` no tiene la columna. Ejecuta los comandos de la sección **"Actualización de Base de Datos"**.

### ❌ Error: "No se estableció la conexión: los parámetros están incorrectos"

Verifica que:

- MySQL esté corriendo en XAMPP (ícono verde).
- La base de datos `taller_mecanico` exista.
- El usuario y contraseña en `modelo.py` coincidan con tu configuración de MySQL.

### ❌ Error: "Access denied for user 'root'@'localhost'"

Si tu MySQL tiene contraseña, agrégala en `modelo.py`:

```python
password="tu_contraseña_aqui",
```

---

## 📤 Subir cambios a Git

Flujo básico para actualizar el repositorio:

```bash
git status                              # Ver qué cambió
git add .                               # Agregar todos los cambios
git commit -m "Descripción de cambios"  # Confirmar cambios
git push origin main                    # Subir a GitHub
```

---

## 👨‍💻 Autor

**izagod0** - [@izagod0](https://github.com/izagod0)

Repositorio: [https://github.com/izagod0/TALLER-MECANICO](https://github.com/izagod0/TALLER-MECANICO)

---

## 📄 Licencia

Este proyecto es de uso libre para fines educativos.