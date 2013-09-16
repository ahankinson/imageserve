

class ISMIAttribute(object):
    """ Used to convert a dict (or a JSON representation)
        into an object. This makes it easier to use in
        Django templates.
    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)