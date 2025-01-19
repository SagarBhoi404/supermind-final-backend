# from flask import Blueprint, jsonify
# from models.blog_analytics_model import connect_to_astra, get_blog_analytics, get_all_blog_analytics
#
# blog_analytics_bp = Blueprint('blog_analytics', __name__)
#
# # Get analytics for a specific blog
# @blog_analytics_bp.route('/api/blogs/<uuid:blog_id>/analytics', methods=['GET'])
# def get_blog_analytics_endpoint(blog_id):
#     session = connect_to_astra()
#     analytics = get_blog_analytics(session, blog_id)
#     return jsonify(dict(analytics)) if analytics else jsonify({'message': 'Analytics not found'}), 404
#
# # List analytics for all blogs
# @blog_analytics_bp.route('/api/blogs/analytics', methods=['GET'])
# def list_blog_analytics():
#     session = connect_to_astra()
#     analytics = get_all_blog_analytics(session)
#     return jsonify([dict(data) for data in analytics]), 200
