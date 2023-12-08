# Team

This is a web service that organises some aspects of the teamwork.

The service is built on Django framework.  It consists of a set of *more or less* independent applications that handle different aspects of the work.  See READMEs in these applications to find more details.

The core application is [People](people).  It maintains the database of actual members of the team, and it handles the root URL.

## Setting up

The project depends on Python version 3 (3.10.7 was used in development) and a few Python packages listed in requirements.txt.  The recommended way of configuring this is using the Python virtual environment:

    python3.10 -m venv "path/to/venv"
    source "path/to/venv/bin/activate"
    pip install -r requirements.txt

Then create `team/site_settings.py` with the instance-specific configuration, using `team/site_settings.py.template` as template and following the advice given in that file.

Finally, use the Django CLI tools to create the admin user, and set up your web and DB servers if necessary (not explained here).

## Using Docker

To run the application with Docker, you can run `docker compose up -d` from the root of the project.  Use `STATIC_ROOT = os.path.join(BASE_DIR, 'static')` in the settings instead of `STATICFILE_DIRS`.
