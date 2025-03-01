import os.path
import logging

WEB_DIR = 'web'
HOST_URL = '127.0.0.1'
HOST_PORT = 8000
WEB_CACHE_PATH = os.path.join(WEB_DIR, 'cache')
LOGGING_FORMAT = '[%(name)s.%(funcName)s]: [%(levelname)s] %(message)s'
LOGGING_LEVEL = logging.DEBUG
TEST_CREATOR_DATA_PATH = 'test_creator.data'
SHARED_FOLDER_PATH = 'shared.data'
LANGUAGE_FILE_NAME = os.path.join(SHARED_FOLDER_PATH, 'language.json')
TEST_CREATOR_LOCK_FILENAME = os.path.join(SHARED_FOLDER_PATH, 'test_creator.lock')
SERVER_LOCK_FILENAME = os.path.join(SHARED_FOLDER_PATH, 'server.lock')
