from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
from image_to_glb import image_to_colored_glb

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/textures'
app.config['MODEL_FOLDER'] = 'static/models'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and model folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Generate .glb model
            model_path = os.path.join(app.config['MODEL_FOLDER'], f"{os.path.splitext(filename)[0]}.glb")
            try:
                image_to_colored_glb(filepath, model_path)
                return jsonify({
                    'success': True,
                    'model_path': f"/static/models/{os.path.splitext(filename)[0]}.glb"
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
    
    return render_template('index.html')

@app.route('/ar_viewer')
def ar_viewer():
    model = request.args.get('model')
    return render_template('ar_viewer.html', model_path=f"/static/models/{model}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)
