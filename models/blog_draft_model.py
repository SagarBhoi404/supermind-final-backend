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

# Create a new blog draft
def create_blog_draft(draft_id, user_id, title, content, language, created_at, updated_at):
    session = connect_to_astra()
    query = """
    INSERT INTO blog_drafts (draft_id, user_id, title, content, language, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (draft_id, user_id, title, content, language, created_at, updated_at))

# Update an existing blog draft
def update_blog_draft(draft_id, title, content, language, updated_at):
    session = connect_to_astra()
    query = """
    UPDATE blog_drafts
    SET title = %s, content = %s, language = %s, updated_at = %s
    WHERE draft_id = %s
    """
    session.execute(query, (title, content, language, updated_at, draft_id))

# Get all blog drafts
def get_blog_drafts():
    session = connect_to_astra()
    query = "SELECT * FROM blog_drafts"
    result = session.execute(query)
    drafts = [{"draft_id": row.draft_id, "user_id": row.user_id, "title": row.title, "content": row.content, "language": row.language, "created_at": row.created_at, "updated_at": row.updated_at} for row in result]
    return drafts
