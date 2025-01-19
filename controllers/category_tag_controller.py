from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
from models.category_tag_model import (
    connect_to_astra,
    create_categories_table,
    create_tags_table,
    insert_category,
    get_all_categories,
    update_category,
    delete_category,
    insert_tag,
    get_all_tags,
    update_tag,
    delete_tag
)

category_tag_bp = Blueprint('category_tag', __name__)

# Categories Endpoints
@category_tag_bp.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    name = data['name']
    created_at = updated_at = datetime.now()

    session = connect_to_astra()
    create_categories_table(session)

    category_id = uuid.uuid4()
    insert_category(session, category_id, name, created_at, updated_at)

    return jsonify({'message': 'Category created successfully', 'category_id': str(category_id)}), 201

@category_tag_bp.route('/api/categories', methods=['GET'])
def list_categories():
    session = connect_to_astra()
    categories = get_all_categories(session)
    return jsonify([dict(category) for category in categories]), 200

@category_tag_bp.route('/api/categories/<uuid:category_id>', methods=['PUT'])
def edit_category(category_id):
    data = request.json
    name = data['name']
    updated_at = datetime.now()

    session = connect_to_astra()
    update_category(session, category_id, name, updated_at)
    return jsonify({'message': 'Category updated successfully'}), 200

@category_tag_bp.route('/api/categories/<uuid:category_id>', methods=['DELETE'])
def delete_category_endpoint(category_id):
    session = connect_to_astra()
    delete_category(session, category_id)
    return jsonify({'message': 'Category deleted successfully'}), 200

# Tags Endpoints
@category_tag_bp.route('/api/tags', methods=['POST'])
def create_tag():
    data = request.json
    name = data['name']
    created_at = updated_at = datetime.now()

    session = connect_to_astra()
    create_tags_table(session)

    tag_id = uuid.uuid4()
    insert_tag(session, tag_id, name, created_at, updated_at)

    return jsonify({'message': 'Tag created successfully', 'tag_id': str(tag_id)}), 201

@category_tag_bp.route('/api/tags', methods=['GET'])
def list_tags():
    session = connect_to_astra()
    tags = get_all_tags(session)
    return jsonify([dict(tag) for tag in tags]), 200

@category_tag_bp.route('/api/tags/<uuid:tag_id>', methods=['PUT'])
def edit_tag(tag_id):
    data = request.json
    name = data['name']
    updated_at = datetime.now()

    session = connect_to_astra()
    update_tag(session, tag_id, name, updated_at)
    return jsonify({'message': 'Tag updated successfully'}), 200

@category_tag_bp.route('/api/tags/<uuid:tag_id>', methods=['DELETE'])
def delete_tag_endpoint(tag_id):
    session = connect_to_astra()
    delete_tag(session, tag_id)
    return jsonify({'message': 'Tag deleted successfully'}), 200
