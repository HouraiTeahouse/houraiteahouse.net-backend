from houraiteahouse.config import DevelopmentConfig
from houraiteahouse.app import create_app

# Use this for running locally at-will (eg, for debugging)

if __name__ == '__main__':
    create_app(DevelopmentConfig()).run(
        '0.0.0.0', 5000, debug=True, threaded=True)
