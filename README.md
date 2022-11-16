# Team

This is a web service that organises some aspects of the teamwork.

The service is built on Django framework.  It consists of a set of *more or less* independent applications that handle different aspects of the work.  See READMEs in these applications to find more details.

## Setting up

The project depends on Python version 3 (3.10.7 was used in development) and a few Python packages listed in requirements.txt.  The recommended way of configuring this is using the Python virtual environment:

    python3.10 -m venv "path/to/venv"
    source "path/to/venv/bin/activate"
    pip install -r requirements.txt

Then create `team/site_settings.py` with the instance-sprecific configuration, using `team/site_settings.py.template` as template and following the advice given in that file.

Finally, use the Django CLI tools to create the admin user, and set up your web and DB servers if necessary (not explained here).
