from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask app using factory pattern
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'

    # Print registered routes for debugging
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule}")

    app.run(
        host='0.0.0.0',  # Make the server publicly available
        port=port,
        debug=debug
    )
