from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import config

def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session


# Get the user's preferred language
def get_language_preferences(user_id):
    session = connect_to_astra()
    query = "SELECT language FROM language_preferences WHERE user_id = %s"
    result = session.execute(query, [user_id])
    if result:
        return {"language": result[0].language}
    return {"language": "en"}

# Set or update the user's preferred language
def set_language_preferences(user_id, language):
    session = connect_to_astra()
    query = "INSERT INTO language_preferences (user_id, language) VALUES (%s, %s)"
    session.execute(query, [user_id, language])
