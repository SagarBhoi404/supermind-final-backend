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

# Create blog_translations table if it doesn't exist
def create_blog_translations_table(session):
    query = """
    CREATE TABLE IF NOT EXISTS blog_translations (
        translation_id UUID PRIMARY KEY,
        blog_id UUID,
        language TEXT,
        translated_content TEXT,
        translation_accuracy DECIMAL,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """
    session.execute(query)

# Insert a translation
def insert_translation(session, translation_id, blog_id, language, translated_content, translation_accuracy, created_at, updated_at):
    query = """
    INSERT INTO blog_translations (translation_id, blog_id, language, translated_content, 
    translation_accuracy, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (translation_id, blog_id, language, translated_content, translation_accuracy, created_at, updated_at))

# Get translations by blog_id
def get_translations_by_blog_id(session, blog_id):
    query = "SELECT * FROM blog_translations WHERE blog_id = %s ALLOW FILTERING"
    rows = session.execute(query, [blog_id])
    return rows

# Get a translation by blog_id and language
def get_translation_by_language(session, blog_id, language):
    query = "SELECT * FROM blog_translations WHERE blog_id = %s AND language = %s ALLOW FILTERING"
    row = session.execute(query, [blog_id, language]).one()
    return row

# Update a translation
def update_translation(session, blog_id, language, translated_content, translation_accuracy, updated_at):
    query = """
    UPDATE blog_translations SET translated_content = %s, translation_accuracy = %s, updated_at = %s 
    WHERE blog_id = %s AND language = %s ALLOW FILTERING
    """
    session.execute(query, [translated_content, translation_accuracy, updated_at, blog_id, language])

# Delete a translation
def delete_translation(session, blog_id, language):
    query = "DELETE FROM blog_translations WHERE blog_id = %s AND language = %s ALLOW FILTERING"
    session.execute(query, [blog_id, language])
