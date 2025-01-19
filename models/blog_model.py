from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from datetime import datetime

import config


def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session


def create_blogs_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS blogs (
            blog_id UUID PRIMARY KEY,
            user_id UUID,
            title TEXT,
            content TEXT,
            status TEXT,
            language TEXT,
            translation_status TEXT,
            seo_url TEXT,
            seo_metadata TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
        );
    """)


import uuid

def insert_blog(session, blog_id, user_id, title, content, status, language, translation_status, seo_url, seo_metadata, created_at, updated_at):
    query = """
    INSERT INTO blogs (
        blog_id, user_id, title, content, status, language, translation_status, seo_url, seo_metadata, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    prepared = session.prepare(query)

    # Convert user_id and blog_id to UUID objects if they are not already
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    if isinstance(blog_id, str):
        blog_id = uuid.UUID(blog_id)

    session.execute(prepared, [blog_id, user_id, title, content, status, language, translation_status, seo_url, seo_metadata, created_at, updated_at])



def get_blog_by_id(session, blog_id):
    rows = session.execute("SELECT * FROM blogs WHERE blog_id = %s", (blog_id,))
    return rows.one()


def get_all_blogs(session, language=None, status=None):
    query = "SELECT * FROM blogs"
    filters = []
    params = []

    # Build filters dynamically
    if language:
        filters.append("language = %s")
        params.append(language)
    if status:
        filters.append("status = %s")
        params.append(status)

    # If there are filters, add a WHERE clause
    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Add ALLOW FILTERING only if necessary
    if language or status:
        query += " ALLOW FILTERING"

    # Execute the query
    rows = session.execute(query, tuple(params))

    # Convert rows to a list of dictionaries
    blogs = []
    for row in rows:
        blogs.append(dict(row._asdict()))  # Convert Cassandra Row to dictionary

    return blogs



def update_blog(session, blog_id, title, content, status, language, translation_status, seo_url, seo_metadata,
                updated_at):
    session.execute("""
        UPDATE blogs SET title = %s, content = %s, status = %s, language = %s, translation_status = %s, seo_url = %s, seo_metadata = %s, updated_at = %s
        WHERE blog_id = %s
    """, (title, content, status, language, translation_status, seo_url, seo_metadata, updated_at, blog_id))


def delete_blog(session, blog_id):
    session.execute("DELETE FROM blogs WHERE blog_id = %s", (blog_id,))
