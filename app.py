import os

from flask import Flask, request, jsonify
from controllers.user_controller import user_bp
from controllers.blog_controller import blog_bp
from controllers.blog_translation_controller import blog_translation_bp
from controllers.category_tag_controller import category_tag_bp
# from controllers.blog_analytics_controller import blog_analytics_bp
from controllers.video_controller import video_bp
from controllers.other_controllers import seo_bp, dashboard_bp, language_bp, content_bp, draft_bp, tags_bp, get_text
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(blog_translation_bp)
app.register_blueprint(category_tag_bp)
# app.register_blueprint(blog_analytics_bp)

app.register_blueprint(video_bp)
app.register_blueprint(seo_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(language_bp)
app.register_blueprint(content_bp)
app.register_blueprint(draft_bp)
app.register_blueprint(tags_bp)

@app.route('/get_text_from_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save file to a temporary directory
    temp_file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)  # Ensure the directory exists
    file.save(temp_file_path)

    try:
        # Extract text from the file
        extracted_text = get_text(temp_file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
    finally:
        # Ensure the temporary file is deleted
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception as e:
            return jsonify({"error": f"Failed to delete temporary file: {str(e)}"}), 500

    return jsonify({"extracted_text": extracted_text}), 200

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run()
