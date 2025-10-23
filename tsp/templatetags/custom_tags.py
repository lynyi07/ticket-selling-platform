from django.template.defaulttags import register
import decimal

@register.filter
def get_item(dictionary, key):
    """
    Get the value associated with the given key in a dictionary.
    
    Parameters
    ----------
    dictionary : dict
        The dictionary to retrieve the value from.
    key : int
        The key to retrieve the value for.

    Returns
    -------
    Any
        The value associated with the given key, or None if the key is not found.
    """
    
    return dictionary.get(key)
