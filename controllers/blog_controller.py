from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
from models.blog_model import connect_to_astra, create_blogs_table, insert_blog, get_blog_by_id, get_all_blogs, update_blog, delete_blog
from models.blog_translation_model import create_blog_translations_table

blog_bp = Blueprint('blog', __name__)

from googletrans import Translator


def translate_text(content, target_language):
    """
    Translates the given content into the target language.

    Args:
        content (str): The text to be translated.
        target_language (str): The target language code (e.g., 'hi' for Hindi).

    Returns:
        str: The translated text.
    """
    try:
        # Create a Translator instance
        translator = Translator()

        # Perform the translation
        translation = translator.translate(content, dest=target_language)

        # Return the translated text
        return translation.text

    except Exception as e:
        print(f"Error during translation: {e}")
        return f"Translation failed for language: {target_language}"


@blog_bp.route('/api/blogs', methods=['POST'])
def create_blog():
    # Get the data from the request
    data = request.json

    # Validate required fields
    required_fields = ['user_id', 'title', 'content', 'status', 'language', 'seo_url', 'seo_metadata']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Extract data
    user_id = data['user_id']
    title = data['title']
    content = data['content']
    status = data['status']
    language = data['language']  # Assuming this is the original language
    translation_status = data.get('translation_status', 'pending')  # Default to 'pending'
    seo_url = data['seo_url']
    seo_metadata = data['seo_metadata']
    created_at = updated_at = datetime.now()

    # Connect to the database and ensure tables exist
    session = connect_to_astra()
    create_blogs_table(session)
    create_blog_translations_table(session)  # Ensure the translations table exists

    # Create the blog entry in the database
    blog_id = uuid.uuid4()
    insert_blog(session, blog_id, user_id, title, content, status, language, translation_status, seo_url, seo_metadata,
                created_at, updated_at)

    # Automatically translate the blog content into 10 Indian languages
    indian_languages = [
        'hi', 'mr', 'gu', 'ta', 'kn', 'te', 'bn', 'ml', 'pa', 'or'
    ]  # Hindi, Marathi, Gujarati, Tamil, Kannada, Telugu, Bengali, Malayalam, Punjabi, Odia
    for lang in indian_languages:
        translated_content = translate_text(content, lang)  # Translate the content
        translation_accuracy = None  # Set this based on your translation evaluation logic
        insert_translation(session, blog_id, lang, translated_content, translation_accuracy, created_at, updated_at)

    return jsonify({'message': 'Blog created successfully with translations'}), 201


def create_translations_table(session):
    """
    Ensures the translations table exists in the database.
    """
    query = """
    CREATE TABLE IF NOT EXISTS blog_translations (
        blog_id UUID,
        language TEXT,
        translated_content TEXT,
        translation_accuracy DECIMAL,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        PRIMARY KEY (blog_id, language)
    )
    """
    session.execute(query)


def insert_translation(session, blog_id, language, translated_content, translation_accuracy, created_at, updated_at):
    """
    Inserts a translated blog entry into the blog_translations table.
    """
    query = """
    INSERT INTO blog_translations (blog_id, language, translated_content, translation_accuracy, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (blog_id, language, translated_content, translation_accuracy, created_at, updated_at))

@blog_bp.route('/api/blogs/<uuid:blog_id>', methods=['PUT'])
def edit_blog(blog_id):
    data = request.json
    title = data['title']
    content = data['content']
    status = data['status']
    language = data['language']
    translation_status = data['translation_status']
    seo_url = data['seo_url']
    seo_metadata = data['seo_metadata']
    updated_at = datetime.now()

    session = connect_to_astra()
    update_blog(session, blog_id, title, content, status, language, translation_status, seo_url, seo_metadata, updated_at)

    return jsonify({'message': 'Blog updated successfully'}), 200

@blog_bp.route('/api/blogs/<uuid:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    session = connect_to_astra()
    delete_blog(session, blog_id)

    return jsonify({'message': 'Blog deleted successfully'}), 200

@blog_bp.route('/api/blogs/<uuid:blog_id>', methods=['GET'])
def get_blog(blog_id):
    session = connect_to_astra()
    blog = get_blog_by_id(session, blog_id)

    if blog:
        # Assuming 'blog' is a tuple, construct a dictionary manually
        blog_dict = {
            'blog_id': blog[0],
            'user_id': blog[1],
            'title': blog[2],
            'content': blog[3],
            'status': blog[4],
            'language': blog[5],
            'translation_status': blog[6],
            'seo_url': blog[7],
            'seo_metadata': blog[8],
            'created_at': str(blog[9]),  # Ensure timestamp is stringified
            'updated_at': str(blog[10]) # Ensure timestamp is stringified
        }
        return jsonify(blog_dict), 200
    else:
        return jsonify({'message': 'Blog not found'}), 404

@blog_bp.route('/api/blog/<string:seo_url>', methods=['GET'])
def get_blog_by_seo_url(seo_url):
    try:
        session = connect_to_astra()  # Connect to Cassandra

        # Trim leading/trailing spaces in seo_url
        seo_url = seo_url.strip()

        query = "SELECT * FROM blogs WHERE seo_url = %s ALLOW FILTERING"
        result = session.execute(query, [seo_url])

        # Log the result to debug
        if not result:
            print(f"No result found for seo_url: '{seo_url}'")
        else:
            print(f"Found result(s) for seo_url: '{seo_url}'")

        # Use result.all() for better results debugging
        blogs = result.all()

        if blogs:
            blog = blogs[0]  # Get the first matching result
            blog_dict = {
                'blog_id': str(blog[0]),  # Convert UUID to string
                'user_id': str(blog[1]),
                'title': blog[2],
                'content': blog[3],
                'status': blog[4],
                'language': blog[5],
                'translation_status': blog[6],
                'seo_url': blog[7],
                'seo_metadata': blog[8],
                'created_at': blog[9].isoformat() if blog[9] else None,
                'updated_at': blog[10].isoformat() if blog[10] else None
            }
            return jsonify(blog_dict), 200
        else:
            return jsonify({'message': 'Blog not found'}), 404

    except Exception as e:
        print(f"Error while fetching blog by seo_url: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500



@blog_bp.route('/api/blogs', methods=['GET'])
def list_blogs():
    language = request.args.get('language')
    status = request.args.get('status')

    session = connect_to_astra()
    blogs = get_all_blogs(session, language, status)

    return jsonify([dict(blog) for blog in blogs]), 200


@blog_bp.route('/api/blogs/<uuid:blog_id>/publish', methods=['POST'])
def publish_blog(blog_id):
    session = connect_to_astra()
    blog = get_blog_by_id(session, blog_id)

    if blog:
        update_blog(session, blog_id, blog.title, blog.content, 'published', blog.language, blog.translation_status, blog.seo_url, blog.seo_metadata, datetime.now())
        return jsonify({'message': 'Blog published successfully'}), 200
    else:
        return jsonify({'message': 'Blog not found'}), 404

@blog_bp.route('/api/blogs/<uuid:blog_id>/draft', methods=['POST'])
def draft_blog(blog_id):
    session = connect_to_astra()
    blog = get_blog_by_id(session, blog_id)

    if blog:
        update_blog(session, blog_id, blog.title, blog.content, 'draft', blog.language, blog.translation_status, blog.seo_url, blog.seo_metadata, datetime.now())
        return jsonify({'message': 'Blog saved as draft'}), 200
    else:
        return jsonify({'message': 'Blog not found'}), 404
