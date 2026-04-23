from flask import Blueprint, request, jsonify
from app.services.poem_service import create_poem, get_all_poems, get_poem_by_id

poem_bp = Blueprint("poem", __name__)
ALLOWED_MOODS = {"bahagia", "sedih", "galau", "semangat"}


@poem_bp.route("/poems/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}
    theme = data.get("theme")
    mood = data.get("mood")
    stanza_count = data.get("stanza_count")

    if not theme:
        return jsonify({"error": "Theme is required"}), 400
    if not mood:
        return jsonify({"error": "Mood is required"}), 400
    if mood not in ALLOWED_MOODS:
        return jsonify({"error": "Mood harus salah satu dari: bahagia/sedih/galau/semangat"}), 400
    if stanza_count is None:
        return jsonify({"error": "stanza_count is required"}), 400
    if not isinstance(stanza_count, int):
        return jsonify({"error": "stanza_count harus integer"}), 400
    if stanza_count <= 0:
        return jsonify({"error": "stanza_count harus lebih besar dari 0"}), 400
    if stanza_count > 10:
        return jsonify({"error": "stanza_count maksimal 10"}), 400

    try:
        result = create_poem(theme=theme, mood=mood, stanza_count=stanza_count)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@poem_bp.route("/poems", methods=["GET"])
def get_all():
    data = get_all_poems()
    return jsonify(data)


@poem_bp.route("/poems/<int:poem_id>", methods=["GET"])
def get_detail(poem_id: int):
    poem = get_poem_by_id(poem_id)
    if not poem:
        return jsonify({"error": "Poem not found"}), 404
    return jsonify(poem)