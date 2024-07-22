import pytest
from models import (Elevator, Floor, ElevatorDemand, ElevatorMovement,
                    MovementType)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from sqlalchemy import inspect
import datetime


def test_engine_creation(test_engine, test_session):
    assert test_engine is not None
    assert test_session is not None


def test_init_db(test_session):
    query_text = "SELECT name FROM sqlite_master WHERE type='table';"
    result = test_session.execute(text(query_text))
    tables = result.fetchall()
    tables = set([t[0] for t in tables])

    assert tables == {'elevator', 'elevator_movement', 'floor',
                      'elevator_demand'}


def test_table_structure(test_engine):
    inspector = inspect(test_engine)
    tables_structure = {
        'elevator': {'id', 'created_at', 'updated_at'},
        'floor': {'id', 'created_at', 'updated_at'},
        'elevator_demand': {'id', 'created_at', 'updated_at', 'timestamp',
                            'timestamp_attended', 'floor_id', 'elevator_id'},
        'elevator_movement': {'id', 'created_at', 'updated_at',
                              'movement_type', 'floor_start_id',
                              'floor_moving_to_id', 'elevator_id',
                              'timestamp_start', 'timestamp_finish'}

    }
    for table_name in tables_structure.keys():
        columns = set(col['name'] for col in inspector.get_columns(table_name))
        assert columns == tables_structure[table_name]


def test_create_elevator(test_session):
    elevator = Elevator()
    test_session.add(elevator)
    test_session.commit()

    assert elevator.id is not None
    assert elevator.created_at is not None
    assert elevator.updated_at is not None


def test_create_floor(test_session):
    floor = Floor()
    test_session.add(floor)
    test_session.commit()

    assert floor.id is not None
    assert floor.created_at is not None
    assert floor.updated_at is not None


def test_create_elevator_demand(test_session):
    floor = Floor()
    test_session.add(floor)
    test_session.commit()

    elevator = Elevator()
    test_session.add(elevator)
    test_session.commit()

    timestamp = datetime.datetime.now().timestamp()
    elevator_demand = ElevatorDemand(
        floor_id=floor.id,
        elevator_id=elevator.id,
        timestamp=timestamp
    )
    test_session.add(elevator_demand)
    test_session.commit()

    assert elevator_demand.id is not None
    assert elevator_demand.timestamp is not None
    assert elevator_demand.timestamp_attended is None
    assert elevator_demand.floor_id == floor.id
    assert elevator_demand.elevator_id == elevator.id


def test_create_elevator_invalid_demand(test_session):
    floor = Floor()
    test_session.add(floor)
    test_session.commit()

    elevator = Elevator()
    test_session.add(elevator)
    test_session.commit()

    timestamp = datetime.datetime.now().timestamp()
    elevator_demand = ElevatorDemand(
        floor_id=floor.id+1,
        elevator_id=elevator.id+1,
        timestamp=timestamp
    )
    test_session.add(elevator_demand)

    with pytest.raises(IntegrityError) as _:
        test_session.commit()
    test_session.rollback()


def test_complete_elevator_demand(test_session):
    floor = Floor()
    test_session.add(floor)
    test_session.commit()

    elevator = Elevator()
    test_session.add(elevator)
    test_session.commit()

    timestamp = datetime.datetime.now().timestamp()
    elevator_demand = ElevatorDemand(
        floor_id=floor.id,
        elevator_id=elevator.id,
        timestamp=timestamp
    )
    test_session.add(elevator_demand)
    test_session.commit()

    assert elevator_demand.id is not None
    assert elevator_demand.timestamp is not None
    assert elevator_demand.timestamp_attended is None
    assert elevator_demand.floor_id == floor.id
    assert elevator_demand.elevator_id == elevator.id

    timestamp_attended = datetime.datetime.now().timestamp()
    query = test_session.query(ElevatorDemand)
    model = query.filter(ElevatorDemand.id == elevator_demand.id).first()
    model.complete(timestamp_attended)
    test_session.commit()

    query = test_session.query(ElevatorDemand)
    model = query.filter(ElevatorDemand.id == elevator_demand.id).first()
    assert (model.timestamp_attended ==
            datetime.datetime.fromtimestamp(timestamp_attended))


