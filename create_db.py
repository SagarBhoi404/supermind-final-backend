from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import config

# Connect to Cassandra
cloud_config = {'secure_connect_bundle': config.ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}
auth_provider = PlainTextAuthProvider(config.ASTRA_DB_CLIENT_ID, config.ASTRA_DB_CLIENT_SECRET)

try:
    # Initialize cluster and session
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()

    # Create keyspace if it doesn't exist
    keyspace = "blog"
    # session.execute(f"""
    #     CREATE KEYSPACE IF NOT EXISTS {keyspace}
    #     WITH replication = {{
    #         'class': 'SimpleStrategy',
    #         'replication_factor': 3
    #     }}
    # """)
    # print(f"Keyspace {keyspace} created or already exists.")

    # Use the created keyspace
    session.set_keyspace(keyspace)

    # Define the table creation queries
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT,
            role TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
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
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS translations (
            translation_id UUID PRIMARY KEY,
            blog_id UUID,
            language TEXT,
            content TEXT,
            status TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS comments (
            comment_id UUID PRIMARY KEY,
            blog_id UUID,
            user_id UUID,
            content TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tags (
            tag_id UUID PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS blog_tags (
            blog_id UUID,
            tag_id UUID,
            PRIMARY KEY (blog_id, tag_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id UUID PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS blog_categories (
            blog_id UUID,
            category_id UUID,
            PRIMARY KEY (blog_id, category_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS seo_metadata (
            seo_metadata_id UUID PRIMARY KEY,
            blog_id UUID,
            metadata TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS analytics (
            blog_id UUID PRIMARY KEY,
            views INT,
            engagement_metrics TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS languages (
            language_code TEXT PRIMARY KEY,
            language_name TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users_sessions (
            session_id UUID PRIMARY KEY,
            user_id UUID,
            login_time TIMESTAMP,
            logout_time TIMESTAMP,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """
    ]

    # Execute the queries to create the tables
    for query in queries:
        try:
            session.execute(query)
            print("Query executed successfully:", query.split()[1])
        except Exception as e:
            print(f"Error executing query: {e}")

except Exception as e:
    print(f"Error connecting to Astra DB: {e}")
finally:
    # Close the connection
    if cluster:
        cluster.shutdown()
    print("Connection closed.")

print("Keyspace and tables created successfully.")
