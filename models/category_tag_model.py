from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import config

# Connect to Astra DB
def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session

# Create categories table
def create_categories_table(session):
    query = """
    CREATE TABLE IF NOT EXISTS categories (
        category_id UUID PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """
    session.execute(query)

# Create tags table
def create_tags_table(session):
    query = """
    CREATE TABLE IF NOT EXISTS tags (
        tag_id UUID PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """
    session.execute(query)

# Category operations
def insert_category(session, category_id, name, created_at, updated_at):
    query = """
    INSERT INTO categories (category_id, name, created_at, updated_at)
    VALUES (%s, %s, %s, %s)
    """
    session.execute(query, (category_id, name, created_at, updated_at))

def get_all_categories(session):
    query = "SELECT * FROM categories"
    rows = session.execute(query)
    return rows

def update_category(session, category_id, name, updated_at):
    query = """
    UPDATE categories SET name = %s, updated_at = %s WHERE category_id = %s
    """
    session.execute(query, (name, updated_at, category_id))

def delete_category(session, category_id):
    query = "DELETE FROM categories WHERE category_id = %s"
    session.execute(query, [category_id])

# Tag operations
def insert_tag(session, tag_id, name, created_at, updated_at):
    query = """
    INSERT INTO tags (tag_id, name, created_at, updated_at)
    VALUES (%s, %s, %s, %s)
    """
    session.execute(query, (tag_id, name, created_at, updated_at))

def get_all_tags(session):
    query = "SELECT * FROM tags"
    rows = session.execute(query)
    return rows

def update_tag(session, tag_id, name, updated_at):
    query = """
    UPDATE tags SET name = %s, updated_at = %s WHERE tag_id = %s
    """
    session.execute(query, (name, updated_at, tag_id))

def delete_tag(session, tag_id):
    query = "DELETE FROM tags WHERE tag_id = %s"
    session.execute(query, [tag_id])
