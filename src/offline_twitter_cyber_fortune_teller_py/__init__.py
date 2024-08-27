from pathlib import Path
from tomllib import load
from .data_type import XPath, TwitterAnalysisConfig

_base = Path(__file__).parent.parent.parent
data_folder = _base / "user_data"
config = TwitterAnalysisConfig(**load(open(_base / "config" / "config.toml", "rb")))
xpath = XPath(**load(open(_base / "config" / "xpath.toml", "rb")))
if not data_folder.exists():
    data_folder.mkdir()
print(xpath)
print(config)
