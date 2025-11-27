from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.usuario import Usuario
from app.forms.auth_forms import LoginForm, RegistroForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.es_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('profesor.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_password(form.password.data):
            if not usuario.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'warning')
                return render_template('auth/login.html', form=form)
            
            login_user(usuario, remember=form.remember.data)
            next_page = request.args.get('next')
            
            if usuario.es_admin():
                return redirect(next_page or url_for('admin.dashboard'))
            return redirect(next_page or url_for('profesor.dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profesor.dashboard'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('Este email ya está registrado', 'danger')
            return render_template('auth/register.html', form=form)
        
        usuario = Usuario(
            email=form.email.data,
            nombre=form.nombre.data,
            apellidos=form.apellidos.data,
            rol='profesor'
        )
        usuario.set_password(form.password.data)
        db.session.add(usuario)
        db.session.commit()
        
        flash('Registro exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('auth.login'))

