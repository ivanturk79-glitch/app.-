import os
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

@app.route('/')
def home():
    return "Music Proxy Server is Running!"

@app.route('/search', methods=['GET'])
def search_tracks():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    # Поиск треков (используем публичный поиск)
    search_url = f"https://rus.hitmos.fm/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        # Здесь бэкенд парсит результаты или проксирует запрос к API плеера
        # Возвращаем заготовку структуры для фронтенда мини-приложения
        return jsonify({
            "query": query,
            "status": "success",
            "message": "Use frontend player integration or direct stream links"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream', methods=['GET'])
def stream_track():
    track_url = request.args.get('url')
    track_id = request.args.get('id', 'track')
    
    if not track_url:
        return jsonify({"error": "URL parameter is required"}), 400

    safe_filename = f"{track_id}.mp3"
    file_path = os.path.join(CACHE_DIR, safe_filename)

    # Проверка кеша (если файл уже скачан на сервер, отдаем мгновенно)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="audio/mpeg")

    try:
        # Скачиваем трек на сервер для кэширования и обхода лимитов
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(track_url, headers=headers, stream=True, timeout=15)
        
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return send_file(file_path, mimetype="audio/mpeg")
        else:
            return jsonify({"error": "Failed to fetch audio from source"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
