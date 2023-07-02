import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
from base64 import b64decode
from PIL import Image
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dadansep'
socketio = SocketIO(app)

# Inisialisasi variabel global jumlah pengguna online
online_users = 0

@app.route('/')
def index():
    return render_template('index.html', online_users=online_users)

@socketio.on('connect')
def connect():
    global online_users
    online_users += 1
    emit('user_status', {'online_users': online_users}, broadcast=True)

@socketio.on('disconnect')
def disconnect():
    global online_users
    online_users = max(online_users - 1, 0)
    emit('user_status', {'online_users': online_users}, broadcast=True)

@socketio.on('message')
def handle_message(message):
    emit('chat_message', message, broadcast=True)

@socketio.on('image')
def handle_image(data):
    image_data = data['image']
    image_name = data['name']
    save_path = os.path.join('static', 'images', image_name)

    # Mengompresi dan menyimpan gambar
    image = Image.open(io.BytesIO(b64decode(image_data)))
    max_size = (1024, 1024)  # Ukuran maksimum yang diinginkan
    image.thumbnail(max_size)
    image.save(save_path, format='JPEG', optimize=True, quality=85)

    emit('image', {'name': image_name}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9822)

