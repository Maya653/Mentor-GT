from groq import Groq
from flask import current_app
from app.models.user import User
from app.models.docente import Docente
from app.models.articulo import Articulo
from app.models.formacion_academica import FormacionAcademica
from app.models.empleo import Empleo
from app.models.congreso import Congreso
from app.models.curso_impartido import CursoImpartido
from datetime import datetime

class ChatbotService:
    """Chatbot con IA usando Groq (Llama 3.3)"""
    
    def __init__(self):
        api_key = current_app.config.get('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY no configurada")
        self.client = Groq(api_key=api_key)
    
    def generar_respuesta(self, pregunta: str, usuario_id: int, historial: list = None) -> dict:
        """
        Genera respuesta usando Groq (Llama 3.3)
        """
        
        # Obtener datos del usuario
        user = User.query.get(usuario_id)
        docente = Docente.query.filter_by(user_id=usuario_id).first()
        
        if not docente:
            return {
                'respuesta': "Por favor, completa tu perfil primero para que pueda ayudarte mejor.",
                'metadata': {'timestamp': datetime.now().isoformat(), 'error': False}
            }
        
        articulos = Articulo.query.filter_by(docente_id=docente.id).all()
        formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
        empleos = Empleo.query.filter_by(docente_id=docente.id).all()
        congresos = Congreso.query.filter_by(docente_id=docente.id).all()
        cursos = CursoImpartido.query.filter_by(docente_id=docente.id).all()
        
        # Construir contexto del CV
        contexto = self._construir_contexto_cv(user, docente, articulos, formaciones, empleos, congresos, cursos)
        
        # Construir el sistema prompt
        system_prompt = f"""Eres un asistente académico especializado en ayudar a profesores universitarios con sus CVs.

INFORMACIÓN DEL PROFESOR:
{contexto}

INSTRUCCIONES:
- Responde de manera clara, profesional y útil
- Si te preguntan sobre datos del CV, usa la información proporcionada
- Si te piden generar un CV, explica los pasos para hacerlo
- Si te piden sincronizar, explica cómo configurar ORCID
- Sé conciso pero informativo
- Usa emojis ocasionalmente para hacer la conversación más amigable
- Si no tienes información, sugiere al usuario agregarla al sistema"""

        # Preparar mensajes para la API
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Agregar historial si existe
        if historial:
            messages.extend(historial)
        
        # Agregar pregunta actual
        messages.append({
            "role": "user",
            "content": pregunta
        })
        
        try:
            # Llamar a Groq API
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            respuesta = chat_completion.choices[0].message.content
            
            # Detectar si el usuario quiere generar CV
            es_solicitud_cv = self._detectar_intencion_generar_cv(pregunta)
            
            return {
                'respuesta': respuesta,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'modelo': 'llama-3.3-70b',
                    'tokens_usados': chat_completion.usage.total_tokens,
                    'es_solicitud_cv': es_solicitud_cv
                }
            }
            
        except Exception as e:
            return {
                'respuesta': f"Lo siento, hubo un error al procesar tu pregunta: {str(e)}",
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'error': True
                }
            }
    
    def _construir_contexto_cv(self, user, docente, articulos, formaciones, empleos, congresos, cursos):
        """Construye el contexto del CV para el chatbot"""
        
        contexto = f"""
DATOS PERSONALES:
- Nombre: {docente.nombre_completo or 'No especificado'}
- Email: {user.email}
- ORCID ID: {docente.orcid or 'No configurado'}
- CVU: {docente.cvu or 'No configurado'}

FORMACIÓN ACADÉMICA ({len(formaciones)} total):
"""
        
        if formaciones:
            for f in formaciones[:5]:
                contexto += f"- {f.grado_obtenido or f.nivel} - {f.institucion} ({f.fecha_fin.year if f.fecha_fin else 'En curso'})\n"
        else:
            contexto += "No hay formación académica registrada.\n"
        
        contexto += f"\nARTÍCULOS CIENTÍFICOS ({len(articulos)} total):\n"
        
        if articulos:
            articulos_ordenados = sorted(articulos, key=lambda x: x.anio or 0, reverse=True)
            
            for art in articulos_ordenados[:10]:
                contexto += f"- [{art.anio or 'N/A'}] {art.titulo}\n"
                if art.revista:
                    contexto += f"  Revista: {art.revista}\n"
                if art.doi:
                    contexto += f"  DOI: {art.doi}\n"
            
            if len(articulos) > 10:
                contexto += f"\n... y {len(articulos) - 10} artículos más\n"
        else:
            contexto += "No hay artículos registrados aún.\n"
        
        contexto += f"\nEXPERIENCIA LABORAL ({len(empleos)} total):\n"
        if empleos:
            for emp in empleos[:5]:
                periodo = f"{emp.fecha_inicio.year if emp.fecha_inicio else 'N/A'} - {'Actual' if emp.actual else (emp.fecha_fin.year if emp.fecha_fin else 'N/A')}"
                contexto += f"- {emp.puesto} en {emp.institucion} ({periodo})\n"
        else:
            contexto += "No hay experiencia laboral registrada.\n"
        
        contexto += f"\nCONGRESOS ({len(congresos)} total):\n"
        if congresos:
            for cong in congresos[:5]:
                contexto += f"- {cong.titulo_ponencia or cong.nombre_congreso} ({cong.fecha.year if cong.fecha else 'N/A'})\n"
        else:
            contexto += "No hay congresos registrados.\n"
        
        contexto += f"\nCURSOS IMPARTIDOS ({len(cursos)} total):\n"
        if cursos:
            for curso in cursos[:5]:
                contexto += f"- {curso.nombre_curso} - {curso.nivel or 'N/A'}\n"
        else:
            contexto += "No hay cursos registrados.\n"
        
        return contexto
    
    def _detectar_intencion_generar_cv(self, pregunta: str) -> bool:
        """Detecta si el usuario quiere generar un CV"""
        palabras_clave = ['genera', 'generar', 'crear', 'crea', 'cv', 'curriculum', 
                          'reporte', 'documento', 'pdf', 'word', 'descargar']
        pregunta_lower = pregunta.lower()
        return any(palabra in pregunta_lower for palabra in palabras_clave)
    
    def generar_respuesta_streaming(self, pregunta: str, usuario_id: int):
        """
        Genera respuesta en modo streaming (para efecto de "escribiendo")
        """
        user = User.query.get(usuario_id)
        docente = Docente.query.filter_by(user_id=usuario_id).first()
        
        if not docente:
            yield "Por favor, completa tu perfil primero."
            return
        
        articulos = Articulo.query.filter_by(docente_id=docente.id).all()
        formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
        empleos = Empleo.query.filter_by(docente_id=docente.id).all()
        congresos = Congreso.query.filter_by(docente_id=docente.id).all()
        cursos = CursoImpartido.query.filter_by(docente_id=docente.id).all()
        
        contexto = self._construir_contexto_cv(user, docente, articulos, formaciones, empleos, congresos, cursos)
        
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
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"
