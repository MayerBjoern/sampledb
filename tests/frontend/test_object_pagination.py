# coding: utf-8
"""

"""

import requests
import pytest
import typing
from bs4 import BeautifulSoup

import sampledb
from sampledb import db
import sampledb.logic
import sampledb.models
from sampledb.models import User, Action


@pytest.fixture
def user() -> User:
    user = sampledb.models.User(
        name="User",
        email="example@example.com",
        type=sampledb.models.UserType.PERSON)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def action() -> Action:
    action = sampledb.logic.actions.create_action(
        action_type_id=sampledb.models.ActionType.SAMPLE_CREATION,
        schema={
            'title': 'Example Object',
            'type': 'object',
            'properties': {
                'name': {
                    'title': 'Name',
                    'type': 'text'
                }
            },
            'required': ['name']
        }
    )
    sampledb.logic.action_translations.set_action_translation(
        language_id=sampledb.logic.languages.Language.ENGLISH,
        action_id=action.id,
        name='Example Action',
        description=''
    )
    return action


def test_get_objects_limit(flask_server: typing.Any, user: User, action: Action):
    object_ids = []
    for i in range(10):
        object = sampledb.logic.objects.create_object(action_id=action.id, data={
            'name': {
                '_type': 'text',
                'text': str(i)
            }
        }, user_id=user.id)
        object_ids.append(object.object_id)
    session = requests.session()
    assert session.get(flask_server.base_url + 'users/{}/autologin'.format(user.id)).status_code == 200

    r = session.get(flask_server.base_url + 'objects')
    assert r.status_code == 200
    document = BeautifulSoup(r.content, 'html.parser')
    rows = document.find(id='table-objects').find('tbody').find_all('tr')
    assert len(rows) == 10
    for i, row in enumerate(rows):
        assert row.find('th').text == str(object_ids[9-i])

    r = session.get(flask_server.base_url + 'objects?limit=4')
    assert r.status_code == 200
    document = BeautifulSoup(r.content, 'html.parser')
    rows = document.find(id='table-objects').find('tbody').find_all('tr')
    assert len(rows) == 4
    for i, row in enumerate(rows):
        assert row.find('th').text == str(object_ids[9-i])

    r = session.get(flask_server.base_url + 'objects?limit=40')
    assert r.status_code == 200
    document = BeautifulSoup(r.content, 'html.parser')
    rows = document.find(id='table-objects').find('tbody').find_all('tr')
    assert len(rows) == 10
    for i, row in enumerate(rows):
        assert row.find('th').text == str(object_ids[9-i])


def test_get_objects_offset(flask_server: typing.Any, user: User, action: Action):
    object_ids = []
    for i in range(10):
        object = sampledb.logic.objects.create_object(action_id=action.id, data={
            'name': {
                '_type': 'text',
                'text': str(i)
            }
        }, user_id=user.id)
        object_ids.append(object.object_id)
    session = requests.session()
    assert session.get(flask_server.base_url + 'users/{}/autologin'.format(user.id)).status_code == 200

    r = session.get(flask_server.base_url + 'objects?offset=5')
    assert r.status_code == 200
    document = BeautifulSoup(r.content, 'html.parser')
    rows = document.find(id='table-objects').find('tbody').find_all('tr')
    assert len(rows) == 10-5
    for i, row in enumerate(rows, start=5):
        assert row.find('th').text == str(object_ids[9-i])

    r = session.get(flask_server.base_url + 'objects?offset=5&limit=3')
    assert r.status_code == 200
    document = BeautifulSoup(r.content, 'html.parser')
    rows = document.find(id='table-objects').find('tbody').find_all('tr')
    assert len(rows) == 3
    for i, row in enumerate(rows, start=5):
        assert row.find('th').text == str(object_ids[9-i])
