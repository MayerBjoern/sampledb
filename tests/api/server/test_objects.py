# coding: utf-8
"""

"""

import requests
import pytest
import json

import sampledb
import sampledb.logic
import sampledb.models


from tests.test_utils import flask_server, app, app_context


@pytest.fixture
def auth_user(flask_server):
    with flask_server.app.app_context():
        user = sampledb.models.User(name="Basic User", email="example@fz-juelich.de", type=sampledb.models.UserType.PERSON)
        sampledb.logic.authentication.insert_user_and_authentication_method_to_db(
            user,
            login='username',
            password='password',
            user_type=sampledb.logic.authentication.AuthenticationType.OTHER
        )
        assert user.id is not None
    return ('username', 'password'), user


@pytest.fixture
def other_user(flask_server):
    with flask_server.app.app_context():
        user = sampledb.models.User(name="Other User", email="other@fz-juelich.de", type=sampledb.models.UserType.PERSON)
        sampledb.db.session.add(user)
        sampledb.db.session.commit()
        assert user.id is not None
    return  user


@pytest.fixture
def auth(auth_user):
    return auth_user[0]


@pytest.fixture
def user(auth_user):
    return auth_user[1]


@pytest.fixture
def action():
    action = sampledb.logic.actions.create_action(
        action_type=sampledb.logic.actions.ActionType.SAMPLE_CREATION,
        name="",
        description="",
        schema={
            'title': 'Example Object',
            'type': 'object',
            'properties': {
                'name': {
                    'title': 'Object Name',
                    'type': 'text'
                }
            },
            'required': ['name']
        }
    )
    return action


def test_get_object_version(flask_server, auth, user, action):
    r = requests.get(flask_server.base_url + 'api/v1/objects/1/versions/0', auth=auth)
    assert r.status_code == 404
    data = {
        'name': {
            '_type': 'text',
            'text': 'Example'
        }
    }
    object = sampledb.logic.objects.create_object(action_id=action.id, data=data, user_id=user.id)
    r = requests.get(flask_server.base_url + 'api/v1/objects/{}/versions/{}'.format(object.object_id, object.version_id), auth=auth)
    assert r.status_code == 200
    assert json.loads(r.content.decode('utf-8')) == {
        "object_id": object.object_id,
        "version_id": object.version_id,
        "action_id": object.action_id,
        "schema": object.schema,
        "data": object.data
    }
    r = requests.get(flask_server.base_url + 'api/v1/objects/1/versions/1', auth=auth)
    assert r.status_code == 404


def test_get_object(flask_server, auth, user, action):
    r = requests.get(flask_server.base_url + 'api/v1/objects/1', auth=auth)
    assert r.status_code == 404
    data = {
        'name': {
            '_type': 'text',
            'text': 'Example'
        }
    }
    object = sampledb.logic.objects.create_object(action_id=action.id, data=data, user_id=user.id)
    r = requests.get(flask_server.base_url + 'api/v1/objects/{}'.format(object.object_id), auth=auth, allow_redirects=False)
    assert r.status_code == 302
    assert r.headers['Location'] == flask_server.base_url + 'api/v1/objects/{}/versions/{}'.format(object.object_id, object.version_id)


