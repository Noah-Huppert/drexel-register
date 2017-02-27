from enum import Enum
import yaml
from pathlib import Path
from helpers.enum_helpers import EnumHelpers

class ProgressStage(EnumHelpers, Enum):
    """Represents stage scheduling process is in
    Fields:
        Scraping: Scraping info about `config.courses`
        ConfigPreferences: Parse and save course preferences from config file
        SectionPreferences: Get user inputted preferences for each section
        BaseSchedule: Creating base schedule
        PrimarySchedule: Creating primary schedule
        BackupSchedule: Creating backup schedules
        Done: Proccess complete, discard file and make a new one
    """

    Scraping = 1

    ConfigPreferences = 2
    SectionPreferences = 3

    BaseSchedule = 4
    PrimarySchedule = 5
    BackupSchedule = 6

    Done = 7

class ProgressStageCompletion(EnumHelpers, Enum):
    """Represents progress in a ProgressStage
    Fields:
        JustSwitched: Value set when writing to file to update `Progress.stage`
        Running: Doing the logic
        Done: Logic is done, switch to next stage
    """
    JustSwitched = 1
    Running = 2
    Done = 3

class Progress():
    """Wrapper class around progress.yaml file
        Fields:
            _path (str): Path of progress file (default progress.yaml)

        Properties:
            config_hash (str): SHA256 hash of configuration values
            stage (ProgressStage): Stage of schedule run
            completion (ProgressStageCompletion): Progress in stage

    """

    """Creates a Progress instance from a dict in the same format as the one returned by self.to_dict
    Args:
        d (dict): Dict with the properly formatted keys: 'config_hash', 'stage', and 'completion'

    Raises:
        ValueError: If 'config_hash', 'stage', or 'completion' is not present in d argument
    """
    def from_dict(d, path="config.yaml"):
        # Check keys
        for key in ['config_hash', 'stage', 'completion']:
            if key not in d:
                raise ValueError("{} must not be none in d, d={}".format(key, d))

            value = None
            if key == 'config_hash':
                d[key] = d[key]
            elif key == 'stage':
                d[key] = ProgressStage.from_str(d[key])
            elif key == 'completion':
                d[key] = ProgressStageCompletion.from_str(d[key])

            value = d[key]
            typ = type(value)

            if (key == 'config_hash') and (type(value) is not str):
                raise ValueError("{} must be a str, type was: {}".format(key, typ))
            elif (key == 'stage') and (type(value) is not ProgressStage):
                raise ValueError("{} must be ProgressStage, type was: {}".format(key, typ))
            elif (key == 'completion') and (type(value) is not ProgressStageCompletion):
                raise ValueError("{} must be ProgressStageCompletion, type was: {}".format(key, typ))

        return Progress(d['config_hash'], d['stage'], d['completion'], path)

    """Creates Config with default starting values
    Only value which is not default is the config_hash.
    Other default values are:
        stage: Scraping
        progress: JustSwitched

    Args:
        config_hash (str): Hash of config values
        path (str): Path of progress file, defaults to progress.yaml

    Raises:
        ValueError: If config_hash is None or len(config_hash) <= 0
    """
    def with_defaults(config_hash, path="config.yaml"):
        if (config_hash is None) or (len(config_hash) <= 0):
            raise ValueError("config_hash cannot be None and len(config_hash) cannot be <= 0, was: {}".format(config_hash))
        else:
            return Progress(config_hash, ProgressStage.Scraping, ProgressStageCompletion.JustSwitched, path)

    """Creates Progress instance from given path or when appropriate from defaults
    Uses defaults if:
        - stage=done
        - stage=back scheduling && progress=done

    Raises:
        ValueError: If config_hash is None, isn't a str, or len(config_hash) <= 0
    """
    def from_path_or_defaults(config_hash, path="config.yaml"):
        if (config_hash is None) or (type(config_hash) is not str) or (len(config_hash) <= 0):
            raise ValueError("config_hash can not be None, must be a str, and len(config_hash) can not be <= 0, was: {}".format(config_hash))

        # Load progress if progress file already exists at path
        path_obj = Path(path)
        if path_obj.is_file():
            file_dict = Progress.load_properties_to_dict(path)
            progress = Progress.from_dict(file_dict, path)

            # Check if progress file is in done state
            if (progress.stage == ProgressStage.Done) or (progress.stage == ProgressStage.BackupSchedule and progress.completion == ProgressStageCompletion.Done):
                # If it is disregard any previous values, return defaults
                return Progress.with_defaults(config_hash, path)
            else:  # Else return progress stored in file
                return progress
        else:  # If doesn't exist load defaults
            return Progress.with_defaults(config_hash, path)

    """Creates new Progress
    Args:
        path (str): Path of progress file, default progress.yaml

    Raises:
            ValueError: If config_hash (also if len(config_hash) <= 0), stage, or completion are not defined
    """
    def __init__(self, config_hash, stage, completion, path="progress.yaml"):
        # TODO: load properties if file already exists
        if (path is None) or (type(path) is not str) or (len(path) <= 0):
            raise ValueError("path cannot be None, must be a str, and len(path) cannot <= 0, was: {}".format(path))

        self.path = path

        if (config_hash is not None) or (len(config_hash) <= 0):
            self._config_hash = config_hash
        else:
            raise ValueError("config_hash can not be None and len(config_hash) cannot be <= 0, was: {}".format(config_hash))

        if (stage is not None) or (type(stage) is not ProgressStage):
            self._stage = stage
        else:
            raise ValueError("stage can not be None")

        if (completion is not None) or (type(completion) is not ProgressStageCompletion):
            self._completion = completion
        else:
            raise ValueError("completion can not be None")

        self.write_properties()

    """Returns a dict representation of the progress
    """
    def to_dict(self):
        return {
            'config_hash': self.config_hash,
            'stage': str(self.stage),
            'completion': str(self.completion)
        }

    """Writes properties to file
    """
    def write_properties(self):
        with open(self.path, 'w') as outfile:
            yaml.dump(self.to_dict(), outfile)

    """Loads properties from file specified by path
    Tries to load properties from file, expects all values to exists

    Raises:
        ValueError: If progress file specified by self.path doesn't contain 'config_hash', 'stage' or 'completion' key
        SyntaxError: If yaml fails to parse progress file specified by path
    """
    def load_properties_to_dict(path="config.yaml"):
        with open(path, "r") as stream:
            try:
                data = yaml.load(stream)

                if 'config_hash' not in data:
                    raise ValueError("Progress file specified by path must have 'config_hash' value, path={}".format(path))

                if 'stage' not in data:
                    raise ValueError("Progress file specified by path must have 'stage' value, path={}".format(path))

                if 'completion' not in data:
                    raise ValueError("Progress file specified by path must have 'completion' value, path={}".format(path))

                # Load directly to values since we are loading to the file (so we don't want setters witting to a file)

                return {
                    'config_hash': data['config_hash'],
                    'stage': data['stage'],
                    'completion': data['completion']
                }
            except yaml.YAMLError as e:
                raise SyntaxError("Failed to parse progress file, path={}, error: {}".format(self.path, e))



    @property
    def config_hash(self):
        return self._config_hash

    """Sets config_hash
    Raises:
        ValueError: If value is none, not a str, or if len(value) <= 0
    """
    @config_hash.setter
    def config_hash(self, value):
        # Check good value
        if (value is None) or (value is not str) or (len(value) <= 0):
            # If not raise
            raise ValueError("config_hash can not be set to None, must be a str, and len(value) cannot <= 0, was: {}".format(value))
        else:
            self._config_hash = value
            self.write_properties()

    @property
    def stage(self):
        return self._stage

    """Sets stage
    Also sets completion to JustSwitched if value != self._stage
    Raises:
        ValueError: If value is None or not a ProgressStage
    """
    @stage.setter
    def stage(self, value):
        if (value is None) or (value is not ProgressStage):
            raise ValueError("stage must not be None and must be a ProgressStage, was: {}".format(value))
        elif value != self.stage:
            self._stage = value
            self._completion = ProgressStageCompletion.JustSwitched  # Set completion to JustSwitched

            self.write_properties()

    @property
    def completion(self):
        return self._completion

    """Sets completion
    Raises:
        ValueError: If value is None or not a ProgressStageCompletion
    """
    @completion.setter
    def completion(self, value):
        if (value is None) or (value is not ProgressStageCompletion):
            raise ValueError("completion must not be None and must be a ProgressStageCompletion, was: {}".format(value))
        else:
            self._completion = value
            self.write_properties()

    def __str__(self):
        return str(self.to_dict())