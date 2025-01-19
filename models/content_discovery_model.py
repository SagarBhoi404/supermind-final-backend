from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import config

def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session

# Get all blogs in a specific category
def get_blogs_by_category(category_id):
    session = connect_to_astra()
    query = """
    SELECT b.blog_id, b.title FROM blogs b
    JOIN blog_categories bc ON b.blog_id = bc.blog_id
    WHERE bc.category_id = %s
    """
    result = session.execute(query, [category_id])
    return [{"blog_id": row.blog_id, "title": row.title} for row in result]

# Get all blogs with a specific tag
def get_blogs_by_tag(tag_id):
    session = connect_to_astra()
    query = """
    SELECT b.blog_id, b.title FROM blogs b
    JOIN blog_tags bt ON b.blog_id = bt.blog_id
    WHERE bt.tag_id = %s
    """
    result = session.execute(query, [tag_id])
    return [{"blog_id": row.blog_id, "title": row.title} for row in result]

# Search blogs by keyword
def search_blogs(query):
    session = connect_to_astra()
    search_query = f"SELECT blog_id, title FROM blogs WHERE title LIKE %s"
    result = session.execute(search_query, [f"%{query}%"])
    return [{"blog_id": row.blog_id, "title": row.title} for row in result]
