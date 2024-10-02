# offline-twitter-cyber-fortune-teller-py
```diff
Have you logged in to X (Twitter)? [y/n] (y): 
What's your username?(e.g. @jack or jack): jack
+ Based on the user's username, joining time, and low follower count, it appears to be the actual Twitter account of Jack Dorsey, the co-founder and former CEO of Twitter. The user activity suggests a strong interest in philanthropy and social impact, particularly focused on COVID-19 relief, girls' health and education, universal basic income (UBI), and transparency in donations. This individual also engages with a diverse range of tweets, including those related to technology, AI, and privacy. Additionally, retweeting content that supports free and open-source software and promotes philanthropic efforts further highlights Jack Dorsey's interests and values.
```
## 简介
* 从2023年2月9日起，Twitter[不再支持免费访问Twitter API](https://x.com/XDevelopers/status/1621026986784337922)，继续使用Twitter API支付较高的费用。
* 此项目绕过Twitter API 使用 *playwright* 框架作为爬虫。
## 要求
- Python 3.11+
- Windows 10或者更高版本
- Linux
    - Debian 11+ 等其他Debian系系统
    - Ubuntu 20.04+([仅支持LTS版本](https://github.com/microsoft/playwright/issues/23296#issuecomment-1567983707))
    - 不支持其他Linux是因为*playwright*[不支持其他Linux上依赖库的安装](https://github.com/microsoft/playwright/issues/23949)
- MacOS 10/11+ ARM/x86_64 *(没有系统，未经过测试)*
## 配置
- 自行配置Python虚拟环境
```bash
pdm install # or `poetry install` etc.
playwright install
playwright install-deps
```
- 配置`/config/config.toml`
## 启动
```commandline
pdm venv activate
source ...
cd src
python -m offline_twitter_cyber_fortune_teller_py
```
