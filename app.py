from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils.shannon_entropy import calculate_shannon_entropy
from utils.ML_for_ransomware import Check_if_ransomware
import os
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with open('types.json', 'r') as f:
    FILE_TYPES = json.load(f)

def check_if_ransomware(file_path, file_type_index):
    
    entropy, variance = calculate_shannon_entropy(file_path)
    examined_file = {
        'id': 0,
        'type': file_type_index,
        'size': os.path.getsize(file_path),
        'entropy': entropy,
        'variance': variance
    }
    
    ml_result = Check_if_ransomware(examined_file)
    
    return {
        'is_ransomware': ml_result['is_ransomware'],
        'confidence': ml_result['confidence'],
        'risk_level': ml_result['risk_level'],
        'entropy': entropy,
        'variance': variance
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/file-types', methods=['GET'])
def get_file_types():
    sorted_types = sorted(FILE_TYPES.items(), key=lambda x: x[0])
    return jsonify({
        'types': [{'name': name, 'index': index} for name, index in sorted_types]
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Brak pliku w żądaniu'}), 400
    
    file = request.files['file']
    file_type_index = request.form.get('fileTypeIndex', type=int)
    
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    if file_type_index is None:
        return jsonify({'error': 'Nie wybrano typu pliku'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        result = check_if_ransomware(file_path, file_type_index)
        os.remove(file_path)
        
        return jsonify({
            'filename': filename,
            'file_type_index': file_type_index,
            'is_ransomware': result['is_ransomware'],
            'confidence': result['confidence'],
            'risk_level': result['risk_level'],
            'entropy': result.get('entropy', 0.0),
            'variance': result.get('variance', 0.0)
        })
    
    return jsonify({'error': 'Błąd podczas przetwarzania pliku'}), 500

@app.route('/result', methods=['GET'])
def result():
    return render_template('result.html')

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Plik jest za duży (maksymalnie 16MB)'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
