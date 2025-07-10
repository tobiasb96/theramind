from urllib.parse import urlparse
from collections import namedtuple

DatabaseConfig = namedtuple('DatabaseConfig', ['dbname', 'user', 'password', 'host', 'port'])

def convert_db_connection_string(database_url):
    """
    Convert a database URL string to a database configuration object.
    
    Args:
        database_url (str): Database URL in format: postgres://user:password@host:port/dbname
        
    Returns:
        DatabaseConfig: Named tuple with database connection parameters
    """
    if not database_url:
        raise ValueError("Database URL is required")
    
    parsed = urlparse(database_url)
    
    return DatabaseConfig(
        dbname=parsed.path.lstrip('/') if parsed.path else '',
        user=parsed.username or '',
        password=parsed.password or '',
        host=parsed.hostname or 'localhost',
        port=parsed.port or 5432
    )