def test_create_elevator_movement(test_session):
    floor1 = Floor()
    test_session.add(floor1)
    test_session.commit()

    floor2 = Floor()
    test_session.add(floor2)
    test_session.commit()

    elevator = Elevator()
    test_session.add(elevator)
    test_session.commit()

    timestamp_start = datetime.datetime.now().timestamp()-10
    timestamp_end = datetime.datetime.now().timestamp()
    elevator_movement = ElevatorMovement(
        floor_start_id=floor1.id,
        floor_moving_to_id=floor2.id,
        elevator_id=elevator.id,
        timestamp_start=timestamp_start,
        timestamp_finish=timestamp_end,
        movement_type=MovementType.autonomous.value
    )
    test_session.add(elevator_movement)
    test_session.commit()

    assert elevator_movement.id is not None
    assert (elevator_movement.timestamp_start ==
            datetime.datetime.fromtimestamp(timestamp_start))
    assert (elevator_movement.timestamp_finish ==
            datetime.datetime.fromtimestamp(timestamp_end))
    assert elevator_movement.floor_start_id == floor1.id
    assert elevator_movement.floor_moving_to_id == floor2.id
    assert elevator_movement.elevator_id == elevator.id


def test_create_invalid_elevator_movement(test_session):
    floor1 = Floor()
    test_session.add(floor1)
    test_session.commit()

    floor2 = Floor()
    test_session.add(floor2)
    test_session.commit()

    elevator = Elevator()
    test_session.add(elevator)
    test_session.commit()

    timestamp_start = datetime.datetime.now().timestamp()-10
    timestamp_end = datetime.datetime.now().timestamp()
    movement = ElevatorMovement(
        floor_start_id=floor1.id+1,
        floor_moving_to_id=floor2.id+1,
        elevator_id=elevator.id+1,
        timestamp_start=timestamp_start,
        timestamp_finish=timestamp_end,
        movement_type=MovementType.autonomous.value
    )
    test_session.add(movement)

    with pytest.raises(IntegrityError) as _:
        test_session.commit()
    test_session.rollback()


def test_repr_models(test_session):
    floor = Floor()
    test_session.add(floor)

    elevator = Elevator()
    test_session.add(elevator)

    test_session.commit()

    timestamp = int(datetime.datetime.now().timestamp())
    movement = ElevatorMovement(
        floor_start_id=floor.id,
        floor_moving_to_id=floor.id,
        elevator_id=elevator.id,
        timestamp_start=timestamp,
        timestamp_finish=timestamp,
        movement_type=MovementType.autonomous.value
    )
    test_session.add(movement)

    demand = ElevatorDemand(
        floor_id=floor.id,
        elevator_id=elevator.id,
        timestamp=timestamp
    )
    test_session.add(demand)

    test_session.commit()

    timestamp = datetime.datetime.fromtimestamp(timestamp)

    assert str(floor) == f'<Floor {floor.id}>'
    assert str(elevator) == f'<Elevator {elevator.id}>'
    assert str(movement) == f'<ElevatorMovement 2, '\
                            f'floor_start_id {floor.id}, '\
                            f'floor_moving_to_id {floor.id}, elevator_id '\
                            f'{elevator.id}, timestamp_start {timestamp}, '\
                            f'timestamp_finish {timestamp}>'
    assert str(demand) == f'<ElevatorDemand 2, timestamp {timestamp} '\
                          f'timestamp_attended None floor_id {floor.id} '\
                          f'elevator_id {elevator.id}>'


def test_invalid_movement_type():
    with pytest.raises(Exception) as _:
        ElevatorMovement(
            floor_start_id=1,
            floor_moving_to_id=1,
            elevator_id=1,
            timestamp_start=1,
            timestamp_finish=1,
            movement_type='fake_movement_type'
        )
