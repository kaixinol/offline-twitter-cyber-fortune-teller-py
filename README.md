# offline-twitter-cyber-fortune-teller-py
```diff
Have you logged in to X (Twitter)? [y/n] (y): 
What's your username?(e.g. @jack or jack): jack
+ Based on the user's username, joining time, and low follower count, it appears to be the actual Twitter account of Jack Dorsey, the co-founder and former CEO of Twitter. The user activity suggests a strong interest in philanthropy and social impact, particularly focused on COVID-19 relief, girls' health and education, universal basic income (UBI), and transparency in donations. This individual also engages with a diverse range of tweets, including those related to technology, AI, and privacy. Additionally, retweeting content that supports free and open-source software and promotes philanthropic efforts further highlights Jack Dorsey's interests and values.
```
## Introduction
* As of February 9, 2023, Twitter [no longer supports free access to the Twitter API](https://x.com/XDevelopers/status/1621026986784337922), and continued use of the Twitter API incurs higher costs.
* This project circumvents the Twitter API by using the *playwright* framework as a web scraper.

## Requirements
- Python 3.11+
- Windows 10 or higher
- Linux
    - Debian 11+ and other Debian-based systems
    - Ubuntu 20.04+ ([LTS versions only](https://github.com/microsoft/playwright/issues/23296#issuecomment-1567983707))
    - Other Linux distributions are not supported because *playwright* [does not support installation of dependency libraries on other Linux distributions](https://github.com/microsoft/playwright/issues/23949)
- MacOS 10/11+ ARM/x86_64 *(not tested, no system available)*

## Configuration
- Set up a Python virtual environment
```bash
pdm install # or `poetry install` etc.
playwright install
playwright install-deps
```
- Configure `/config/config.toml`

## Startup
```commandline
pdm venv activate
source ...
cd src
python -m offline_twitter_cyber_fortune_teller_py
```