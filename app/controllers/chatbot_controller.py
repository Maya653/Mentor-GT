from flask import Blueprint, render_template, request, jsonify, Response, stream_with_context
from flask_login import login_required, current_user
from app import csrf
from app.services.chatbot_service import ChatbotService
from app.utils.decorators import docente_required  # ⬅️ CAMBIO: docente_required en vez de profesor_required
from datetime import datetime
import json

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/')
@login_required
@docente_required  # ⬅️ CAMBIO
def index():
    """Página del chatbot"""
    return render_template('docente/chatbot.html')  # ⬅️ CAMBIO: docente/chatbot.html

@chatbot_bp.route('/mensaje', methods=['POST'])
@login_required
@docente_required  # ⬅️ CAMBIO
@csrf.exempt
def enviar_mensaje():
    """Procesar mensaje del usuario y generar respuesta"""
    try:
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")
        
        pregunta = data.get('mensaje', '')
        print(f"📩 Mensaje: {pregunta}")
        
        if not pregunta:
            print("❌ Mensaje vacío")
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        print("🤖 Creando ChatbotService...")
        chatbot_service = ChatbotService()
        print("✅ ChatbotService creado")
        
        print(f"🔄 Generando respuesta para user_id: {current_user.id}")
        resultado = chatbot_service.generar_respuesta(pregunta, current_user.id)
        print(f"✅ Respuesta generada - Tipo: {type(resultado)}")
        
        # MANEJAR AMBOS FORMATOS (dict o string)
        if isinstance(resultado, dict):
            # Formato antiguo: {'respuesta': '...', 'metadata': {...}}
            respuesta_texto = resultado.get('respuesta', str(resultado))
            print(f"📤 Formato dict detectado - Extrayendo 'respuesta'")
            return jsonify(resultado)  # Devolver todo el dict con metadata
        else:
            # Formato nuevo: string directo
            respuesta_texto = str(resultado)
            print(f"📤 Formato string detectado")
            return jsonify({
                'respuesta': respuesta_texto,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'error': False
                }
            })
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en chatbot: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'respuesta': f'Lo siento, hubo un error: {str(e)}',
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'error': True
            }
        }), 500

@chatbot_bp.route('/stream', methods=['POST'])
@login_required
@docente_required  # ⬅️ CAMBIO
@csrf.exempt  # ⬅️ AGREGADO
def stream_mensaje():
    """API para recibir respuesta en streaming (efecto de escritura)"""
    try:
        data = request.get_json()
        print(f"📩 Streaming - Datos recibidos: {data}")
        
        pregunta = data.get('mensaje', '')
        print(f"📩 Streaming - Mensaje: {pregunta}")
        
        if not pregunta:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        def generate():
            try:
                chatbot_service = ChatbotService()
                for chunk in chatbot_service.generar_respuesta_streaming(pregunta, current_user.id):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            except Exception as e:
                print(f"❌ Error en streaming: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"❌ Error en stream_mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/limpiar', methods=['POST'])
@login_required
@docente_required  # ⬅️ CAMBIO
@csrf.exempt  # ⬅️ AGREGADO
def limpiar():
    """Limpiar el historial del chat"""
    try:
        print("🧹 Limpiando historial del chat")
        return jsonify({
            'mensaje': 'Historial limpiado correctamente',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"❌ Error al limpiar: {str(e)}")
        return jsonify({'error': str(e)}), 500