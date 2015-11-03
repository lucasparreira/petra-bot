from abc import ABCMeta, abstractmethod

__author__ = 'lucas'


class Caching(object):

    """
    Define a caching object contract.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def add(self, key, item):
        pass

    @abstractmethod
    def remove(self, key):
        pass

    @abstractmethod
    def exists(self, key):
        pass

    @abstractmethod
    def get(self, key, default=None):
        pass


class LocalMemCaching(Caching):

    """
    Simple caching mechanism using dictionary in local main memory.
    """

    def __init__(self):
        self.cache = {}

    def add(self, key, item):

        if key is None:
            raise Exception("Argument 'key' is invalid.")

        self.cache[key] = item

    def remove(self, key):
        if key is None:
            raise Exception("Argument 'key' is invalid.")

        return self.cache.pop(key)

    def exists(self, key):

        if key is None:
            raise Exception("Argument 'key' is invalid.")

        return key in self.cache

    def get(self, key, default=None):
        if key is None:
            raise Exception("Argument 'key' is invalid.")

        return self.cache.get(key, default)