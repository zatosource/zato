import pytest
from zato.common.test.pubsub_database import pubsub_db_env, PubSubDBMode, start_pubsub_database, stop_pubsub_database

@pytest.fixture(scope='module')
def pubsub_database():
    database = start_pubsub_database('tmpcheck', PubSubDBMode.PostgreSQL)
    try:
        yield database
    finally:
        stop_pubsub_database(database)

def test_push_multi(pubsub_database):
    from push_multi import run_push_multi_scenario
    with pubsub_db_env(pubsub_database.env):
        run_push_multi_scenario()
