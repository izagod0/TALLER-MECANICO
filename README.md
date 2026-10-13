# 🔧 Sistema de Gestión de Taller Mecánico

Sistema de escritorio desarrollado en **Python** con interfaz gráfica **Tkinter** y base de datos **MySQL** (XAMPP). Permite administrar usuarios, clientes, vehículos, reparaciones y piezas de un taller mecánico, con acceso diferenciado según el rol de cada usuario.

---

## ✨ Funcionalidades

- **Inicio de sesión** con barra superior que muestra usuario, ID y rol.
- **Acceso por rol** (ver tabla más abajo).
- **Usuarios** y **Clientes** con ID autoincremental visible (si ya hay 3, el nuevo es el 4).
- **Vehículos** identificados por su matrícula, asignados a un cliente existente, con buscador por matrícula.
- **Reparaciones** con vehículo, mecánico, estado, fechas, falla, diagnóstico y mano de obra.
- **Piezas usadas** por reparación: descuentan stock al agregarse y lo devuelven al quitarse.
- **Inventario de piezas** con precio, stock y alerta de stock bajo (filas en rojo).

### 🔐 Permisos por rol

| Rol | Módulos a los que tiene acceso |
|-----|-------------------------------|
| **Administrador** | Usuarios, Clientes, Vehículos, Reparaciones, Piezas |
| **Mecánico** | Reparaciones, Piezas |
| **Auxiliar** | Clientes, Vehículos |

El rol sale del campo `Tipo` de la tabla `Usuarios` (`Administrador`, `Mecanico` o `Auxiliar`). Los permisos se pueden cambiar en `permisos.py`.

---

## 📋 Requisitos Previos

