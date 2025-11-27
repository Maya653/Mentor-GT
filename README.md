# Sistema de Gestión de CVs Académicos

Sistema MVC con Flask para gestión de currículums académicos con sincronización de APIs externas.

## 🚀 Inicio Rápido

1. Crear entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:

```bash
cp .env.example .env
```

4. Inicializar base de datos:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Ejecutar aplicación:

```bash
python run.py
```

## 👥 Usuarios por Defecto

**Administrador:**
- Email: admin@academic.com
- Password: admin123

**Profesor:**
- Email: profesor@academic.com
- Password: profesor123

## 📁 Estructura MVC

- **Models:** `app/models/`
- **Views:** `app/views/`
- **Controllers:** `app/controllers/`
- **Services:** `app/services/`

## 🔧 Tecnologías

- Flask 3.0
- SQLite3
- SQLAlchemy
- Jinja2
- Bootstrap 5
