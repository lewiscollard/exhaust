import os


def get_test_file_path(filename):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'data', filename),
    )
