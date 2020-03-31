import psycopg2
import pytest

from flasktodo.db import get_db


def test_get_db_then_close(app):
    # Start up the app and check for a database connection while it's running
    with app.app_context():
        db = get_db()
        assert db is get_db(), 'get_db should always return the same connection'

    # After app closes, database connection should close automatically so
    # running any queries with it should throw an error
    with pytest.raises(psycopg2.InterfaceError) as error:
        cur = db.cursor()
        cur.execute('SELECT 1')
        assert 'closed' in str(error)


# Run the following test twice to check both database CLI commands
@pytest.mark.parametrize(('function', 'command', 'output'), [
    ('flasktodo.db.init_db', 'init-db', 'Initialized the database.'),
    ('flasktodo.db.mock_db', 'mock-db', 'Inserted mock data.'),
])
def test_cli_commands(runner, monkeypatch, function, command, output):
    # Create class to safely track state of function calls
    class Recorder(object):
        called = False

    # Create a stub function to run instead of the original that toggles
    # the recorder state. We don't need to call the original since they're
    # running before every test anyways (see fixtures in conftest.py).
    def cli_stub():
        Recorder.called = True

    # Replace the original import with the stub
    monkeypatch.setattr(function, cli_stub)
    # Use the CLI runner to call the function
    result = runner.invoke(args=[command])
    # Check CLI output and verify the stub was called
    assert output in result.output
    assert Recorder.called


def add_item_test_db(client, app):
    assert client.get('/create-item')
    response = client.post(
        '/create-item', data={'description': 'test'}
    )
    assert client.get('/')
    

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM todos WHERE description = 'test'"
        ).fetchtone() is not None
    
    assert b'test' in response.data
    

#add item to the test database need to write the query for that 
#this adds the test to the database but i also need to check 
#that the variables are correct as well
