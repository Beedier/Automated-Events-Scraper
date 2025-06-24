from dbcore.database import Database
from dbcore.config import get_config


# Load the .env file
env_config = get_config()

# Initialize database with the DB_URL from config
db = Database(env_config.get('DATABASE'))

# Expose useful things
Base = db.Base