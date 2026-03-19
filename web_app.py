from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template_string, request

from app import predict_skills
from src.common import DEFAULT_SAMPLE_TEXT_PATH


app = Flask(__name__)

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Skill Prediction</title>
  </head>
  <body>
    <h1>Skill Prediction</h1>

    <form method="post">
      <p>
        <label for="text">Job Description</label><br>
        <textarea id="text" name="text" rows="14" cols="100">{{ text }}</textarea>
      </p>
      <p>
        <button type="submit" name="action" value="predict">Predict</button>
        <button type="submit" name="action" value="sample">Use Sample</button>
        <button type="submit" name="action" value="clear">Clear</button>
      </p>
    </form>

    {% if error %}
    <p><strong>Error:</strong> {{ error }}</p>
    {% endif %}

    {% if result %}
    <h2>Summary</h2>
    <ul>
      <li>Total Predicted Skills: {{ result.summary.total_predicted_skills }}</li>
      <li>Threshold: {{ result.summary.threshold }}</li>
      <li>Top Category: {{ result.summary.top_category }}</li>
    </ul>

    <h2>Predicted Skills</h2>
    <table border="1" cellpadding="8" cellspacing="0">
      <thead>
        <tr>
          <th>Skill</th>
          <th>Category</th>
          <th>Confidence</th>
        </tr>
      </thead>
      <tbody>
        {% for row in result.predicted_skills %}
        <tr>
          <td>{{ row.name }}</td>
          <td>{{ row.category }}</td>
          <td>{{ row.confidence }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% endif %}
  </body>
</html>
"""


def sample_text() -> str:
    path = Path(DEFAULT_SAMPLE_TEXT_PATH)
    return path.read_text(encoding="utf-8") if path.exists() else ""


@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    result = None
    error = ""

    if request.method == "POST":
        action = request.form.get("action", "predict")

        if action == "sample":
            text = sample_text()
        elif action == "clear":
            text = ""
        else:
            text = request.form.get("text", "").strip()
            if not text:
                error = "Input text is empty."
            else:
                try:
                    result = predict_skills(text=text, threshold=None, top_k=12, min_predictions=5)
                except Exception as exc:  # pragma: no cover
                    error = str(exc)

    return render_template_string(PAGE_TEMPLATE, text=text, result=result, error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
