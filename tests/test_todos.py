import pytest

import psycopg2

from flasktodo.db import get_db

def test_todo_list(client):
    # View the home page and check to see the header and a to-do item
    response = client.get('/')
    assert b'<h1>A simple to-do application</h1>' in response.data
    assert b'clean room' in response.data

    # Mock data should show three to-do items, one of which is complete
    assert response.data.count(b'<li class="">') == 2
    assert response.data.count(b'<li class="completed">') == 1


def test_add_item(client, app):
    response = client.get('/create-item')
    assert b'<h1>Create a to-do item</h1>' in response.data
    assert b'Enter an item' in response.data


    response = client.post(
        '/create-item', data={'description': 'feedthemax'}
    )

    with app.app_context():
        cur = get_db().cursor()
        cur.execute(
            "SELECT * FROM todos WHERE description = 'feedthemax'"
        )
        assert cur.fetchone() is not None

    response = client.get('/')
    assert b'feedthemax' in response.data


