from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
from models.video_model import (
    connect_to_astra,
    create_video_uploads_table,
    insert_video,
    get_video_status,
    update_video_transcription,
)

video_bp = Blueprint('video', __name__)

# Upload a video
@video_bp.route('/api/videos/upload', methods=['POST'])
def upload_video():
    data = request.json
    user_id = data['user_id']
    file_name = data['file_name']
    file_url = data['file_url']
    created_at = updated_at = datetime.now()

    session = connect_to_astra()
    create_video_uploads_table(session)

    video_id = uuid.uuid4()
    insert_video(session, video_id, user_id, file_name, file_url, created_at, updated_at)

    return jsonify({'message': 'Video uploaded successfully', 'video_id': str(video_id)}), 201

# Get video status
@video_bp.route('/api/videos/<uuid:video_id>/status', methods=['GET'])
def get_video_status_endpoint(video_id):
    session = connect_to_astra()
    video = get_video_status(session, video_id)
    return jsonify(dict(video)) if video else jsonify({'message': 'Video not found'}), 404

# Start transcription for a video
@video_bp.route('/api/videos/<uuid:video_id>/transcribe', methods=['POST'])
def start_transcription(video_id):
    session = connect_to_astra()
    transcription_content = "Sample transcribed content"
    updated_at = datetime.now()
    update_video_transcription(session, video_id, transcription_content, updated_at)
    return jsonify({'message': 'Transcription started successfully'}), 200
