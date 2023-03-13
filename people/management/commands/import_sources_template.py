# This file is a template for definitions of data sources recognised by the import command.
# Copy it to import_sources.py and implement the import logic for your sources using the explanations below.

def sample():
    """
    A sample data source.

    This function wraps a single data source--e. g., a database or just a data file--for importing `Person` objects.

    The caller expects this function to return an iterable where each item is a dictionary with four fields: "login",
    "level", "full_name", and "join_date", all of them are string values for the corresponding fields of the `Person`
    model.  The level must contain name of an existing `Level` instance, and the date must be in YYYY-MM-DD format.

    The caller does not purge data before importing.  This function may implement optimisations, such as storing the
    state at one call and skipping certain records at the next call if they were not changed.

    To be recognised by the import command, this function must be registered in the `DATA_SOURCES` map in the end of
    this file.  There may be multiple data sources.
    """
    for i in range(1, 5):
        yield {
            "login": "login {}".format(i),
            "level": "",
            "full_name": "Full Name {}".format(i),
            "join_date": "2000-01-01",
        }


# The data sources are registered in this dictionary.  The import management command addresses them by the key that the
# administrator supplies as the parameter to the management command.
DATA_SOURCES = {
    "sample": sample,
}
