import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to convert Decimal objects to floats.

    Attributes
    ----------
    Inherit all attributes from json.JSONEncoder.
    """
    
    def default(self, o):
        """
        Convert Decimal objects to string values for JSON serialization.
        
        Parameters
        ----------
        o : object
            The object to be serialized.

        Returns
        -------
        object
            The serialized object with Decimal objects converted to floats.
        """
        
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)