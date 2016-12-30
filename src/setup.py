import os
from shutil import copy

# Enviroment setup script to create the necessary files and directories

manage_file_dir = os.path.abspath(os.path.dirname(__file__))
basedir = '/var/htwebsite'
config = 'config.json'
example_config = 'example_config.json'
news_dir = 'news'

lang_dirs = ['en', 'ja']


def create_or_update(dir_path):
    if not os.path.exists(dir_path):
        print('Creating {0} as it currently doesn\'t exist'.format(dir_path))
        os.makedirs(dir_path)

create_or_update(basedir)
for lang in lang_dirs:
    create_or_update(os.path.join(basedir, news_dir, lang))
config_path = os.path.join(basedir, config)
if not os.path.exists(config_path):
    copy(os.path.join(manage_file_dir, example_config),
         config_path)
    print(('No config.json was present, please edit {0} to suit your'
           ' needs.').format(config_path))
print('Setup complete!')
