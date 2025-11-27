import unittest
from app import create_app, db
from app.models.usuario import Usuario

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_usuario_creation(self):
        usuario = Usuario(
            email='test@example.com',
            nombre='Test',
            apellidos='User',
            rol='profesor'
        )
        usuario.set_password('password123')
        db.session.add(usuario)
        db.session.commit()
        
        self.assertEqual(usuario.email, 'test@example.com')
        self.assertTrue(usuario.check_password('password123'))
        self.assertFalse(usuario.check_password('wrongpassword'))

if __name__ == '__main__':
    unittest.main()

