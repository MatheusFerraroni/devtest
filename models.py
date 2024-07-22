from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base
import enum


class Elevator(Base):
    __tablename__ = 'elevator'
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):
        return f'<Elevator {self.id}>'


class Floor(Base):
    __tablename__ = 'floor'
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):
        return f'<Floor {self.id}>'


class ElevatorDemand(Base):
    __tablename__ = "elevator_demand"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    timestamp = Column(DateTime, nullable=False)
    timestamp_attended = Column(DateTime)

    floor_id = mapped_column(Integer, ForeignKey('floor.id'), nullable=False)

    elevator_id = Column(Integer, ForeignKey('elevator.id'), nullable=False)
    elevator = relationship("Elevator", foreign_keys=[elevator_id])
    floor = relationship("Floor", foreign_keys=[floor_id])

    def complete(self, timestamp_attended):
        self.timestamp_attended = datetime.fromtimestamp(timestamp_attended)

    def __init__(self, floor_id=None, elevator_id=None, timestamp=None):
        self.floor_id = floor_id
        self.elevator_id = elevator_id
        self.timestamp = datetime.fromtimestamp(timestamp)

    def __repr__(self):
        return f'<ElevatorDemand {self.id}, '\
                f'timestamp {self.timestamp} '\
                f'timestamp_attended {self.timestamp_attended} '\
                f'floor_id {self.floor_id} '\
                f'elevator_id {self.elevator_id}>'


class MovementType(enum.Enum):
    autonomous = 'autonomous'
    called = 'called'
    resting = 'resting'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class ElevatorMovement(Base):
    __tablename__ = "elevator_movement"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    floor_start_id = Column(Integer, ForeignKey('floor.id'), nullable=False)
    floor_moving_to_id = Column(
        Integer,
        ForeignKey('floor.id'),
        nullable=False
    )
    elevator_id = Column(Integer, ForeignKey('elevator.id'), nullable=False)
    timestamp_start = Column(DateTime, nullable=False)
    timestamp_finish = Column(DateTime)
    movement_type = Column(Enum(MovementType), nullable=False)

    floor_start = relationship("Floor", foreign_keys=[floor_start_id])
    floor_moving_to = relationship("Floor", foreign_keys=[floor_moving_to_id])
    elevator = relationship("Elevator", foreign_keys=[elevator_id])

    def __init__(
        self,
        floor_start_id=None,
        floor_moving_to_id=None,
        elevator_id=None,
        timestamp_start=None,
        timestamp_finish=None,
        movement_type=None
    ):
        self.floor_start_id = floor_start_id
        self.floor_moving_to_id = floor_moving_to_id
        self.elevator_id = elevator_id
        self.timestamp_start = datetime.fromtimestamp(timestamp_start)
        self.timestamp_finish = datetime.fromtimestamp(timestamp_finish)

        if MovementType.has_value(movement_type):
            self.movement_type = movement_type
        else:
            raise Exception(f'Invalid movement type {movement_type}.')

    def __repr__(self):
        return f'<ElevatorMovement {self.id}, '\
               f'floor_start_id {self.floor_start_id}, '\
               f'floor_moving_to_id {self.floor_moving_to_id}, '\
               f'elevator_id {self.elevator_id}, '\
               f'timestamp_start {self.timestamp_start}, '\
               f'timestamp_finish {self.timestamp_finish}>'
