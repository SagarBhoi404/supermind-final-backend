from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
from models.blog_translation_model import (
    connect_to_astra,
    create_blog_translations_table,
    insert_translation,
    get_translations_by_blog_id,
    get_translation_by_language,
    update_translation,
    delete_translation
)

blog_translation_bp = Blueprint('blog_translation', __name__)

# Start translation for a blog
@blog_translation_bp.route('/api/blogs/<uuid:blog_id>/translate', methods=['POST'])
def start_translation(blog_id):
    data = request.json
    language = data['language']
    translated_content = data['translated_content']
    translation_accuracy = data.get('translation_accuracy', 0)
    created_at = updated_at = datetime.now()

    session = connect_to_astra()
    create_blog_translations_table(session)

    translation_id = uuid.uuid4()
    insert_translation(session, translation_id, blog_id, language, translated_content, translation_accuracy, created_at, updated_at)

    return jsonify({'message': 'Translation created successfully', 'translation_id': str(translation_id)}), 201

# Get all translations of a blog
@blog_translation_bp.route('/api/blogs/<uuid:blog_id>/translations', methods=['GET'])
def get_translations(blog_id):
    session = connect_to_astra()
    translations = get_translations_by_blog_id(session, blog_id)

    # Convert each translation row to a dictionary
    translations_list = []
    for translation in translations:
        translations_list.append({
            'blog_id': str(translation.blog_id),
            'language': translation.language,
            'translated_content': translation.translated_content,
            'translation_accuracy': translation.translation_accuracy,
            'created_at': translation.created_at.isoformat() if translation.created_at else None,
            'updated_at': translation.updated_at.isoformat() if translation.updated_at else None
        })

    return jsonify(translations_list), 200

# Get a specific translation by language
@blog_translation_bp.route('/api/blogs/<uuid:blog_id>/translations/<string:language>', methods=['GET'])
def get_translation(blog_id, language):
    session = connect_to_astra()
    translation = get_translation_by_language(session, blog_id, language)
    return jsonify(dict(translation)) if translation else jsonify({'message': 'Translation not found'}), 404

# Update a specific translation
@blog_translation_bp.route('/api/blogs/<uuid:blog_id>/translations/<string:language>', methods=['PUT'])
def edit_translation(blog_id, language):
    data = request.json
    translated_content = data['translated_content']
    translation_accuracy = data.get('translation_accuracy', 0)
    updated_at = datetime.now()

    session = connect_to_astra()
    update_translation(session, blog_id, language, translated_content, translation_accuracy, updated_at)
    return jsonify({'message': 'Translation updated successfully'}), 200

# Delete a specific translation
@blog_translation_bp.route('/api/blogs/<uuid:blog_id>/translations/<string:language>', methods=['DELETE'])
def delete_translation_endpoint(blog_id, language):
    session = connect_to_astra()
    delete_translation(session, blog_id, language)
    return jsonify({'message': 'Translation deleted successfully'}), 200
