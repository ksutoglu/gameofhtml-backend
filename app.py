from flask import Flask, jsonify, request
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_NAME = "comments.db"

# Veritabanı başlat
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                username TEXT NOT NULL,
                comment TEXT NOT NULL,
                rating INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
init_db()

# 🔵 Mevcut oyun endpointi
@app.route('/games')
def get_games():
    with open("Wizard_Data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        oyunlar = data["segments"][0]["hits"]

        games = []
        for i, game in enumerate(oyunlar):
            games.append({
                "id": game.get("Id", f"{i+1}"),
                "title": game.get("Title", "Bilinmeyen"),
                "description": game.get("Description", ""),
                "instructions": game.get("Instructions", ""),
                "genres": game.get("Genres", []),
                "url": game.get("Game URL", "#"),
                "image": game.get("Assets", [""])[0] if game.get("Assets") else ""
            })
        return jsonify(games)

# 🔶 Yorum ekleme endpointi
@app.route("/comment", methods=["POST"])
def add_comment():
    data = request.json
    game_id = data.get("game_id")
    username = data.get("username")
    comment = data.get("comment")
    rating = data.get("rating", 5)

    if not all([game_id, username, comment]):
        return jsonify({"error": "Eksik veri"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (game_id, username, comment, rating)
            VALUES (?, ?, ?, ?)""",
            (game_id, username, comment, rating))
        conn.commit()

    return jsonify({"message": "Yorum eklendi!"}), 201

# 🔷 Belirli oyunun yorumlarını alma
@app.route("/comments", methods=["GET"])
def get_comments():
    game_id = request.args.get("game_id")
    if not game_id:
        return jsonify({"error": "game_id gerekli"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, comment, rating, created_at FROM comments WHERE game_id = ? ORDER BY created_at DESC", (game_id,))
        yorumlar = cursor.fetchall()

    yorumlar_json = [
        {"username": u, "comment": c, "rating": r, "created_at": t}
        for u, c, r, t in yorumlar
    ]
    return jsonify(yorumlar_json)

# 🟢 Server'ı başlat
if __name__ == '__main__':
    app.run(debug=True)
