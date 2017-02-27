import re, hashlib
import yaml


class Config:
    """Wrapper class around config.yaml file
    Fields:
        year: Year to schedule in
        quarter: Quarter to schedule in
        courses: Courses to schedule
    """

    """Creates new Config instance
    Raises:
        ValueError: If year, quarter, or courses contains bad data
    """
    def __init__(self, year, quarter, courses):
        # Make sure year and quarter values are strings
        if year is not None and type(year) is not str:
            year = str(year)

        if quarter is not None and type(quarter) is not str:
            quarter = str(quarter)

        # Verify configuration contains good data
        check_errs = []

        # -- -- config.year
        try:
            Config.check_year(year)
        except ValueError as e:
            check_errs.append(e)

        # -- -- config.quarter
        try:
            Config.check_quarter(quarter)
        except ValueError as e:
            check_errs.append(e)

        # -- -- config.courses
        try:
            Config.check_courses(courses)
        except ValueError as e:
            check_errs.append(e)

        # If check errors were encountered inform user and raise ValueError
        if len(check_errs) > 0:
            text = "The following errors where found with the provided configuration:"

            for err in check_errs:
                text += "\n    {}".format(err)

            # Raise own ValueError
            raise ValueError(text)

        # Now set years
        self.year = year
        self.quarter = quarter
        self.courses = courses

    """Initialize Config class from file
    Args:
        path (str): Path of config file to load from, defaults to config.yaml
    """
    def from_file(path="config.yaml"):
        config = {}
        with open(path, "r") as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as e:
                raise SyntaxError("Failed to parse config file, error: {}".format(e))

        return Config(config['year'], config['quarter'], config['courses'])

    # Static check methods, following documentation docs apply to the functions /check_(.*)/
    """Check a $1 field value
    Args:
        $1 ($1.type): $1.type to check

    Raises:
        ValueError: If $1 inputted is not valid
    """
    def check_year(year):
        pattern = re.compile(r"\b\d\d-\d\d\b")
        if year is None:  # Check exists
            raise ValueError("Year must be provided")
        elif pattern.match(year) is None:  # Check follows pattern
            raise ValueError("Year must be 2 digits separated by a dash followed by 2 more digits (Ex., dd-dd, 12-34, "
                             + "16-17).")
        else:
            return True

    def check_quarter(quarter):
        pattern = re.compile(r"\b(summer|fall|winter|spring)\b")
        if quarter is None:  # Check exists
            raise ValueError("Quarter must be provided")
        elif pattern.match(quarter) is None:  # Check follows pattern
            raise ValueError("Quarter must be one of: summer, fall, winter, or spring")
        else:
            return True

    def check_courses(courses):
        crn_pattern = re.compile(r"^!?\d{5}!?$")
        if courses is None:  # Check exists
            raise ValueError("Courses must be provided")
        elif type(courses) is not list:  # Check is list
            raise ValueError("Courses must be a list")
        else:  # Check syntax of each list item
            errors = {}

            course_i = 0
            for course in courses:
                try:
                    Config.check_course(course)
                except ValueError as e:
                    errors[course_i] = e
                finally:
                    course_i += 1

            # If check errors occur, raise own exception
            if len(errors) > 0:
                text = ""

                i = 0  # Used to only add line breaks after first run
                for course_i, error in errors.items():
                    if i > 0:
                        text += "\n"

                    text += "courses[{}] has errors:\n".format(course_i)
                    text += "    {}".format(error)

                    i += 1
                raise ValueError(text)
            else:  # Else return true
                return True

    def check_course(course):
        if type(course) is not dict:  # Check is dict
            raise ValueError("course must be a dict")

        errors = []

        # Has subject and course keys
        for key in ['subject', 'course']:
            if key not in course:  # Check course has key
                errors.append(ValueError("course must have {} key".format(key)))

        # Check optional 'type' key is list
        type_pattern = re.compile(r"\b(lab|lecture|recitation)\b")
        if 'types' in course and type(course['types']) is not list:
            errors.append(ValueError("course['types'] must be a list"))
        elif 'types' in course:  # Check each 'type' list item is valid
            item_i = 0
            for type_item in course['types']:
                if type_pattern.match(type_item) is None:  # Check 'type' item matches pattern
                    errors.append(
                        ValueError("course['types'][{}] must be one of: lab, lecture or recitation".format(item_i)))
                item_i += 1

        # Check optional 'crns' key is list
        crn_pattern = re.compile(r"^(\d{5}|!\d{5}!)$")  # ddddd or !ddddd!
        mandatory_crn_pattern = re.compile(r"^!\d{5}!$")
        if 'crns' in course and type(course['crns']) is not list:
            errors.append(ValueError("course['crns'] must be a list"))
        elif 'crns' in course:  # Check each 'crn' list item is valid
            # courses['crns'] => [{'lecture': [12345, 54321]}, {'lab': ['!12345!']}]
            # `typ in course['crns']` is each {'type': ['crn1', 'crn2']}
            # `crn_type, crns in typ.items()` is each crn_type=`type`, crns=`['crn1', 'crn2']`
            for typ in course['crns']:
                for crn_type, crns in typ.items():
                    # Check key (crn_type) of list object matches type pattern
                    if type_pattern.match(crn_type) is None:
                        errors.append(ValueError("course['crns'][{}] key must be one of: lab, lecture or recitation".format(crn_type)))

                    # Check crns in list
                    mandatory_crn_found = False  # Keep track if we find a mandatory CRN in this category
                    crn_i = 0
                    for crn in crns:
                        crn = str(crn)
                        if crn_pattern.match(crn) is None:
                            errors.append(ValueError("course['crns']['{}'][{}] crn must be 5 digits and optionally surrounded by exclamation marks".format(crn_type, crn_i)))
                        elif mandatory_crn_pattern.match(crn) is not None:
                            if mandatory_crn_found == True:  # This is not the only mandatory crn in list, raise error
                                errors.append(ValueError("course['crns']['{}'][{}] Only 1 CRN can be marked in a column at a time".format(crn_type, crn_i)))
                            else:
                                mandatory_crn_found = True

                        # Check if mandatory CRN is present that crn is only item in list
                        if mandatory_crn_found == True and crn_i != 0:
                            errors.append(ValueError("course['crns']['{}'][{}] When mandatory CRN is present it must be the only CRN in its section".format(crn_type, crn_i)))

                        crn_i += 1

        # If any errors occured
        if len(errors) > 0:
            text = ""

            i = 0
            for error in errors:
                # Only newline after first run
                if i > 0:
                    text += "\n"

                text += "    {}".format(error)

            raise ValueError(text)
        else:  # Else return True
            return True

    """Computes hash of configuration options
    Returns:
        str: SHA256 hash of config contents
    """
    def hash(self):
        return hashlib.sha256(str(self).encode('UTF-8')).hexdigest()

    def __str__(self):
        return "Config<year='{}', quarter='{}', courses='{}'>".format(self.year, self.quarter, self.courses)