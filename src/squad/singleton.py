"""A singlton class, that camn be inherited by classes that want to offer this
interface. used by our 'Environmwent' class.
"""


class Singleton:
    """Use to create a singleton"""

    def __new__(cls, *args, **kwds):
        # type: (*str, **str) -> Singleton
        """
        >>> s = Singleton()
        >>> p = Singleton()
        >>> id(s) == id(p)
        True
        """
        it_id = "__it__"
        # getattr will dip into base classes, so __dict__ must be used
        instance: Singleton = cls.__dict__.get(it_id, None)
        if instance is not None:
            return instance
        instance = object.__new__(cls)
        setattr(cls, it_id, instance)
        instance.init(*args, **kwds)
        return instance

    def init(self, *args, **kwds):
        # type: (*str, **str) -> None
        """Initialisation - sub-classes should implememnt this."""
