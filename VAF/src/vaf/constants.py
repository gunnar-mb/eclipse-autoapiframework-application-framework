"""Constants relevant for all VAF modules"""

from enum import Enum


class TruthyEnum(Enum):
    """Enum that allows the usage in if/while by checking against the first entry"""

    def __bool__(self) -> bool:
        first_element = list(self.__class__)[0]
        return self != first_element


VAF_CFG_FILE = ".vafconfig.json"
