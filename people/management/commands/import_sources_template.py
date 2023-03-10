# This file is a template for definitions of data sources recognised by the import command.
# Copy it to import_sources.py and implement the import logic for your sources using the explanations below.

def sample():
    """
    A sample data source that returns dummy data.
    """
    yield {
        "login": "login",
        "level": "",
        "full_name": "Full Name",
        "join_date": "2000-01-01",
    }


# The data sources are registered in this dictionary.  The import management command addresses them by the key that the
# administrator supplies as the parameter to the management command.
DATA_SOURCES = {
    "sample": sample,
}
