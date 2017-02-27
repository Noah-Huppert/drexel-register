from sqlalchemy import declarative_base, Column, Integer, String, Float, Time, Date, DateTime
from sqlalchemy.orm import relationship

from models.db.db import Base

"""
Represents a scheduling run through
"""
class ScheduleRun(Base):
    __tablename__ = 'schedule_runs'

    id = Column(Integer, primary_key=True, nullable=False)
    preferences = relationship('SchedulePreference', back_populates='schedule_run')

    # Configuration file hash
    config_hash = Column(String, nullable=False)

