# Development
## Getting Started

    git clone git@github.com:regCore/regCore.git && cd regCore
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -r requirements-dev.txt
    cp regcore/settings-dev.py regcore/settings.py
    pre-commit install

    ./manage.py runserver
