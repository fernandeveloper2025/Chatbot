from flask import Flask, render_template, request, jsonify
from ejemplo import SoporteTecnicoBot

app = Flask(__name__)
bot = SoporteTecnicoBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    
    # Si es la inicialización del chat
    if data.get('type') == 'init':
        user_data = data.get('userData', {})
        bot.sesion_actual.update({
            "nombre_cliente": user_data.get('nombre_cliente'),
            "telefono": user_data.get('telefono'),
            "numero_servicio": user_data.get('numero_servicio'),
            "documento": user_data.get('documento')
        })
        return jsonify({"status": "ok"})
    
    # Si es un mensaje normal
    user_message = data.get("message")
    bot_response = bot.procesar_mensaje(user_message)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)