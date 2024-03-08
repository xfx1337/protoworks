from configparser import *

from singleton import singleton

@singleton
class Config(ConfigParser):
    def __init__(self, config_file,):
        super().__init__()

        self.read(config_file, encoding="utf8")
        self.validate()


    def validate(self):
        required_values = {
            "path": {
                "projects_path": None
            }
        }

        for section, keys in required_values.items():
                if section not in self:
                    raise InvalidConfig(
                        '[Configuration] Missing section %s in the config file' % section)

                for key, values in keys.items():
                    if key not in self[section] or self[section][key] == '':
                        raise InvalidConfig((
                            '[Configuration] Missing value for %s under section %s in ' +
                            'the config file') % (key, section))

                    if values:
                        if self[section][key] not in values:
                            raise InvalidConfig((
                                '[Configuration] Invalid value for %s under section %s in ' +
                                'the config file') % (key, section))