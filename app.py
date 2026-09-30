
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key is missing in .env")

client = genai.Client(api_key=api_key)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_plan():

    try:
        data = request.get_json()

        name = data.get("name")
        age = int(data.get("age"))
        weight = float(data.get("weight"))
        height = float(data.get("height"))
        goal = data.get("goal")
        level = data.get("level")
        diet = data.get("diet")

        if not name or not (13 <= age <= 100):
            return jsonify({"error": "Please enter valid details"}), 400

        if not (1 <= weight <= 500 and 50 <= height <= 250):
            return jsonify({"error": "Invalid height or weight"}), 400

        if goal not in ["Weight Loss", "Muscle Gain",
                        "General Fitness", "Improve Stamina"]:
            return jsonify({"error": "Invalid fitness goal"}), 400

        if level not in ["Beginner", "Intermediate", "Advanced"]:
            return jsonify({"error": "Invalid fitness level"}), 400

        if diet not in ["Vegetarian", "Non-Vegetarian", "Vegan"]:
            return jsonify({"error": "Invalid diet preference"}), 400

        prompt = f"""
        You are FitBuddy, an AI fitness planning assistant.

        Create a beginner-friendly and safe educational fitness plan.

        User details:
        Name: {name}
        Age: {age}
        Weight: {weight} kg
        Height: {height} cm
        Fitness Goal: {goal}
        Fitness Level: {level}
        Diet Preference: {diet}

        Include:
        1. Personalized fitness overview
        2. Seven-day workout schedule
        3. Exercise names and beginner-friendly instructions
        4. Rest and recovery guidance
        5. General balanced meal suggestions
        6. Hydration and healthy lifestyle tips

        Use clear headings and simple language.
        Avoid extreme diets, unsafe weight-loss targets,
        medical diagnoses, or guaranteed results.
        Mention that users with medical conditions should
        consult a qualified healthcare professional.
        """

        last_unavailable_error = None
        for model in ("gemini-3.8-flash", "gemini-3-flash-preview"):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
            except Exception as error:
                if getattr(error, "code", None) != 503:
                    raise
                app.logger.warning(
                    "Gemini model %s is temporarily unavailable", model,
                    exc_info=True
                )
                last_unavailable_error = error
                continue

            if response.text:
                return jsonify({"plan": response.text})

        if last_unavailable_error:
            return jsonify({
                "error": "Gemini is temporarily busy. Please try again shortly."
            }), 503

        return jsonify({
            "error": "Gemini returned an empty response. Please try again."
        }), 502

    except Exception as e:
        app.logger.exception("Fitness plan generation failed")
        if getattr(e, "code", None) == 429:
            return jsonify({
                "error": "The Gemini API quota is temporarily unavailable. Please try again later."
            }), 429
        return jsonify({
            "error": "Unable to generate the plan. Check your Gemini API key and connection."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)