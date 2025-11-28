import os
import re
import json
from groq import Groq
from flask import current_app
from app.models.user import User
from app.models.docente import Docente
from app.models.articulo import Articulo
from app.models.congreso import Congreso
from app.models.curso_impartido import CursoImpartido
from app.models.proyecto_investigacion import ProyectoInvestigacion
from app.models.formacion_academica import FormacionAcademica
from app.models.empleo import Empleo

class ChatbotService:
    def __init__(self):
        # Intentar obtener API key de dos formas
        api_key = os.getenv('GROQ_API_KEY') or current_app.config.get('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY no está configurada")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def generar_respuesta(self, mensaje, user_id, historial=None):
        """Generar respuesta del chatbot"""
        try:
            # Obtener docente
            user = User.query.get(user_id)
            if not user:
                return "Error: Usuario no encontrado"
            
            docente = Docente.query.filter_by(user_id=user.id).first()
            if not docente:
                return "Por favor, completa tu perfil primero."
            
            # ✨ DETECTAR MENSAJE ESPECIAL CON SECCIONES PERSONALIZADAS (del modal)
            if mensaje.startswith('GENERAR_CV_PERSONALIZADO|'):
                return self._procesar_cv_personalizado(mensaje, docente)
            
            # Respuesta conversacional normal
            return self._generar_respuesta_conversacional(mensaje, docente, historial)
            
        except Exception as e:
            print(f"Error en ChatbotService: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Lo siento, ocurrió un error: {str(e)}"
    
    def _procesar_cv_personalizado(self, mensaje, docente):
        """Procesar solicitud de CV con secciones personalizadas del modal"""
        try:
            # Parsear mensaje: GENERAR_CV_PERSONALIZADO|plantilla:conacyt|secciones:{...}
            parts = mensaje.split('|')
            plantilla = parts[1].split(':')[1]
            secciones_json = parts[2].split(':', 1)[1]
            secciones = json.loads(secciones_json)
            
            print(f"🎨 Generando CV personalizado - Plantilla: {plantilla}")
            print(f"📋 Secciones seleccionadas: {secciones}")
            
            # Generar PDF
            from app.services.cv_pdf_generator import CVPDFGenerator
            generator = CVPDFGenerator()
            pdf_filename = generator.generar_pdf(docente, secciones, plantilla)
            
            print(f"✅ PDF generado: {pdf_filename}")
            
            # Construir respuesta
            respuesta = f"""✅ ¡Perfecto! He generado tu CV en formato **{plantilla.upper()}**.

📋 **Secciones incluidas:**
"""
            
            # Listar secciones incluidas
            secciones_nombres = {
                'datos_generales': 'Datos Generales',
                'formacion_academica': 'Formación Académica',
                'experiencia_laboral': 'Experiencia Laboral',
                'articulos_cientificos': 'Artículos Científicos',
                'libros_capitulos': 'Libros y Capítulos',
                'congresos_ponencias': 'Congresos y Ponencias',
                'proyectos_investigacion': 'Proyectos de Investigación',
                'cursos_impartidos': 'Cursos Impartidos',
                'tesis_dirigidas': 'Tesis Dirigidas',
                'desarrollos_tecnologicos': 'Desarrollos Tecnológicos'
            }
            
            for key, incluida in secciones.items():
                if incluida:
                    respuesta += f"✓ {secciones_nombres.get(key, key)}\n"
            
            respuesta += f"""
📥 **[Haz clic aquí para descargar tu CV](/static/pdfs/{pdf_filename})**

💡 **Tip:** Puedes generar otro CV con diferentes opciones cuando quieras.
"""
            
            return respuesta
            
        except Exception as e:
            print(f"❌ Error al generar CV personalizado: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"❌ Error al generar el CV: {str(e)}"
    
    def _generar_respuesta_conversacional(self, mensaje, docente, historial=None):
        """Generar respuesta conversacional normal"""
        contexto = self._construir_contexto_cv(docente)
        
        system_message = f"""Eres un asistente virtual especializado en ayudar a docentes con su CV académico.
Tienes acceso a la siguiente información del docente:

{contexto}

Tu trabajo es:
1. Responder preguntas sobre el CV del docente
2. Ayudar a mejorar su perfil académico
3. Proporcionar información útil sobre sus logros y trayectoria

Sé amable, profesional y conciso en tus respuestas. Usa emojis ocasionalmente."""

        messages = [{"role": "system", "content": system_message}]
        
        if historial:
            messages.extend(historial)
        
        messages.append({"role": "user", "content": mensaje})
        
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        
        return chat_completion.choices[0].message.content
    
    def _construir_contexto_cv(self, docente):
        """Construir contexto con información del CV"""
        contexto_partes = []
        
        contexto_partes.append(f"INFORMACIÓN PERSONAL:")
        contexto_partes.append(f"- Nombre: {docente.nombre_completo or 'No especificado'}")
        contexto_partes.append(f"- Email: {docente.correo_principal or 'No especificado'}")
        if docente.cvu:
            contexto_partes.append(f"- CVU: {docente.cvu}")
        if docente.orcid:
            contexto_partes.append(f"- ORCID: {docente.orcid}")
        
        # Artículos
        articulos = Articulo.query.filter_by(docente_id=docente.id).order_by(Articulo.anio.desc()).limit(10).all()
        if articulos:
            contexto_partes.append(f"\nARTÍCULOS CIENTÍFICOS ({len(articulos)} más recientes):")
            for art in articulos:
                contexto_partes.append(f"- {art.titulo} ({art.anio})")
            
            total_articulos = Articulo.query.filter_by(docente_id=docente.id).count()
            contexto_partes.append(f"\nTotal de artículos: {total_articulos}")
        
        # Formación
        formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
        if formaciones:
            contexto_partes.append(f"\nFORMACIÓN ACADÉMICA:")
            for form in formaciones[:3]:
                contexto_partes.append(f"- {form.nivel or 'N/A'}: {form.grado_obtenido or 'Sin título'}")
        
        # Empleos
        empleos = Empleo.query.filter_by(docente_id=docente.id).order_by(Empleo.fecha_inicio.desc()).limit(3).all()
        if empleos:
            contexto_partes.append(f"\nEXPERIENCIA LABORAL:")
            for emp in empleos:
                contexto_partes.append(f"- {emp.puesto or 'Sin puesto'} en {emp.institucion or 'Sin institución'}")
        
        # Congresos
        congresos = Congreso.query.filter_by(docente_id=docente.id).order_by(Congreso.fecha.desc()).limit(5).all()
        if congresos:
            contexto_partes.append(f"\nCONGRESOS:")
            for cong in congresos:
                contexto_partes.append(f"- {cong.nombre_congreso}")
        
        # Cursos
        cursos = CursoImpartido.query.filter_by(docente_id=docente.id).limit(5).all()
        if cursos:
            contexto_partes.append(f"\nCURSOS IMPARTIDOS:")
            for curso in cursos:
                contexto_partes.append(f"- {curso.nombre_curso}")
        
        # Proyectos
        proyectos = ProyectoInvestigacion.query.filter_by(docente_id=docente.id).all()
        if proyectos:
            contexto_partes.append(f"\nPROYECTOS DE INVESTIGACIÓN:")
            for proy in proyectos:
                contexto_partes.append(f"- {proy.nombre_proyecto}")
        
        return "\n".join(contexto_partes)
    
    def generar_respuesta_streaming(self, pregunta: str, usuario_id: int):
        """Generar respuesta en modo streaming (para efecto de escritura)"""
        user = User.query.get(usuario_id)
        docente = Docente.query.filter_by(user_id=usuario_id).first()
        
        if not docente:
            yield "Por favor, completa tu perfil primero."
            return
        
        contexto = self._construir_contexto_cv(docente)
        
        system_prompt = f"""Eres un asistente académico especializado.

INFORMACIÓN DEL PROFESOR:
{contexto}

Responde de manera clara y profesional."""

        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": pregunta}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"