# from flask import Flask, render_template, request
# from complaint_x_bot.retrieval_generation import generation
# from complaint_x_bot.data_ingestion import data_ingestion


# vstore = data_ingestion("done")
# chain = generation(vstore)


# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("index.html")



# @app.route("/get", methods = ["POST", "GET"])
# def chat():
   
#    if request.method == "POST":
#       msg = request.form["msg"]
#       input = msg

#       result = chain.invoke(
#          {"input": input},
#     config={
#         "configurable": {"session_id": "Prateek"}
#     },
# )["answer"]

#       return str(result)

# if __name__ == '__main__':
    
#     app.run(host="0.0.0.0", port=5000, debug= True)


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from complaint_x_bot.retrieval_generation import generation
from complaint_x_bot.data_ingestion import data_ingestion
import uuid

# Initialize the complaint bot components
vstore = data_ingestion("done")
chain = generation(vstore)

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store chat history
chat_sessions = {}

# Your existing routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["POST", "GET"])
def chat():
    if request.method == "POST":
        msg = request.form["msg"]
        input = msg
        result = chain.invoke(
            {"input": input},
            config={
                "configurable": {"session_id": "Prateek"}
            },
        )["answer"]
        return str(result)

# New routes for multi-screen chat
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/agent")
def agent():
    session_id = request.args.get('session_id')
    if not session_id:
        return render_template("welcome.html")
    return render_template("agent.html", session_id=session_id)

@app.route("/customer")
def customer():
    session_id = request.args.get('session_id', uuid.uuid4().hex)
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return render_template("customer.html", session_id=session_id)

# Socket.IO event handlers
@socketio.on('join')
def on_join(data):
    room = data['session_id']
    join_room(room)
    emit('status', {'msg': f"{'Agent' if data.get('is_agent') else 'Customer'} has joined the chat"}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['session_id']
    leave_room(room)
    emit('status', {'msg': f"{'Agent' if data.get('is_agent') else 'Customer'} has left the chat"}, room=room)

@socketio.on('send_message')
def on_chat_message(data):
    room = data['session_id']
    sender = data['sender']
    message = data['message']
    
    # Store message in session history
    if room not in chat_sessions:
        chat_sessions[room] = []
    
    chat_sessions[room].append({
        'sender': sender,
        'message': message
    })
    
    # Broadcast message to the room
    emit('receive_message', {
        'sender': sender,
        'message': message
    }, room=room)
    
    # If message is from customer, generate AI response for agent assistance
    if sender == 'customer' and data.get('need_ai_response', False):
        ai_response = chain.invoke(
            {"input": message},
            config={"configurable": {"session_id": room}}
        )["answer"]
        
        # Send AI suggestion to agent only
        emit('ai_suggestion', {
            'message': ai_response
        }, room=room)

@socketio.on('get_history')
def get_chat_history(data):
    room = data['session_id']
    if room in chat_sessions:
        emit('chat_history', {'history': chat_sessions[room]})
    else:
        emit('chat_history', {'history': []})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)