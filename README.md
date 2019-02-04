# Git Issues

This helps download and analyse github issues

## Install 

1. [Install virtualenvwrapper ](https://virtualenvwrapper.readthedocs.io/en/latest/install.html#basic-installation)
1. Create virtualenv `mkvirtualenv --python=python3 gitsu`
1. Activate virtualenv `workon gitsu`
1. Install packages `pip install -r requirements.py`
1. Add local directory to path `add2virtualenv <project_dir>`


## Architecture

1. postgresql -- database backend
1. gitsu-etl -- etl processes to get data in place
1. gitsu-analytics -- analysis processes including notebooks
1. gitsu-web -- frontend visualization

