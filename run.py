from app import create_app, db
from app.models.usuario import Usuario

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Usuario': Usuario}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear usuario administrador por defecto
        if not Usuario.query.filter_by(email='admin@academic.com').first():
            admin = Usuario(
                email='admin@academic.com',
                nombre='Administrador',
                apellidos='Sistema',
                rol='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Crear usuario profesor por defecto
        if not Usuario.query.filter_by(email='profesor@academic.com').first():
            profesor = Usuario(
                email='profesor@academic.com',
                nombre='Profesor',
                apellidos='Ejemplo',
                rol='profesor'
            )
            profesor.set_password('profesor123')
            db.session.add(profesor)
        
        db.session.commit()
        print("✅ Base de datos inicializada")
        print("✅ Usuarios por defecto creados")
    app.run(debug=True, host='0.0.0.0', port=5000)

