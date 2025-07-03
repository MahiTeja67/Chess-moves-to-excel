from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import pandas as pd
import tempfile
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Renders templates/index.html

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    if not files or len(files) > 10:
        return "Upload up to 10 PDF files only.", 400

    all_games = []

    for file in files:
        if not file.filename.endswith('.pdf'):
            continue

        pdf = fitz.open(stream=file.read(), filetype="pdf")
        text = "".join([page.get_text() for page in pdf])

        # Extract move pairs like "1. e4 e5"
        move_pairs = re.findall(r'\d+\.\s*\S+(?:\s+\S+)?', text)
        all_games.append(move_pairs)

    # Pad each game row to the same length
    max_len = max(len(game) for game in all_games)
    for game in all_games:
        game += [''] * (max_len - len(game))

    # Convert to DataFrame and save to Excel
    df = pd.DataFrame(all_games)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df.to_excel(temp_file.name, index=False, header=False)

    return send_file(temp_file.name, as_attachment=True, download_name="chess_games.xlsx")

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

