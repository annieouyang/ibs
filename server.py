import os
import base64
import json
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

PROMPT = """You are a registered dietitian specializing in the low-FODMAP diet for IBS management.

Analyze this image. It may be a restaurant menu with multiple items listed, or a photo of a single dish.

For EACH identifiable dish or menu item visible, provide a FODMAP analysis and estimate where that item's name/label appears in the image as x/y percentage coordinates (0,0 = top-left corner, 100,100 = bottom-right corner).

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{
  "dishes": [
    {
      "dish_name": "Name of the dish",
      "score": <integer 0-100, where 100 = perfectly FODMAP-safe, 0 = extremely high FODMAP>,
      "rating": "Safe" | "Moderate" | "Avoid",
      "summary": "2-sentence plain-English explanation of why this dish received this score.",
      "safe_ingredients": ["ingredient1", "ingredient2"],
      "problematic_ingredients": ["ingredient1", "ingredient2"],
      "modification_tips": ["tip1", "tip2", "tip3"],
      "position": {"x": <0-100>, "y": <0-100>}
    }
  ]
}

Scoring guide:
- 80-100: Low FODMAP, safe for most IBS sufferers
- 50-79: Moderate, some FODMAPs present, portion-dependent
- 0-49: High FODMAP, likely to trigger symptoms

Position guide:
- For a single dish photo with no visible label, use {"x": 50, "y": 50}
- For a menu, estimate the center-point of where each dish name appears on the page
- Spread positions so badges do not overlap (at least 12 units apart)

If you cannot identify any food items, return: {"dishes": [], "error": "No menu items detected"}"""


@app.route("/")
def index():
    return send_from_directory(".", "ibs-fodmap-analyzer.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    image_b64 = data.get("image")
    media_type = data.get("media_type", "image/jpeg")

    if not image_b64:
        return jsonify({"error": "No image provided"}), 400

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": PROMPT}
                ],
            }],
        )

        text = message.content[0].text.strip()
        result = json.loads(text.replace("```json", "").replace("```", "").strip())
        return jsonify(result)

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse model response: {text}"}), 500
    except anthropic.APIStatusError as e:
        return jsonify({"error": f"API error {e.status_code}: {e.message}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("Run: export ANTHROPIC_API_KEY=sk-ant-...")
        exit(1)
    print("gutwise running at http://localhost:5050")
    app.run(port=5050, debug=True)
