from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import config
def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session

# Get overall dashboard statistics
def get_dashboard_stats():
    session = connect_to_astra()
    query = "SELECT count(*), sum(views) FROM blogs"
    result = session.execute(query)
    return {"blog_count": result[0].count, "total_views": result[0].sum}

# Get list of users
def get_users():
    session = connect_to_astra()
    query = "SELECT * FROM users"
    result = session.execute(query)
    users = [{"user_id": row.user_id, "name": row.name, "role": row.role} for row in result]
    return users

# Get recent activity on the platform
def get_recent_activity():
    session = connect_to_astra()
    query = "SELECT * FROM activity ORDER BY created_at DESC LIMIT 10"
    result = session.execute(query)
    activity = [{"activity_id": row.activity_id, "action": row.action, "created_at": row.created_at} for row in result]
    return activity
