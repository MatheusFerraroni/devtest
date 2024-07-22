from models import (
    Elevator,
    Floor,
    ElevatorDemand,
    ElevatorMovement,
    MovementType
)
from unittest.mock import Mock
from unittest.mock import patch
import datetime
import math
import csv


@patch('main.get_session', autospec=True)
def test_add_floor(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session
    response = client.get('/add_floor')

    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'id' in json_data
    assert type(json_data['id']) is int

    query = test_session.query(Floor)
    model = query.filter(Floor.id == json_data['id']).first()
    assert type(model) is Floor
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_add_floor_error(mock_db_session, client, test_session):
    mock_session = Mock()
    mock_session.commit.side_effect = KeyError
    mock_db_session.return_value = mock_session

    response = client.get('/add_floor')

    assert response.status_code == 500

    json_data = response.get_json()
    assert json_data['status'] == 'error'
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_add_elevator(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session
    response = client.get('/add_elevator')

    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'id' in json_data
    assert type(json_data['id']) is int

    query = test_session.query(Elevator)
    model = query.filter(Elevator.id == json_data['id']).first()
    assert type(model) is Elevator
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_add_elevator_error(mock_db_session, client, test_session):
    mock_session = Mock()
    mock_session.commit.side_effect = KeyError
    mock_db_session.return_value = mock_session

    response = client.get('/add_elevator')

    assert response.status_code == 500

    json_data = response.get_json()
    assert json_data['status'] == 'error'
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_request_elevator(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session

    response = client.get('/add_elevator')
    elevator_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor_id = response.get_json()['id']

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/request_elevator/{floor_id}/'
                          f'{elevator_id}/{timestamp}')

    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'id' in json_data
    assert type(json_data['id']) is int

    query = test_session.query(ElevatorDemand)
    model = query.filter(ElevatorDemand.id == json_data['id']).first()
    assert type(model) is ElevatorDemand
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_request_elevator_incorrect(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session

    response = client.get('/add_elevator')
    elevator_id = response.get_json()['id']+1

    response = client.get('/add_floor')
    floor_id = response.get_json()['id']+1

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/request_elevator/{floor_id}/'
                          f'{elevator_id}/{timestamp}')

    assert response.status_code == 500

    json_data = response.get_json()
    assert json_data['status'] == 'error'
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_request_elevator_with_complete(
    mock_db_session,
    client,
    test_session
):
    mock_db_session.return_value = test_session

    response = client.get('/add_elevator')
    elevator_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor_id = response.get_json()['id']

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/request_elevator/{floor_id}/'
                          f'{elevator_id}/{timestamp}')

    assert response.status_code == 200

    json_data = response.get_json()
    id_demand = json_data['id']

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/request_elevator_complete/'
                          f'{id_demand}/{timestamp}')
    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'id' in json_data
    assert type(json_data['id']) is int
    assert json_data['id'] == id_demand

    query = test_session.query(ElevatorDemand)
    model = query.filter(ElevatorDemand.id == json_data['id']).first()
    assert type(model) is ElevatorDemand
    desired_timestamp = datetime.datetime.fromtimestamp(timestamp)
    assert model.timestamp_attended == desired_timestamp
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_request_elevator_with_complete_error(
    mock_db_session,
    client,
    test_session
):
    mock_db_session.return_value = test_session

    response = client.get('/add_elevator')
    elevator_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor_id = response.get_json()['id']

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/request_elevator/{floor_id}/'
                          f'{elevator_id}/{timestamp}')

    assert response.status_code == 200

    json_data = response.get_json()
    id_demand = json_data['id']

    mock_session = Mock()
    mock_session.commit.side_effect = KeyError
    mock_db_session.return_value = mock_session

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/request_elevator_complete/'
                          f'{id_demand}/{timestamp}')
    assert response.status_code == 500

    json_data = response.get_json()
    assert json_data['status'] == 'error'
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_create_elevator_movement(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session

    response = client.get('/add_elevator')
    elevator_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor1_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor2_id = response.get_json()['id']

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/add_elevator_movement/{floor1_id}/{floor2_id}/'
                          f'{elevator_id}/{timestamp}/{timestamp}/called')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'id' in json_data
    assert type(json_data['id']) is int
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_create_invalid_elevator_movement(
    mock_db_session,
    client,
    test_session
):
    mock_db_session.return_value = test_session

    response = client.get('/add_elevator')
    elevator_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor1_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor2_id = response.get_json()['id']

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/add_elevator_movement/{floor1_id}/{floor2_id}/'
                          f'{elevator_id}/{timestamp}/{timestamp}/fake')

    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    test_session.rollback()


