from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    """ConfigParser wrapper"""

    # folder: str

    def __init__(self, config):

        # object.__setattr__(self, name, value)