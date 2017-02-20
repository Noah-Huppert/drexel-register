import sys, re, logging
import yaml
import urwid

# Config
# -- -- Get path
config_file_path = "config.yaml"

if len(sys.argv) >= 2:  # If custom path provided for courses file
    config_file_path = sys.argv[1]

# -- -- Read file
config = {}
with open(config_file_path, "r") as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as e:
        logging.error("Failed to parse \"{}\", error: {}".format(config_file_path, e))
        sys.exit(-1)

# -- -- Verify
# If set to false by any of the following checks the program exits, built this way so all errors are shown before exit
config_ok = True

# -- -- -- config.year
cnfg_yr_pattern = re.compile("\d\d-\d\d")
if 'year' not in config:  # Check exists
    logging.error("config.year must be included")
    config_ok = False
elif cnfg_yr_pattern.match(config['year']) is None:  # Matches dd-dd
    logging.error("config.year must be two digits, then a dash, then two more digits. Ex: 16-17")
    config_ok = False

# -- -- -- quarter
cnf_qtr_pattern = re.compile("summer|fall|winter|spring")
if 'quarter' not in config:  # Check exists
    logging.error("config.quarter must be included")
    config_ok = False
elif cnf_qtr_pattern.match(config['quarter']) is None:  # Check matches one of the quarter values
    logging.error("config.quarter must be one of the following: \"summer\", \"fall\", \"winter\", \"spring\"")
    config_ok = False

# -- -- -- courses
cnf_typ_pattern = re.compile("lab|lecture|recitation")
cnf_crn_pattern = re.compile("^!?\d{5}!?$")
if 'courses' not in config:  # Check exists
    logging.error("config.courses must be included")
    config_ok = False
elif type(config['courses']) is not list:  # Check courses is a list
    logging.error("config.courses must be a list")
    config_ok = False
else:  # Check courses list objects
    courseIndex = 0  # Course index
    for course in config['courses']:
        if type(course) is not dict:  # course is a dict
            logging.error("All items of config.courses must be key value objects")
            config_ok = False
            break

        # Course has 'subject' and 'course' keys
        mandatory_keys = ['subject', 'course']
        for key in mandatory_keys:
            if key not in course:
                logging.error("config.courses[{}] must include a {}".format(courseIndex, key))

        # Check 'types' key if present
        if 'types' in course:
            if type(course['types']) is not list:  # Check 'types' is list
                logging.error("config.courses[{}].types should be a list".format(courseIndex))
                config_ok = False
            else:  # Else check items are valid type
                typeIndex = 0
                for item in course['types']:
                    if cnf_typ_pattern.match(item) is None:  # Check type list item is one of recitation, lab, or lecture
                        logging.error("config.courses[{}].types[{}] should match one of: lab, lecture, recitation".format(courseIndex, typeIndex))
                        config_ok = False

                    typeIndex += 1

        # Check 'crns' key if present
        if 'crns' in course:
            if type(course['crns']) is not list:  # Check 'crns' is list
                logging.error("config.courses[{}].crns should be a list".format(courseIndex))
                config_ok = False
            else:  # Check keys match cnf_type_pattern, and values match cnf_crn_pattern
                crnIndex = 0
                for obj in course['crns']:
                    for key, values in obj.items():
                        if cnf_typ_pattern.match(key) is None:  # Check key matches cnf_type_pattern
                            logging.error("config.courses[{}].crns[{}] should be one of lab, lecture, or recitation".format(courseIndex, typeIndex))
                            config_ok = False

                        # Check each value matches cnf_crn_pattern
                        crnListItemIndex = 0
                        for value in values:
                            if cnf_crn_pattern.match(str(value)) is None:  # Check if specific item matches cnf_crn_pattern
                                logging.error("config.course[{}].crns[{}][{}] should be a valid crn".format(courseIndex, crnIndex, crnListItemIndex))
                                config_ok = False

                            crnListItemIndex += 1

                    crnIndex += 1

        courseIndex += 1

# Check that all checks passed
if config_ok == False:
    logging.error("Configuration is not ok, please fix errors above errors")
    sys.exit(-1)
else:
    logging.info("Configuration file \"{}\" is OK".format(config_file_path))