@patch('main.get_session', autospec=True)
def test_export_demand(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session

    test_session.query(ElevatorDemand).delete()
    test_session.query(ElevatorMovement).delete()
    test_session.query(Floor).delete()
    test_session.query(Elevator).delete()

    response = client.get('/add_elevator')
    elevator_id = response.get_json()['id']

    response = client.get('/add_floor')
    floor_id = response.get_json()['id']

    timestamp = int(datetime.datetime.now().timestamp())
    response = client.get(f'/request_elevator/{floor_id}/'
                          f'{elevator_id}/{timestamp}')
    demand_id = response.get_json()['id']

    csv_demand = client.get('/get_data/demand?page=1&per_page=1')

    assert csv_demand.status_code == 200

    content = csv_demand.data.decode('utf-8')
    csv_reader = csv.reader(content.splitlines())
    headers = next(csv_reader)
    assert headers == [
        'id',
        'created_at',
        'updated_at',
        'timestamp',
        'timestamp_attended',
        'floor_id',
        'elevator_id'
    ]

    row = next(csv_reader)
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    check = [row[0], row[3], row[4], row[5], row[6]]
    check_against = list(map(str, [
                                    demand_id,
                                    timestamp,
                                    '',
                                    floor_id,
                                    elevator_id
                                  ]))
    assert check == check_against


@patch('main.get_session', autospec=True)
def test_export_multiple_demands(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session

    test_session.query(ElevatorDemand).delete()
    test_session.query(ElevatorMovement).delete()
    test_session.query(Floor).delete()
    test_session.query(Elevator).delete()

    amt = 128
    per_page = 5

    elevator_ids = []
    for _ in range(amt):
        response = client.get('/add_elevator')
        elevator_id = response.get_json()['id']
        elevator_ids.append(elevator_id)

    floor_ids = []
    for _ in range(amt):
        response = client.get('/add_floor')
        floor_id = response.get_json()['id']
        floor_ids.append(floor_id)

    timestamps = []
    for i in range(amt):
        timestamp = int(datetime.datetime.now().timestamp()-i)
        timestamps.append(timestamp)

    demand_ids = []
    for i in range(amt):
        elevator_id = elevator_ids[i]
        floor_id = floor_ids[i]
        timestamp = timestamps[i]
        response = client.get(f'/request_elevator/{floor_id}/'
                              f'{elevator_id}/{timestamp}')
        demand_id = response.get_json()['id']
        demand_ids.append(demand_id)

    for page in range(1, math.ceil(amt/per_page)):
        csv_demand = client.get(f'/get_data/demand?page={page}'
                                f'&per_page={per_page}')

        assert csv_demand.status_code == 200

        content = csv_demand.data.decode('utf-8')
        csv_reader = csv.reader(content.splitlines())
        headers = next(csv_reader)
        assert headers == ['id', 'created_at', 'updated_at', 'timestamp',
                           'timestamp_attended', 'floor_id', 'elevator_id']

        from_api = []
        while True:
            try:
                row = next(csv_reader)
                check = [row[0], row[3], row[4], row[5], row[6]]
                from_api.append(check)
            except StopIteration:
                break

        expected = []
        start = (page - 1) * per_page
        for i in range(start, start+per_page):
            timestamp = str(datetime.datetime.fromtimestamp(timestamps[i]))
            check = [
                demand_ids[i],
                timestamp,
                '',
                floor_ids[i],
                elevator_ids[i]
            ]
            check = list(map(str, check))
            expected.append(check)

        assert from_api == expected


@patch('main.get_session', autospec=True)
def test_export_multiple_moviments(mock_db_session, client, test_session):
    mock_db_session.return_value = test_session

    test_session.query(ElevatorDemand).delete()
    test_session.query(ElevatorMovement).delete()
    test_session.query(Floor).delete()
    test_session.query(Elevator).delete()

    amt = 11
    per_page = 5
    per_elevator = 10

    movements = [
        MovementType.autonomous.value,
        MovementType.called.value,
        MovementType.resting.value
    ]

    timestamp = int(datetime.datetime.now().timestamp())

    expected = {}
    elevators_id = []
    for i in range(amt):

        response = client.get('/add_elevator')
        elevator_id = response.get_json()['id']
        elevators_id.append(elevator_id)

        for j in range(per_elevator):
            response = client.get('/add_floor')
            floor1_id = response.get_json()['id']

            response = client.get('/add_floor')
            floor2_id = response.get_json()['id']

            start = timestamp+10
            end = timestamp+10
            timestamp += 20

            movement = movements[(i + j) % len(movements)]

            response = client.get(f'/add_elevator_movement/'
                                  f'{floor1_id}/{floor2_id}/'
                                  f'{elevator_id}/{start}/{end}/{movement}')
            movement_id = response.get_json()['id']

            check = [
                movement_id,
                floor1_id,
                floor2_id,
                elevator_id,
                datetime.datetime.fromtimestamp(start),
                datetime.datetime.fromtimestamp(end),
                movement
            ]
            check = list(map(str, check))
            try:
                expected[elevator_id].append(check)
            except Exception as _:
                expected[elevator_id] = []
                expected[elevator_id].append(check)

    for elevator_id in elevators_id:
        for page in range(1, math.ceil(amt/per_page)):
            csv_demand = client.get(f'/get_data/movement/{elevator_id}?'
                                    f'page={page}&per_page={per_page}')

            assert csv_demand.status_code == 200

            content = csv_demand.data.decode('utf-8')
            csv_reader = csv.reader(content.splitlines())
            headers = next(csv_reader)
            assert headers == ['id', 'created_at', 'updated_at',
                               'floor_start_id', 'floor_moving_to_id',
                               'elevator_id', 'timestamp_start',
                               'timestamp_finish', 'movement_type']

            from_api = []
            while True:
                try:
                    row = next(csv_reader)
                    check = [
                        row[0],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8]
                    ]
                    from_api.append(check)
                except StopIteration:
                    break

            start = (page - 1) * per_page
            assert from_api == expected[elevator_id][start: start+per_page]
