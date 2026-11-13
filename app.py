"""
Edge TTS Microservice — Docker container that does one thing:
Accept text, return Christopher's voice as MP3 bytes.
"""

import asyncio
import io
from flask import Flask, request, Response, jsonify
import edge_tts

app = Flask(__name__)

DEFAULT_VOICE = "en-US-ChristopherNeural"

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    voice = data.get("voice", DEFAULT_VOICE)
    rate = data.get("rate", "+0%")
    pitch = data.get("pitch", "+0Hz")
    volume = data.get("volume", "+0%")

    try:
        mp3_bytes = asyncio.run(synthesize(text, voice, rate, pitch, volume))
        return Response(mp3_bytes, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


async def synthesize(text, voice, rate, pitch, volume):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "voice": DEFAULT_VOICE})


@app.route("/voices", methods=["GET"])
def voices():
    """List available voices (optional convenience endpoint)."""
    voices_list = asyncio.run(edge_tts.list_voices())
    lang = request.args.get("lang", "en")
    filtered = [v for v in voices_list if v["Locale"].startswith(lang)]
    return jsonify(filtered)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100)
