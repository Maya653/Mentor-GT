from app import create_app, db
from app.models.user import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
    with app.app_context():
        # Habilitar foreign keys en SQLite
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            with db.engine.connect() as conn:
                conn.execute(db.text('PRAGMA foreign_keys = ON'))
                conn.commit()
        
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario administrador por defecto
        if not User.query.filter_by(email='admin@utte.edu.mx').first():
            admin = User(
                email='admin@utte.edu.mx',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin: admin@utte.edu.mx / admin123")
        
        # Crear usuario docente por defecto
        if not User.query.filter_by(email='docente@utte.edu.mx').first():
            docente_user = User(
                email='docente@utte.edu.mx',
                role='docente'
            )
            docente_user.set_password('docente123')
            db.session.add(docente_user)
            db.session.commit()
            print("✅ Docente: docente@utte.edu.mx / docente123")
        
        print("✅ Base de datos lista")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
