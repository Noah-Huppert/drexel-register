from sqlalchemy import declarative_base, Column, Integer, String, Float, Time, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from models.db.db import Base

"""
Model which represents course schedule requests made by user in config.yaml
"""
class SchedulePreference(Base):
    __tablename__ = 'schedule_preferences'

    id = Column(Integer, primary_key=True, nullable=False)
    schedule_run_id = Column(Integer, ForeignKey('schedule_runs.id'))
    schedule_run = relationship('ScheduleRun', back_populates='preferences')

    crn = Column(Integer)
    instruction_type = Column(String)
    preference = Column(Integer)
