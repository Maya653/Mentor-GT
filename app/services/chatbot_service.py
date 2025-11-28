import os
import re
import json
from groq import Groq
from flask import current_app
from app import db
from app.models.user import User
from app.models.docente import Docente
from app.models.articulo import Articulo
from app.models.congreso import Congreso
from app.models.curso_impartido import CursoImpartido
from app.models.proyecto_investigacion import ProyectoInvestigacion
from app.models.formacion_academica import FormacionAcademica
from app.models.empleo import Empleo

# Campos del perfil que se pueden actualizar via chatbot
CAMPOS_ACTUALIZABLES = {
    'nombre': 'nombre_completo',
    'nombre_completo': 'nombre_completo',
    'nombre completo': 'nombre_completo',
    'email': 'correo_principal',
    'correo': 'correo_principal',
    'correo_principal': 'correo_principal',
    'correo principal': 'correo_principal',
    'orcid': 'orcid',
    'cvu': 'cvu',
    'curp': 'curp',
    'rfc': 'rfc',
    'sexo': 'sexo',
    'género': 'sexo',
    'genero': 'sexo',
    'nacionalidad': 'nacionalidad',
    'pais_nacimiento': 'pais_nacimiento',
    'país de nacimiento': 'pais_nacimiento',
    'pais de nacimiento': 'pais_nacimiento',
    'estado_civil': 'estado_civil',
    'estado civil': 'estado_civil',
    'domicilio': 'domicilio',
    'direccion': 'domicilio',
    'dirección': 'domicilio',
    'researcher_id': 'researcher_id',
    'scopus_author_id': 'scopus_author_id',
    'scopus': 'scopus_author_id',
}

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
            
            # 🔄 DETECTAR SOLICITUD DE ACTUALIZACIÓN DE PERFIL
            resultado_actualizacion = self._detectar_y_procesar_actualizacion(mensaje, docente)
            if resultado_actualizacion:
                return resultado_actualizacion
            
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
    
    def _detectar_y_procesar_actualizacion(self, mensaje, docente):
        """Detectar si el mensaje solicita actualizar el perfil y procesarlo"""
        mensaje_lower = mensaje.lower()
        
        # Palabras clave que indican intención de actualizar
        palabras_actualizacion = [
            'actualiza', 'actualizar', 'cambia', 'cambiar', 'modifica', 'modificar',
            'edita', 'editar', 'pon', 'poner', 'establece', 'establecer', 'configura',
            'guardar', 'guarda', 'quiero que mi', 'mi nombre es', 'mi correo es',
            'mi email es', 'mi orcid es', 'mi cvu es', 'cámbialo a', 'cambialo a'
        ]
        
        # Verificar si el mensaje contiene intención de actualizar
        es_actualizacion = any(palabra in mensaje_lower for palabra in palabras_actualizacion)
        
        if not es_actualizacion:
            return None
        
        print(f"🔄 Detectada solicitud de actualización: {mensaje}")
        
        # Usar la IA para extraer los datos a actualizar
        datos_a_actualizar = self._extraer_datos_actualizacion(mensaje, docente)
        
        if not datos_a_actualizar:
            return None
        
        # Ejecutar la actualización
        return self._ejecutar_actualizacion(docente, datos_a_actualizar)
    
    def _extraer_datos_actualizacion(self, mensaje, docente):
        """Usar IA para extraer qué campos actualizar y con qué valores"""
        campos_disponibles = list(set(CAMPOS_ACTUALIZABLES.values()))
        
        prompt_extraccion = f"""Analiza el siguiente mensaje del usuario y extrae los datos que quiere actualizar en su perfil.

MENSAJE DEL USUARIO: "{mensaje}"

CAMPOS DISPONIBLES PARA ACTUALIZAR:
- nombre_completo: Nombre completo del docente
- correo_principal: Email/correo del docente  
- orcid: Identificador ORCID
- cvu: Número de CVU
- curp: CURP del docente
- rfc: RFC del docente
- sexo: Sexo/género (Masculino, Femenino, Otro)
- nacionalidad: Nacionalidad
- pais_nacimiento: País de nacimiento
- estado_civil: Estado civil
- domicilio: Dirección/domicilio
- researcher_id: ID de Researcher
- scopus_author_id: ID de Scopus

DATOS ACTUALES DEL DOCENTE:
- nombre_completo: {docente.nombre_completo or 'No especificado'}
- correo_principal: {docente.correo_principal or 'No especificado'}
- orcid: {docente.orcid or 'No especificado'}
- cvu: {docente.cvu or 'No especificado'}

INSTRUCCIONES:
1. Identifica qué campo(s) el usuario quiere actualizar
2. Extrae el nuevo valor que el usuario proporciona
3. Responde SOLO en formato JSON válido, sin texto adicional
4. Si no puedes identificar claramente qué actualizar, responde con: {{"error": "no_identificado"}}

FORMATO DE RESPUESTA (JSON válido):
{{"campo": "nombre_del_campo", "valor": "nuevo_valor"}}

O para múltiples campos:
{{"actualizaciones": [{{"campo": "campo1", "valor": "valor1"}}, {{"campo": "campo2", "valor": "valor2"}}]}}

Responde SOLO con el JSON, sin explicaciones ni texto adicional."""

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un extractor de datos. Solo respondes en JSON válido."},
                    {"role": "user", "content": prompt_extraccion}
                ],
                model=self.model,
                temperature=0.1,  # Baja temperatura para respuestas precisas
                max_tokens=256
            )
            
            respuesta_ia = response.choices[0].message.content.strip()
            print(f"📋 Respuesta IA extracción: {respuesta_ia}")
            
            # Limpiar la respuesta de posibles marcadores de código
            respuesta_ia = respuesta_ia.replace('```json', '').replace('```', '').strip()
            
            # Parsear JSON
            datos = json.loads(respuesta_ia)
            
            if "error" in datos:
                print(f"⚠️ IA no pudo identificar datos: {datos}")
                return None
            
            return datos
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON de IA: {e}")
            print(f"   Respuesta recibida: {respuesta_ia}")
            return None
        except Exception as e:
            print(f"❌ Error en extracción de datos: {e}")
            return None
    
    def _ejecutar_actualizacion(self, docente, datos):
        """Ejecutar la actualización real en la base de datos"""
        try:
            campos_actualizados = []
            
            # Manejar formato simple {"campo": "x", "valor": "y"}
            if "campo" in datos and "valor" in datos:
                actualizaciones = [{"campo": datos["campo"], "valor": datos["valor"]}]
            # Manejar formato múltiple {"actualizaciones": [...]}
            elif "actualizaciones" in datos:
                actualizaciones = datos["actualizaciones"]
            else:
                print(f"⚠️ Formato de datos no reconocido: {datos}")
                return None
            
            for act in actualizaciones:
                campo = act.get("campo", "").lower().strip()
                valor = act.get("valor", "").strip()
                
                # Mapear nombre amigable al nombre real del campo
                campo_real = CAMPOS_ACTUALIZABLES.get(campo, campo)
                
                # Validar que el campo existe en el modelo Docente
                if not hasattr(docente, campo_real):
                    print(f"⚠️ Campo no válido: {campo_real}")
                    continue
                
                # Obtener valor anterior para el log
                valor_anterior = getattr(docente, campo_real, None)
                
                # Actualizar el campo
                setattr(docente, campo_real, valor)
                campos_actualizados.append({
                    "campo": campo_real,
                    "valor_anterior": valor_anterior,
                    "valor_nuevo": valor
                })
                
                print(f"✅ Actualizado {campo_real}: '{valor_anterior}' → '{valor}'")
            
            if not campos_actualizados:
                return None
            
            # Guardar cambios en la base de datos
            db.session.commit()
            print(f"💾 Cambios guardados en BD")
            
            # Construir respuesta de confirmación
            respuesta = "✅ **¡Perfil actualizado correctamente!**\n\n"
            respuesta += "📝 **Cambios realizados:**\n"
            
            for cambio in campos_actualizados:
                nombre_campo = cambio["campo"].replace("_", " ").title()
                respuesta += f"- **{nombre_campo}:** {cambio['valor_nuevo']}\n"
            
            respuesta += "\n💡 Los cambios ya están guardados y se reflejarán en tu perfil."
            
            return respuesta
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar perfil: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ Error al actualizar el perfil: {str(e)}"
    
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

IMPORTANTE: 
- NO digas que puedes actualizar o modificar datos del perfil directamente.
- Si el usuario quiere actualizar datos, dile que lo intente con un mensaje claro como: "Actualiza mi nombre a [nuevo nombre]"
- Las actualizaciones de perfil son manejadas por un sistema separado, no por ti.
- Nunca finjas que actualizaste algo si no recibiste confirmación del sistema.

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