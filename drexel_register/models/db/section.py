from sqlalchemy import declarative_base, Column, Integer, String, Float, Time, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from drexel_register.drexel_register.items import ScraperSection
from drexel_register.models.db.db import Base
from drexel_register.models.db.helpers import Helpers

"""
Course section
"""
class Section(Helpers, Base):
    __tablename__ = 'sections'

    id = Column(Integer)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship('Course', back_populates='sections')

    crn = Column(Integer)
    subject_code = Column(String)
    course_number = Column(String)
    instruction_type = Column(String)
    instruction_method = Column(String)
    section = Column(String)

    max_enroll = Column(Integer)
    enroll = Column(Integer)

    days = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)

    instructor = Column(String)
    credits = Column(Integer)

    campus = Column(String)
    building = Column(String)
    room = Column(String)

    comments = Column(String)
    textbooks = Column(String)

    start_date = Column(Date)
    end_date = Column(Date)

     """Create instance of Section from Scrapy Section item

    If a key on the provided item is None it is ignored

    Args:
        item (str[]): Item to create Section from

    Returns:
        Section: Section created from item

    Raises:
        ValueError: If item param is not a Scraper Section Item
    """
    def from_item(item):
        if item is ScraperSection:
            section = Section()
            section._set_if_present(item, ['crn',
                                    'subject_code',
                                    'course_number',
                                    'instruction_type',
                                    'instruction_method',
                                    'section',

                                    'max_enroll',
                                    'enroll',

                                    'days',
                                    'start_time',
                                    'end_time',

                                    'instructor',
                                    'credits',

                                    'campus',
                                    'building',
                                    'room',

                                    'comments',
                                    'textbooks',

                                    'start_date',
                                    'end_date'])

            return section
        else:
            raise ValueError("Item must be a Scraper Section")