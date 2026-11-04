from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from chatbot import chatbot_reply
from database import initialize_database, clear_moods, get_moods, save_mood

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"message": "Backend connected"})


@app.get("/api/moods")
def read_moods():
    return jsonify({"moods": get_moods()})


@app.post("/api/moods")
def create_mood():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid mood entry."}), 400

    success, message = save_mood(
        data.get("entry_date"),
        data.get("mood_score"),
        data.get("note", ""),
    )

    if not success:
        return jsonify({"error": message}), 400

    return jsonify({"message": message})


@app.delete("/api/moods")
def delete_moods():
    clear_moods()
    return jsonify({"message": "Demo mood entries cleared."})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid message."}), 400

    success, reply_or_error = chatbot_reply(data.get("messages"))

    if not success:
        return jsonify({"error": reply_or_error}), 400

    return jsonify({"reply": reply_or_error})


if __name__ == "__main__":
    initialize_database()
    app.run(host="127.0.0.1", port=5000, debug=False)
