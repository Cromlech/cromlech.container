# -*- coding: utf-8 -*-

from zope.interface import implements
from cromlech.container.contained import Contained, setitem, uncontained
from cromlech.container.interfaces import IContainer


class Lazy(object):
    """Lazy Attributes.
    """

    def __init__(self, func, name=None):
        if name is None:
            name = func.__name__
        self.data = (func, name)

    def __get__(self, inst, cls):
        if inst is None:
            return self

        func, name = self.data
        value = func(inst)
        inst.__dict__[name] = value

        return value


class Container(Contained):
    """Non-persistent container.
    """
    implements(IContainer)

    def __init__(self):
        self._data = self._create_container()

    def _create_container(self):
        """Construct an item-data container

        Subclasses should override this if they want different data.

        The value returned is a mapping object that also has `get`,
        `has_key`, `keys`, `items`, and `values` methods.
        """
        return {}

    def keys(self):
        """See interface `IReadContainer`.
        """
        return self._data.keys()

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        """See interface `IReadContainer`.
        """
        return self._data[key]

    def get(self, key, default=None):
        """See interface `IReadContainer`.
        """
        return self._data.get(key, default)

    def values(self):
        """See interface `IReadContainer`.
        """
        return self._data.values()

    def __len__(self):
        """See interface `IReadContainer`.
        """
        return len(self._data)

    def items(self):
        """See interface `IReadContainer`.
        """
        return self._data.items()

    def __contains__(self, key):
        """See interface `IReadContainer`.
        """
        return key in self._data

    has_key = __contains__

    def __setitem__(self, key, object):
        """See interface `IWriteContainer`.
        """
        setitem(self, self._data.__setitem__, key, object)

    def __delitem__(self, key):
        """See interface `IWriteContainer`.
        """
        uncontained(self._data[key], self, key)
        del self._data[key]
