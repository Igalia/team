# Utility functions for handling forms.

def make_readonly(form):
    """Sets the disabled attribute for all fields in the form.
    """
    for field_name in form.fields:
        field = getattr(form, 'fields')[field_name]
        field.disabled = True
