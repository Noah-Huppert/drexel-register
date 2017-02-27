import scrapy


class Course (scrapy.Item):
    academic_year = scrapy.Field()
    quarter = scrapy.Field()

    subject_code = scrapy.Field()
    course_number = scrapy.Field()
    course_title = scrapy.Field()

    credits = scrapy.Field()

    college = scrapy.Field()
    restrictions = scrapy.Field()
    co_requisites = scrapy.Field()
    pre_requisites = scrapy.Field()

class Section (scrapy.Item):
    crn = scrapy.Field()
    subject_code = scrapy.Field()
    course_number = scrapy.Field()
    instruction_type = scrapy.Field()
    instruction_method = scrapy.Field()
    section = scrapy.Field()

    max_enroll = scrapy.Field()
    enroll = scrapy.Field()

    days = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()

    instructor = scrapy.Field()
    credits = scrapy.Field()

    campus = scrapy.Field()
    building = scrapy.Field()
    room = scrapy.Field()

    comments = scrapy.Field()
    textbooks = scrapy.Field()

    start_date = scrapy.Field()
    end_date = scrapy.Field()
