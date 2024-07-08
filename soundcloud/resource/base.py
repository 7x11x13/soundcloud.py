import datetime
from dataclasses import dataclass

import dateutil.parser
from dacite import Config, from_dict


@dataclass
class BaseData:
    dacite_config = Config(
        type_hooks={datetime.datetime: dateutil.parser.isoparse}, cast=[tuple]
    )

    @classmethod
    def from_dict(cls, d: dict):
        return from_dict(cls, d, cls.dacite_config)
