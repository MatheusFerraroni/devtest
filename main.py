from models import (
    Elevator,
    Floor,
    ElevatorDemand,
    ElevatorMovement
)
from flask import Flask, request, send_file
from database import db_session
from database import init_db
from io import BytesIO, StringIO
import csv


app = Flask(__name__)


def get_session():
    return db_session


@app.route('/get_data/movement/<int:elevator_id>', methods=['GET'])
def get_data_movement(elevator_id):
    session = get_session()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10000, type=int)
    offset = (page - 1) * per_page

    query = session.query(ElevatorMovement)
    query = query.filter(ElevatorMovement.elevator_id == elevator_id)
    query = query.order_by('created_at')
    query = query.offset(offset).limit(per_page)
    movements = query.all()

    csvfile = StringIO()
    csv_writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['id', 'created_at', 'updated_at', 'floor_start_id',
                         'floor_moving_to_id', 'elevator_id',
                         'timestamp_start', 'timestamp_finish',
                         'movement_type'
                         ])

    for movement in movements:
        csv_writer.writerow([
            movement.id,
            movement.created_at,
            movement.updated_at,
            movement.floor_start_id,
            movement.floor_moving_to_id,
            movement.elevator_id,
            movement.timestamp_start,
            movement.timestamp_finish,
            movement.movement_type.value
        ])

    csvfile.seek(0)

    bytes_io = BytesIO(csvfile.getvalue().encode('utf-8'))

    return send_file(
        bytes_io,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'elevator_movement_page_{page}.csv'
    )


@app.route('/get_data/demand', methods=['GET'])
def get_data_demand():
    session = get_session()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10000, type=int)
    offset = (page - 1) * per_page

    query = session.query(ElevatorDemand).offset(offset).limit(per_page)
    demands = query.all()

    csvfile = StringIO()
    csv_writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['id', 'created_at', 'updated_at', 'timestamp',
                         'timestamp_attended', 'floor_id', 'elevator_id'])

    for demand in demands:
        csv_writer.writerow([demand.id, demand.created_at, demand.updated_at,
                             demand.timestamp, demand.timestamp_attended,
                             demand.floor_id, demand.elevator_id])

    csvfile.seek(0)

    bytes_io = BytesIO(csvfile.getvalue().encode('utf-8'))

    return send_file(
        bytes_io,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'elevator_demand_page_{page}.csv'
    )


@app.route('/add_floor')
def add_floor():
    session = get_session()
    try:
        model = Floor()
        session.add(model)
        session.commit()
        return {'status': 'success', 'id': model.id}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/add_elevator')
def add_elevator():
    session = get_session()
    try:
        model = Elevator()
        session.add(model)
        session.commit()
        return {'status': 'success', 'id': model.id}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/request_elevator/<int:floor_id>/<int:elevator_id>/<int:start>')
def request_elevator(floor_id, elevator_id, start):
    session = get_session()
    try:
        model = ElevatorDemand(floor_id, elevator_id, start)
        session.add(model)
        session.commit()
        return {'status': 'success', 'id': model.id}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route(
    '/request_elevator_complete/<int:request_id>/<int:timestamp_attended>'
)
def request_elevator_complete(request_id, timestamp_attended):
    session = get_session()
    try:
        query = session.query(ElevatorDemand)
        model = query.filter(ElevatorDemand.id == request_id).first()
        model.complete(timestamp_attended)
        session.commit()
        return {'status': 'success', 'id': model.id}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route(
    '/add_elevator_movement/<int:floor_start_id>/<int:floor_moving_to_id>/'
    '<int:elevator_id>/<int:timestamp_start>/<int:timestamp_finish>/'
    '<string:movement_type>'
)
def add_elevator_movement(
    floor_start_id,
    floor_moving_to_id,
    elevator_id,
    timestamp_start,
    timestamp_finish,
    movement_type
):
    try:
        session = get_session()
        model = ElevatorMovement(
            floor_start_id,
            floor_moving_to_id,
            elevator_id,
            timestamp_start,
            timestamp_finish,
            movement_type
        )
        session.add(model)
        session.commit()
        return {'status': 'success', 'id': model.id}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.teardown_appcontext
def shutdown_session(exception=None):
    session = get_session()
    session.remove()


def main():
    app.run(debug=True, port=81)


if __name__ == '__main__':
    init_db()
    main()
