from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.publicacion import Publicacion
from app.forms.publicacion_forms import PublicacionForm
from app.utils.decorators import profesor_required

publicacion_bp = Blueprint('publicacion', __name__)

@publicacion_bp.route('/')
@login_required
@profesor_required
def listar():
    publicaciones = Publicacion.query.filter_by(usuario_id=current_user.id)\
        .order_by(Publicacion.año.desc()).all()
    return render_template('profesor/publicaciones.html', publicaciones=publicaciones)

@publicacion_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@profesor_required
def nueva():
    form = PublicacionForm()
    if form.validate_on_submit():
        publicacion = Publicacion(
            usuario_id=current_user.id,
            titulo=form.titulo.data,
            autores=form.autores.data,
            revista=form.revista.data,
            volumen=form.volumen.data,
            numero=form.numero.data,
            paginas=form.paginas.data,
            año=form.año.data,
            doi=form.doi.data,
            isbn=form.isbn.data,
            tipo=form.tipo.data,
            indizada=form.indizada.data
        )
        db.session.add(publicacion)
        db.session.commit()
        flash('Publicación creada exitosamente', 'success')
        return redirect(url_for('publicacion.listar'))
    
    return render_template('profesor/nueva_publicacion.html', form=form)

@publicacion_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@profesor_required
def editar(id):
    publicacion = Publicacion.query.get_or_404(id)
    if publicacion.usuario_id != current_user.id:
        flash('No tienes permisos para editar esta publicación', 'danger')
        return redirect(url_for('publicacion.listar'))
    
    form = PublicacionForm(obj=publicacion)
    if form.validate_on_submit():
        publicacion.titulo = form.titulo.data
        publicacion.autores = form.autores.data
        publicacion.revista = form.revista.data
        publicacion.volumen = form.volumen.data
        publicacion.numero = form.numero.data
        publicacion.paginas = form.paginas.data
        publicacion.año = form.año.data
        publicacion.doi = form.doi.data
        publicacion.isbn = form.isbn.data
        publicacion.tipo = form.tipo.data
        publicacion.indizada = form.indizada.data
        
        db.session.commit()
        flash('Publicación actualizada exitosamente', 'success')
        return redirect(url_for('publicacion.listar'))
    
    return render_template('profesor/editar_publicacion.html', form=form, publicacion=publicacion)

@publicacion_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@profesor_required
def eliminar(id):
    publicacion = Publicacion.query.get_or_404(id)
    if publicacion.usuario_id != current_user.id:
        flash('No tienes permisos para eliminar esta publicación', 'danger')
        return redirect(url_for('publicacion.listar'))
    
    db.session.delete(publicacion)
    db.session.commit()
    flash('Publicación eliminada exitosamente', 'success')
    return redirect(url_for('publicacion.listar'))

