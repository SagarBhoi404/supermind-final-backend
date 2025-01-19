import os
from docx import Document
import PyPDF2
import speech_recognition as sr
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
from models.seo_model import get_seo_metadata, generate_sitemap
from models.dashboard_model import get_dashboard_stats, get_users, get_recent_activity
from models.langauge_pre_model import get_language_preferences, set_language_preferences
from models.content_discovery_model import get_blogs_by_category, get_blogs_by_tag, search_blogs
from models.blog_draft_model import create_blog_draft, update_blog_draft, get_blog_drafts


import config

# Connect to Astra DB
def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session

# SEO Controller
seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/api/seo/<uuid:blog_id>', methods=['GET'])
def get_blog_seo(blog_id):
    metadata = get_seo_metadata(blog_id)
    return jsonify(metadata), 200

@seo_bp.route('/api/seo/sitemap', methods=['GET'])
def get_sitemap():
    sitemap = generate_sitemap()
    return jsonify(sitemap), 200

@seo_bp.route('/api/blog/<string:seo_url>', methods=['GET'])
def get_blog_by_seo_url(seo_url):
    blog = get_blog_by_seo_url(seo_url)
    if blog:
        return jsonify(blog), 200
    return jsonify({"message": "Blog not found"}), 404

# Dashboard Controller
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    stats = get_dashboard_stats()
    return jsonify(stats), 200

@dashboard_bp.route('/api/dashboard/users', methods=['GET'])
def list_users():
    users = get_users()
    return jsonify(users), 200

@dashboard_bp.route('/api/dashboard/recent-activity', methods=['GET'])
def get_recent_activity():
    activity = get_recent_activity()
    return jsonify(activity), 200

# Language Preferences Controller
language_bp = Blueprint('language', __name__)

@language_bp.route('/api/language-preferences', methods=['GET'])
def get_language():
    user_id = request.args.get('user_id')
    language = get_language_preferences(user_id)
    return jsonify(language), 200

@language_bp.route('/api/language-preferences', methods=['POST'])
def set_language():
    data = request.json
    user_id = data['user_id']
    language = data['language']
    set_language_preferences(user_id, language)
    return jsonify({"message": "Language preference updated successfully"}), 200

# Content Discovery Controller
content_bp = Blueprint('content', __name__)

@content_bp.route('/api/blogs/categories/<uuid:category_id>', methods=['GET'])
def get_blogs_by_category_route(category_id):
    blogs = get_blogs_by_category(category_id)
    return jsonify(blogs), 200

@content_bp.route('/api/blogs/tags/<uuid:tag_id>', methods=['GET'])
def get_blogs_by_tag_route(tag_id):
    blogs = get_blogs_by_tag(tag_id)
    return jsonify(blogs), 200

@content_bp.route('/api/blogs/search', methods=['GET'])
def search_blogs_route():
    query = request.args.get('query')
    blogs = search_blogs(query)
    return jsonify(blogs), 200

# Blog Drafts Controller
draft_bp = Blueprint('draft', __name__)

@draft_bp.route('/api/blog-drafts', methods=['POST'])
def create_draft():
    data = request.json
    draft_id = uuid.uuid4()
    user_id = data['user_id']
    title = data['title']
    content = data['content']
    language = data['language']
    created_at = updated_at = datetime.now()

    create_blog_draft(draft_id, user_id, title, content, language, created_at, updated_at)
    return jsonify({"message": "Draft created successfully"}), 201

@draft_bp.route('/api/blog-drafts/<uuid:draft_id>', methods=['PUT'])
def update_draft(draft_id):
    data = request.json
    title = data['title']
    content = data['content']
    language = data['language']
    updated_at = datetime.now()

    update_blog_draft(draft_id, title, content, language, updated_at)
    return jsonify({"message": "Draft updated successfully"}), 200

@draft_bp.route('/api/blog-drafts', methods=['GET'])
def list_drafts():
    drafts = get_blog_drafts()
    return jsonify(drafts), 200

# Blog Tags and Categories Controller
tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/api/blogs/<uuid:blog_id>/tags', methods=['GET'])
def get_tags_for_blog_route(blog_id):
    tags = get_tags_for_blog(blog_id)
    return jsonify(tags), 200

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/api/blogs/<uuid:blog_id>/categories', methods=['GET'])
def get_categories_for_blog_route(blog_id):
    categories = get_categories_for_blog(blog_id)
    return jsonify(categories), 200


# Get all tags for a specific blog
def get_tags_for_blog(blog_id):
    session = connect_to_astra()
    query = """
    SELECT t.tag_id, t.name FROM tags t
    JOIN blog_tags bt ON t.tag_id = bt.tag_id
    WHERE bt.blog_id = %s
    """
    result = session.execute(query, [blog_id])
    tags = [{"tag_id": row.tag_id, "name": row.name} for row in result]
    return tags

# Get all categories for a specific blog
def get_categories_for_blog(blog_id):
    session = connect_to_astra()
    query = """
    SELECT c.category_id, c.name FROM categories c
    JOIN blog_categories bc ON c.category_id = bc.category_id
    WHERE bc.blog_id = %s
    """
    result = session.execute(query, [blog_id])
    categories = [{"category_id": row.category_id, "name": row.name} for row in result]
    return categories


# Define the extraction functions
def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return '\n'.join(text)


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
    return '\n'.join(text)


def extract_audio_from_video(file_path):
    video = VideoFileClip(file_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path


def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio_path)

    with audio_file as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Audio is not clear or language is not English"
    except sr.RequestError:
        return "Could not request results from Google Speech Recognition service"


def get_text(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.txt':
        return extract_text_from_txt(file_path)

    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)

    elif file_extension == '.pdf':
        return extract_text_from_pdf(file_path)

    elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
        # Extract audio from video and convert to text
        audio_path = extract_audio_from_video(file_path)
        text = convert_audio_to_text(audio_path)
        os.remove(audio_path)  # Clean up the temporary audio file
        return text

    else:
        return "Unsupported file format."



