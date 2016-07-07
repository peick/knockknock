import pytest


@pytest.fixture
def config_dir():
    return pytest.config.rootdir.join('tests').join('data')

