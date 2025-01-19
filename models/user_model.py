from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import uuid
from datetime import datetime
import config

# Connect to Astra DB
def connect_to_astra():
    cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
    auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect(config.ASTRA_DB_KEYSPACE)
    return session

# Create users table if it doesn't exist
def create_users_table(session):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        user_id UUID PRIMARY KEY,
        name TEXT,
        email TEXT,
        password TEXT,
        role TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """
    session.execute(create_table_query)

# Insert user data into the users table
def insert_user(session, user_id, name, email, password, role, created_at, updated_at):
    insert_query = """
    INSERT INTO users (user_id, name, email, password, role, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(insert_query, (user_id, name, email, password, role, created_at, updated_at))

# Query user by email
def get_user_by_email(session, email):
    query = "SELECT * FROM users WHERE email = %s ALLOW FILTERING"
    result = session.execute(query, [email])
    return result.one()

# Query user by user_id
def get_user_by_id(session, user_id):
    query = "SELECT * FROM users WHERE user_id = %s ALLOW FILTERING"
    result = session.execute(query, [uuid.UUID(user_id)])
    return result.one()

# Update user data
def update_user(session, user_id, name, email, role, updated_at):
    update_query = """
    UPDATE users SET name = %s, email = %s, role = %s, updated_at = %s WHERE user_id = %s ALLOW FILTERING
    """
    session.execute(update_query, (name, email, role, updated_at, uuid.UUID(user_id)))
