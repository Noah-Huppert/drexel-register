from sqlalchemy import declarative_base, Column, Integer, String, Float, Time, Date, DateTime
from sqlalchemy.orm import relationship

from drexel_register.items import ScraperCourse
from drexel_register.models.db.db import Base
from drexel_register.models.db.helpers import Helpers

"""
Drexel Course
"""
class Course(Helpers, Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, nullable=False)
    sections = relationship('Section', back_populates='course')

    academic_year = Column(String)
    quarter = Column(String)

    subject_code = Column(String)
    course_number = Column(String)
    course_title = Column(String)

    credits = Column(Float)

    college = Column(String)
    restrictions = Column(String)
    co_requisites = Column(String)
    pre_requisites = Column(String)

    """Create instance of Course from Scrapy Course item

    If a key on the provided item is None it is ignored

    Args:
        item (str[]): Item to create Course from

    Returns:
        Course: Course created from item

    Raises:
        ValueError: If item param is not a Scraper Course Item
    """
    def from_item(item):
        if item is ScraperCourse:
            course = Course()
            course._set_if_present(item, ['academic_year',
                                    'quarter',

                                    'subject_code',
                                    'course_number',
                                    'course_title',

                                    'credits',

                                    'college',
                                    'restrictions',
                                    'co_requisites',
                                    'pre_requisites'])

            return course
        else:
            raise ValueError("Item must be a Scraper Course item")
