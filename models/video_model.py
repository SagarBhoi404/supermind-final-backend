from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

import config


# Connect to Astra DB
def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session



def create_video_uploads_table(session):
    query = """
    CREATE TABLE IF NOT EXISTS video_uploads (
        video_id UUID PRIMARY KEY,
        user_id UUID,
        file_name TEXT,
        file_url TEXT,
        transcription_status TEXT,
        transcribed_content TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """
    session.execute(query)

def insert_video(session, video_id, user_id, file_name, file_url, created_at, updated_at):
    query = """
    INSERT INTO video_uploads (video_id, user_id, file_name, file_url, transcription_status, 
    transcribed_content, created_at, updated_at)
    VALUES (%s, %s, %s, %s, 'pending', NULL, %s, %s)
    """
    session.execute(query, (video_id, user_id, file_name, file_url, created_at, updated_at))

def get_video_status(session, video_id):
    query = "SELECT video_id, transcription_status FROM video_uploads WHERE video_id = %s"
    return session.execute(query, [video_id]).one()

def update_video_transcription(session, video_id, transcription_content, updated_at):
    query = """
    UPDATE video_uploads SET transcription_status = 'completed', transcribed_content = %s, updated_at = %s
    WHERE video_id = %s
    """
    session.execute(query, [transcription_content, updated_at, video_id])