def test_post_object_version(flask_server, auth, user, action):
    r = requests.get(flask_server.base_url + 'api/v1/objects/1', auth=auth)
    assert r.status_code == 404
    data = {
        'name': {
            '_type': 'text',
            'text': 'Example'
        }
    }
    object = sampledb.logic.objects.create_object(action_id=action.id, data=data, user_id=user.id)

    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'].startswith('Failed to decode JSON object')

    object_json=[]
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'JSON body required'

    object_json = {'unknown': 1}
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'invalid key \'unknown\''

    object_json = {
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 201
    assert r.headers['Location'] == flask_server.base_url + 'api/v1/objects/{}/versions/{}'.format(object.object_id, object.version_id + 1)
    new_object = sampledb.logic.objects.get_object(object_id=object.object_id)
    assert new_object.version_id == object.version_id + 1
    assert new_object.data == object_json['data']
    object = new_object

    object_json = {}
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'data must be set'

    object_json = {
        'object_id': object.object_id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 201
    assert r.headers['Location'] == flask_server.base_url + 'api/v1/objects/{}/versions/{}'.format(object.object_id, object.version_id + 1)
    new_object = sampledb.logic.objects.get_object(object_id=object.object_id)
    assert new_object.version_id == object.version_id + 1
    assert new_object.data == object_json['data']
    object = new_object

    object_json = {
        'object_id': object.object_id + 1,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'object_id must be {}'.format(object.object_id)

    object_json = {
        'version_id': object.version_id + 1,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 201
    assert r.headers['Location'] == flask_server.base_url + 'api/v1/objects/{}/versions/{}'.format(object.object_id, object.version_id + 1)
    new_object = sampledb.logic.objects.get_object(object_id=object.object_id)
    assert new_object.version_id == object.version_id + 1
    assert new_object.data == object_json['data']
    object = new_object

    object_json = {
        'version_id': object.version_id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'version_id must be {}'.format(object.version_id+1)

    object_json = {
        'action_id': object.action_id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 201
    assert r.headers['Location'] == flask_server.base_url + 'api/v1/objects/{}/versions/{}'.format(object.object_id, object.version_id + 1)
    new_object = sampledb.logic.objects.get_object(object_id=object.object_id)
    assert new_object.version_id == object.version_id + 1
    assert new_object.data == object_json['data']
    object = new_object

    object_json = {
        'action_id': object.action_id + 1,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'action_id must be {}'.format(object.action_id)

    new_schema = {
        'title': 'Example Object',
        'type': 'object',
        'properties': {
            'name': {
                'title': 'Object Name',
                'type': 'text'
            },
            'info': {
                'title': 'Object Info',
                'type': 'text'
            }
        },
        'required': ['name']
    }
    object_json = {
        'schema': new_schema,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            },
            'info': {
                '_type': 'text',
                'text': 'Example Info'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'].startswith('schema must be either')

    sampledb.logic.actions.update_action(
        action_id=action.id,
        name=action.name,
        description=action.description,
        schema=new_schema
    )
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 201
    new_object = sampledb.logic.objects.get_object(object_id=object.object_id)
    assert new_object.version_id == object.version_id + 1
    assert new_object.schema == object_json['schema']
    assert new_object.data == object_json['data']
    object = new_object

    object_json = {
        'schema': new_schema,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example Object'
            },
            'info': {
                '_type': 'text',
                'text': 'Example Info 2'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 201
    new_object = sampledb.logic.objects.get_object(object_id=object.object_id)
    assert new_object.version_id == object.version_id + 1
    assert new_object.schema == object_json['schema']
    assert new_object.data == object_json['data']
    object = new_object

    object_json = {
        'data': {
            'name': {
                '_type': 'boolean',
                'value': True
            },
            'info': {
                '_type': 'text',
                'text': 'Example Info 2'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/{}/versions/'.format(object.object_id), json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == """validation failed:
 - unexpected keys in schema: {'value'} (at name)"""


def test_get_objects(flask_server, auth, user, other_user, action):
    r = requests.get(flask_server.base_url + 'api/v1/objects/1', auth=auth)
    assert r.status_code == 404
    data = {
        'name': {
            '_type': 'text',
            'text': 'Example'
        }
    }
    object = sampledb.logic.objects.create_object(action_id=action.id, data=data, user_id=other_user.id)
    r = requests.get(flask_server.base_url + 'api/v1/objects/', auth=auth, allow_redirects=False)
    assert r.status_code == 200
    assert r.json() == []
    sampledb.logic.permissions.set_user_object_permissions(
        object_id=object.object_id,
        user_id=user.id,
        permissions=sampledb.logic.permissions.Permissions.READ
    )
    r = requests.get(flask_server.base_url + 'api/v1/objects/', auth=auth, allow_redirects=False)
    assert r.status_code == 200
    assert r.json() == [
        {
            "object_id": object.object_id,
            "version_id": object.version_id,
            "action_id": object.action_id,
            "schema": object.schema,
            "data": object.data
        }
    ]


def test_create_object(flask_server, auth, user, action):
    object_json = {
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 201
    objects = sampledb.logic.objects.get_objects()
    assert len(objects) == 1
    object = objects[0]
    assert r.headers['Location'] == flask_server.base_url + 'api/v1/objects/{}/versions/{}'.format(object.object_id, object.version_id)
    assert object.version_id == 0
    assert object.action_id == action.id
    assert object.schema == action.schema
    assert object.data == object_json['data']

    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'].startswith('Failed to decode JSON object')

    r = requests.post(flask_server.base_url + 'api/v1/objects/', json=[], auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'JSON body required'

    object_json = {
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        },
        'user_id': user.id
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'invalid key \'user_id\''

    object_json = {
        'object_id': 1,
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', json=object_json, auth=auth, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'object_id cannot be set'

    object_json = {
        'version_id': 0,
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 201

    object_json = {
        'version_id': 1,
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'version_id must be 0'

    object_json = {
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'action_id must be set'

    object_json = {
        'action_id': "Create other Sample",
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'action_id must be an integer'

    object_json = {
        'action_id': action.id + 1,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'action {} does not exist'.format(action.id + 1)

    object_json = {
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        },
        'schema': action.schema
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 201

    object_json = {
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'text',
                'text': 'Example'
            }
        },
        'schema': {
            'name': {
                'type': 'text',
                'default': 'Sample'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'schema must be:\n{}'.format(json.dumps(action.schema, indent=4))

    object_json = {
        'action_id': action.id
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == 'data must be set'

    object_json = {
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'boolean',
                'value': True
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == """validation failed:
 - unexpected keys in schema: {'value'} (at name)"""
    object_json = {
        'action_id': action.id,
        'data': {
            'name': {
                '_type': 'boolean',
                'value': True
            },
            'test': {
                '_type': 'text',
                'value': 'Test'
            }
        }
    }
    r = requests.post(flask_server.base_url + 'api/v1/objects/', auth=auth, json=object_json, allow_redirects=False)
    assert r.status_code == 400
    assert r.json()['message'] == """validation failed:
 - unexpected keys in schema: {'value'} (at name)
 - unknown property "test" (at test)"""
