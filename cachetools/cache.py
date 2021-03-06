import collections


class _DefaultSize(object):
    def __getitem__(self, _):
        return 1

    def __setitem__(self, _, value):
        assert value == 1

    def pop(self, _):
        return 1


class Cache(collections.MutableMapping):
    """Mutable mapping to serve as a simple cache or cache base class."""

    __size = _DefaultSize()

    def __init__(self, maxsize, missing=None, getsizeof=None):
        if missing:
            self.__missing = missing
        if getsizeof:
            self.__getsizeof = getsizeof
            self.__size = dict()
        self.__data = dict()
        self.__currsize = 0
        self.__maxsize = maxsize

    def __repr__(self):
        return '%s(%r, maxsize=%d, currsize=%d)' % (
            self.__class__.__name__,
            list(self.items()),
            self.__maxsize,
            self.__currsize,
        )

    def __getitem__(self, key):
        try:
            return self.__data[key]
        except KeyError:
            return self.__missing__(key)

    def __setitem__(self, key, value):
        maxsize = self.__maxsize
        size = self.getsizeof(value)
        if size > maxsize:
            raise ValueError('value too large')
        if key not in self.__data or self.__size[key] < size:
            while self.__currsize + size > maxsize:
                self.popitem()
        if key in self.__data:
            diffsize = size - self.__size[key]
        else:
            diffsize = size
        self.__data[key] = value
        self.__size[key] = size
        self.__currsize += diffsize

    def __delitem__(self, key):
        size = self.__size.pop(key)
        del self.__data[key]
        self.__currsize -= size

    def __contains__(self, key):
        return key in self.__data

    def __missing__(self, key):
        value = self.__missing(key)
        self.__setitem__(key, value)
        return value

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    @staticmethod
    def __getsizeof(value):
        return 1

    @staticmethod
    def __missing(key):
        raise KeyError(key)

    @property
    def maxsize(self):
        """The maximum size of the cache."""
        return self.__maxsize

    @property
    def currsize(self):
        """The current size of the cache."""
        return self.__currsize

    def getsizeof(self, value):
        """Return the size of a cache element's value."""
        return self.__getsizeof(value)

    # collections.MutableMapping mixin methods do not handle __missing__

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    __marker = object()

    def pop(self, key, default=__marker):
        if key in self:
            value = self[key]
            del self[key]
            return value
        elif default is self.__marker:
            raise KeyError(key)
        else:
            return default

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]
