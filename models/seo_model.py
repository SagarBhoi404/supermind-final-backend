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

# Get SEO metadata for a specific blog
def get_seo_metadata(blog_id):
    session = connect_to_astra()
    query = "SELECT seo_url, meta_title, meta_description FROM blogs WHERE blog_id = %s"
    result = session.execute(query, [blog_id])
    blog = result.one()
    if blog:
        return {
            "seo_url": blog.seo_url,
            "meta_title": blog.meta_title,
            "meta_description": blog.meta_description
        }
    return {}

# Generate SEO sitemap
def generate_sitemap():
    session = connect_to_astra()
    query = "SELECT seo_url FROM blogs"
    result = session.execute(query)
    sitemap = [{"url": row.seo_url} for row in result]
    return sitemap