- **Python 3.8** o superior → [Descargar Python](https://www.python.org/downloads/)
- **XAMPP** (con MySQL) → [Descargar XAMPP](https://www.apachefriends.org/es/index.html)
- **Git** → [Descargar Git](https://git-scm.com/downloads)

### Instalación de dependencias de Python

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

### Paso 3: Crear la base de datos

Abre phpMyAdmin en tu navegador:

```
http://localhost/phpmyadmin
```

Ve a la pestaña **SQL** y ejecuta **todo el siguiente bloque** (es el mismo contenido del archivo `base_de_datos.sql` del repositorio, que también puedes importar desde la pestaña *Importar*):

```sql
-- ============================================
-- SISTEMA DE GESTIÓN DE TALLER MECÁNICO
-- Script de creación de la base de datos (6 tablas)
-- ============================================

CREATE DATABASE IF NOT EXISTS taller_mecanico
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE taller_mecanico;

-- TABLA: Usuarios
CREATE TABLE IF NOT EXISTS Usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Contrasena VARCHAR(100) NOT NULL,
    Tipo VARCHAR(50) NOT NULL,
    Telefono VARCHAR(15) NULL
);

-- TABLA: Clientes
CREATE TABLE IF NOT EXISTS Clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Domicilio VARCHAR(150) NULL,
    Telefono VARCHAR(15) NULL,
    RFC VARCHAR(13) NULL
);

-- TABLA: Vehiculos (la matrícula es la llave primaria)
CREATE TABLE IF NOT EXISTS Vehiculos (
    Matricula VARCHAR(15) NOT NULL PRIMARY KEY,
    Modelo VARCHAR(50) NOT NULL,
    Marca VARCHAR(50) NOT NULL,
    Fecha DATE NULL,
    cliente_id INT NULL,
    FOREIGN KEY (cliente_id) REFERENCES Clientes(id)
);

-- TABLA: Piezas (inventario)
CREATE TABLE IF NOT EXISTS Piezas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Descripcion VARCHAR(200) NOT NULL,
    Precio DECIMAL(10,2) NOT NULL DEFAULT 0,
    Stock INT NOT NULL DEFAULT 0,
    StockMinimo INT NOT NULL DEFAULT 5
);

-- TABLA: Reparaciones
CREATE TABLE IF NOT EXISTS Reparaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Matricula VARCHAR(15) NULL,
    mecanico_id INT NULL,
    Estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    FechaEntrada DATE NULL,
    FechaSalida DATE NULL,
    Falla TEXT NULL,
    Diagnostico VARCHAR(255) NULL,
    CostoManoObra DECIMAL(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_rep_vehiculo FOREIGN KEY (Matricula) REFERENCES Vehiculos(Matricula),
    CONSTRAINT fk_rep_mecanico FOREIGN KEY (mecanico_id) REFERENCES Usuarios(id) ON DELETE SET NULL
);

-- TABLA: ReparacionPiezas (piezas usadas en cada reparación)
CREATE TABLE IF NOT EXISTS ReparacionPiezas (
    reparacion_id INT NOT NULL,
    pieza_id INT NOT NULL,
    Cantidad INT NOT NULL,
    PrecioUnitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (reparacion_id, pieza_id),
    FOREIGN KEY (reparacion_id) REFERENCES Reparaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (pieza_id) REFERENCES Piezas(id)
);

-- USUARIO ADMINISTRADOR POR DEFECTO
INSERT IGNORE INTO Usuarios (Nombre, Username, Contrasena, Tipo, Telefono)
VALUES ('Administrador', 'admin', 'admin', 'Administrador', '0000000000');
```

### 🗂️ Resumen de las tablas

| Tabla | Para qué sirve | Llave primaria | Relaciones |
|-------|----------------|----------------|------------|
| `Usuarios` | Personal del taller y su rol (`Tipo`) | `id` | — |
| `Clientes` | Dueños de los vehículos | `id` | — |
| `Vehiculos` | Vehículos registrados | `Matricula` | `cliente_id` → `Clientes.id` |
| `Piezas` | Inventario con precio y stock mínimo | `id` | — |
| `Reparaciones` | Trabajos del taller | `id` | `Matricula` → `Vehiculos`, `mecanico_id` → `Usuarios` |
| `ReparacionPiezas` | Piezas usadas en cada reparación | `reparacion_id` + `pieza_id` | → `Reparaciones`, → `Piezas` |

```
Clientes 1───N Vehiculos 1───N Reparaciones N───1 Usuarios (mecánico)
                                    │
                                    └──N ReparacionPiezas N───1 Piezas
```

### Paso 4: Verificar la instalación

```sql
USE taller_mecanico;
SHOW TABLES;
DESCRIBE Vehiculos;
```

Debes ver **6 tablas** (`Usuarios`, `Clientes`, `Vehiculos`, `Piezas`, `Reparaciones`, `ReparacionPiezas`) y la tabla `Vehiculos` debe tener **5 columnas**:

| Campo | Tipo | Nulo | Clave |
|-------|------|------|-------|
| Matricula | varchar(15) | NO | PRI |
| Modelo | varchar(50) | NO | |
| Marca | varchar(50) | NO | |
| Fecha | date | YES | |
| cliente_id | int | YES | MUL |

### Paso 5: Ejecutar el programa

```bash
python main.py
```

### Credenciales de acceso por defecto

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin`    | Administrador |

Para probar los roles, entra con `admin`, ve a **File → Usuarios** y crea un usuario de tipo `Mecanico` y otro `Auxiliar` (o descomenta los usuarios de prueba al final de `base_de_datos.sql`). Después usa **File → Cerrar sesión** para entrar con ellos.

---

## ⚠️ Actualización de Base de Datos (Versiones Anteriores)

Si ya tenías una versión anterior con datos que quieres conservar, ejecuta **en este orden** en phpMyAdmin (pestaña SQL de `taller_mecanico`):

1. `cambios_base_de_datos.sql` → agrega `Telefono` a Usuarios, cambia Clientes (Nombre, Domicilio, Teléfono, RFC) y deja la matrícula como llave primaria de Vehículos.
2. `cambios_base_de_datos_v2.sql` → agrega precio/stock mínimo a Piezas, amplía Reparaciones y crea `ReparacionPiezas`.

> ⚠️ Estos scripts eliminan las columnas `Ap`, `Am` (Clientes), `id` y `Color` (Vehículos) y `numero_piezas` (Reparaciones). Si hay datos que quieras conservar, respáldalos antes (phpMyAdmin → Exportar). Los comentarios dentro de cada archivo explican cada bloque.

Si solo tienes **datos de prueba**, es más rápido borrar todo y empezar limpio:

```sql
DROP DATABASE taller_mecanico;
```

y luego ejecutar de nuevo el bloque del **Paso 3**.

---

## 🔧 Configuración de la Conexión

Si tu MySQL tiene contraseña o usa un puerto distinto, edita el archivo **`modelo.py`** en la sección `__init__`:

```python
self.conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",              # <-- Cambia si tu MySQL tiene contraseña
    database="taller_mecanico",
    autocommit=True,
)
```

---

## 📁 Estructura del Proyecto

```
TALLER-MECANICO/
│
├── main.py                          # Punto de entrada del programa
├── modelo.py                        # Base de datos, consultas y configuración de cada módulo
├── controlador.py                   # Lógica de control y eventos
├── permisos.py                      # Qué módulos puede usar cada rol
├── base_de_datos.sql                # Script para crear la base de datos desde cero
├── cambios_base_de_datos.sql        # Actualización 1 (Usuarios, Clientes, Vehículos)
├── cambios_base_de_datos_v2.sql     # Actualización 2 (Reparaciones, Piezas)
├── .gitignore                       # Archivos ignorados por Git
├── README.md                        # Este archivo
│
└── vista/
    ├── __init__.py
    ├── vista_principal.py           # Ventana principal, login y barra de sesión
    ├── panel_formulario.py          # Formulario genérico de módulos
    └── dialogo_piezas.py            # Ventana de piezas usadas en una reparación
```

---

## 🛠️ Solución de Problemas Comunes

### ❌ `ModuleNotFoundError: No module named 'vista.dialogo_piezas'`

Falta el archivo `dialogo_piezas.py` dentro de la carpeta `vista/`. Cópialo ahí (junto a `vista_principal.py` y `panel_formulario.py`).

### ❌ `ModuleNotFoundError: No module named 'permisos'`

Falta `permisos.py`. Debe estar en la carpeta principal, junto a `main.py`.

### ❌ Error: "Unknown column '...' in 'field list'"

La base de datos no tiene alguna columna nueva (por ejemplo `Telefono`, `Fecha`, `Estado`, `Precio`). Ejecuta los scripts de la sección **"Actualización de Base de Datos"** o recrea la base con el **Paso 3**.

### ❌ Error al crear llaves foráneas ("errno 150" / "incompatible")

Verifica que `Usuarios.id`, `Clientes.id`, `Piezas.id` y `Reparaciones.id` sean `INT` (sin `UNSIGNED`) y que `Vehiculos.Matricula` sea `VARCHAR(15)`, igual que las columnas que la referencian.

### ❌ "No se puede eliminar" al borrar un registro

El registro está relacionado con otros (un cliente con vehículos, un vehículo con reparaciones o una pieza usada en una reparación). Elimina o reasigna primero los registros relacionados.

### ❌ Error: "MySQL shutdown unexpectedly" en XAMPP

1. Cierra XAMPP completamente.
2. Abre el Administrador de Tareas (`Ctrl + Shift + Esc`) y finaliza cualquier proceso llamado `mysqld.exe`.
3. Ve a la carpeta `C:\xampp\mysql\`.
4. Renombra la carpeta `data` a `data_old`.
5. Copia la carpeta `backup` y renómbrala a `data`.
6. Copia tus bases de datos desde `data_old` hacia la nueva carpeta `data`.
7. Copia el archivo `ibdata1` desde `data_old` hacia `data`.
8. Abre XAMPP como administrador e inicia MySQL.

### ❌ Error: "No se estableció la conexión: los parámetros están incorrectos"

- MySQL esté corriendo en XAMPP (ícono verde).
- La base de datos `taller_mecanico` exista.
- El usuario y contraseña en `modelo.py` coincidan con tu configuración de MySQL.

### ❌ Error: "Access denied for user 'root'@'localhost'"

Si tu MySQL tiene contraseña, agrégala en `modelo.py`:

```python
password="tu_contraseña_aqui",
```

---

## 📤 Subir el proyecto a Git / GitHub

### Primera vez (si la carpeta todavía no es un repositorio)

1. Crea un repositorio vacío en GitHub (sin README ni .gitignore).
2. Abre una terminal **dentro de la carpeta del proyecto** y ejecuta:

```bash
git init
git branch -M main
git remote add origin https://github.com/izagod0/TALLER-MECANICO.git
```

3. Configura tu nombre y correo (solo una vez en tu computadora):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

4. Asegúrate de que exista un archivo `.gitignore` con al menos:

```
__pycache__/
*.pyc
.vscode/
```

5. Sube todo:

```bash
git add .
git commit -m "Taller mecánico: roles, reparaciones y piezas"
git push -u origin main
```

### Cada vez que hagas cambios

```bash
git status                                  # Ver qué cambió
git add .                                   # Agregar todos los cambios
git commit -m "Descripción de los cambios"  # Confirmar cambios
git push origin main                        # Subir a GitHub
```

### Problemas comunes al subir

- **Piden usuario y contraseña:** GitHub ya no acepta la contraseña de la cuenta. Inicia sesión por el navegador cuando Git lo ofrezca, o usa un *Personal Access Token* (GitHub → Settings → Developer settings → Personal access tokens) como contraseña.
- **`rejected ... fetch first` / `non-fast-forward`:** el repositorio en GitHub tiene cambios que no tienes localmente. Ejecuta `git pull --rebase origin main` y luego `git push origin main`.
- **`remote origin already exists`:** ya está configurado el remoto. Revísalo con `git remote -v`; si está mal, corrígelo con `git remote set-url origin https://github.com/izagod0/TALLER-MECANICO.git`.
- **Verifica que subiste todo:** abre el repositorio en GitHub y confirma que aparecen `permisos.py` y `vista/dialogo_piezas.py`.

---

## 📝 Notas

- Las contraseñas se guardan en texto plano en la tabla `Usuarios`: el proyecto es de uso educativo y no está pensado para producción.
- Todos los comandos SQL del programa usan parámetros, por lo que los datos capturados no se concatenan en las consultas.

---

## 👨‍💻 Autor

**izagod0** - [@izagod0](https://github.com/izagod0)

Repositorio: [https://github.com/izagod0/TALLER-MECANICO](https://github.com/izagod0/TALLER-MECANICO)

---

## 📄 Licencia

Este proyecto es de uso libre para fines educativos.
