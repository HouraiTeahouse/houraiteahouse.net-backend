from houraiteahouse.config import ProductionConfig
from houraiteahouse.app import create_app

# This is the file to link to UWSGI

if __name__ == '__main__':
    create_app(ProductionConfig()).run()
