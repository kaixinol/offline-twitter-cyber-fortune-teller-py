import math
import os
from pathlib import Path
from tomllib import load
from .data_type import XPath, TwitterAnalysisConfig

_base = Path(__file__).parent.parent.parent
data_folder = _base / "user_data"
config = TwitterAnalysisConfig(**load(open(_base / "config" / "config.toml", "rb")))
xpath = XPath(**load(open(_base / "config" / "xpath.toml", "rb")))
if isinstance(config.thread, float) and not math.isnan(config.thread):
    raise ValueError("thread value only allows NaN or integer values")
if math.isnan(config.thread):
    config.thread = os.cpu_count()
if not data_folder.exists():
    data_folder.mkdir()
print(xpath)
print(config)
