from sqlalchemy.ext.mutable import Mutable
"""
https://gist.github.com/eoghanmurray
"""
class MutableList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value
    def __getstate__(self):
        return list(self)
    def __setstate__(self, state):
        self.extend(state)
    def append(self, value):
        list.append(self, value)
        self.changed()
 
    def extend(self, iterable):
        list.extend(self, iterable)
        self.changed()
 
    def insert(self, index, item):
        list.insert(self, index, item)
        self.changed()
 
    def pop(self, index=None):
        if index:
            list.pop(self, index)
        else:
            list.pop(self)
        self.changed()
 
    def remove(self, item):
        list.remove(self, item)
        self.changed()
 
    def reverse(self):
        list.reverse(self)
        self.changed()
 
    def sort(self):
        list.sort(self)
        self.changed()
 
class MutableSet(Mutable, set):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableSet."
 
        if not isinstance(value, MutableSet):
            if isinstance(value, set):
                return MutableSet(value)
            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value
    def __reduce_ex__(self, proto):
        return (self.__class__, (list(self), ))
    def __getstate__(self):
        return set(self)
    def __setstate__(self, state):
        self.update(state)
    def update(self, *args):
        set.update(self, *args, **kwargs)
        self.changed()
    def intersection_update(self, *args):
        set.intersection_update(self, *args)
        self.changed()
    def difference_update(self, *args):
        set.difference_update(self, *args)
        self.changed()
    def symmetric_difference_update(self, *args):
        set.symmetric_difference_update(self, *args)
        self.changed()
    def add(self, elem):
        set.add(self, elem)
        self.changed()
    def remove(self, elem):
        set.remove(self, elem)
        self.changed()
    def discard(self, elem):
        set.discard(self, elem)
        self.changed()
    def pop(self):
        set.pop(self)
        self.changed()
    def clear(self):
        set.clear(self)
        self.changed()
