from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
import io

class CVGeneratorService:
    """Servicio para generar CVs en diferentes formatos"""
    
    def generar_pdf(self, usuario, publicaciones, eventos, docencias, tipo_cv='academico'):
        """Genera un CV en formato PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            spaceBefore=12
        )
        
        # Título
        nombre_completo = f"{usuario.nombre} {usuario.apellidos or ''}".strip()
        story.append(Paragraph(nombre_completo, title_style))
        story.append(Paragraph(usuario.email, styles['Normal']))
        if usuario.orcid_id:
            story.append(Paragraph(f"ORCID: {usuario.orcid_id}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Datos personales
        story.append(Paragraph("DATOS PERSONALES", heading_style))
        datos = [
            f"<b>Nombre:</b> {usuario.nombre} {usuario.apellidos or ''}",
            f"<b>Email:</b> {usuario.email}",
        ]
        if usuario.google_scholar_id:
            datos.append(f"<b>Google Scholar:</b> {usuario.google_scholar_id}")
        if usuario.scopus_id:
            datos.append(f"<b>Scopus ID:</b> {usuario.scopus_id}")
        
        for dato in datos:
            story.append(Paragraph(dato, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Publicaciones
        if publicaciones:
            story.append(Paragraph("PUBLICACIONES", heading_style))
            for i, pub in enumerate(publicaciones, 1):
                pub_text = f"<b>{i}. {pub.titulo}</b>"
                if pub.autores:
                    pub_text += f"<br/>{pub.autores}"
                if pub.revista:
                    pub_text += f"<br/>{pub.revista}"
                if pub.año:
                    pub_text += f", {pub.año}"
                if pub.doi:
                    pub_text += f"<br/>DOI: {pub.doi}"
                story.append(Paragraph(pub_text, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            story.append(Spacer(1, 0.2*inch))
        
        # Eventos
        if eventos:
            story.append(Paragraph("EVENTOS ACADÉMICOS", heading_style))
            for evento in eventos:
                evento_text = f"<b>{evento.nombre}</b>"
                if evento.lugar:
                    evento_text += f"<br/>{evento.lugar}"
                if evento.fecha_inicio:
                    evento_text += f", {evento.fecha_inicio.strftime('%Y')}"
                story.append(Paragraph(evento_text, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            story.append(Spacer(1, 0.2*inch))
        
        # Docencia
        if docencias:
            story.append(Paragraph("EXPERIENCIA DOCENTE", heading_style))
            for docencia in docencias:
                doc_text = f"<b>{docencia.nombre_curso}</b>"
                if docencia.institucion:
                    doc_text += f"<br/>{docencia.institucion}"
                if docencia.año:
                    doc_text += f", {docencia.año}"
                story.append(Paragraph(doc_text, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generar_word(self, usuario, publicaciones, eventos, docencias, tipo_cv='academico'):
        """Genera un CV en formato Word"""
        doc = Document()
        
        # Título
        heading = doc.add_heading(f"{usuario.nombre} {usuario.apellidos or ''}", 0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        p = doc.add_paragraph(usuario.email)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        if usuario.orcid_id:
            p = doc.add_paragraph(f"ORCID: {usuario.orcid_id}")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Datos personales
        doc.add_heading('Datos Personales', 1)
        doc.add_paragraph(f"Nombre: {usuario.nombre} {usuario.apellidos or ''}")
        doc.add_paragraph(f"Email: {usuario.email}")
        if usuario.google_scholar_id:
            doc.add_paragraph(f"Google Scholar: {usuario.google_scholar_id}")
        if usuario.scopus_id:
            doc.add_paragraph(f"Scopus ID: {usuario.scopus_id}")
        
        # Publicaciones
        if publicaciones:
            doc.add_heading('Publicaciones', 1)
            for i, pub in enumerate(publicaciones, 1):
                p = doc.add_paragraph(f"{i}. {pub.titulo}", style='List Number')
                if pub.autores:
                    doc.add_paragraph(f"Autores: {pub.autores}")
                if pub.revista:
                    doc.add_paragraph(f"Revista: {pub.revista}")
                if pub.año:
                    doc.add_paragraph(f"Año: {pub.año}")
                if pub.doi:
                    doc.add_paragraph(f"DOI: {pub.doi}")
        
        # Eventos
        if eventos:
            doc.add_heading('Eventos Académicos', 1)
            for evento in eventos:
                doc.add_paragraph(evento.nombre, style='List Bullet')
                if evento.lugar:
                    doc.add_paragraph(f"Lugar: {evento.lugar}")
                if evento.fecha_inicio:
                    doc.add_paragraph(f"Fecha: {evento.fecha_inicio.strftime('%Y-%m-%d')}")
        
        # Docencia
        if docencias:
            doc.add_heading('Experiencia Docente', 1)
            for docencia in docencias:
                doc.add_paragraph(docencia.nombre_curso, style='List Bullet')
                if docencia.institucion:
                    doc.add_paragraph(f"Institución: {docencia.institucion}")
                if docencia.año:
                    doc.add_paragraph(f"Año: {docencia.año}")
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

