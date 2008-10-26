import types

__all__ = ['Enum']

class Enum:
    def __init__(self, name, enumList, unique_values=True):
        self.__doc__ = name
        lookup = { }
        reverseLookup = { }
        uniqueNames = [ ]
        self._uniqueValues = uniqueValues = [ ]
        self._uniqueId = 0

        for x in enumList:
            if type(x) == types.TupleType:
                x, i = x
                if type(x) != types.StringType:
                    raise ValueError("enum name is not a string: %s" % x)

                if type(i) != types.LongType and type(i) != types.IntType:
                    raise ValueError("enum value %s is not an number: %d" % (x, i))

                if x in uniqueNames:
                    raise ValueError("enum name is not unique: %s" % x)

                if unique_values and i in uniqueValues:
                    raise ValueError("enum value is not unique for %s" % x)

                uniqueNames.append(x)
                uniqueValues.append(i)
                lookup[x] = i
                reverseLookup[i] = x

        for x in enumList:
            if type(x) != types.TupleType:
                if type(x) != types.StringType:
                    raise ValueError("enum name is not a string: %s" % x)

                if x in uniqueNames:
                    raise ValueError("enum name is not unique: %s" % x)

                uniqueNames.append(x)
                i = self.__generateUniqueId()
                uniqueValues.append(i)
                lookup[x] = i
                reverseLookup[i] = x

        self.lookup = lookup
        self.reverseLookup = reverseLookup

    def __generateUniqueId(self):
        while self._uniqueId in self._uniqueValues:
            self._uniqueId += 1

        n = self._uniqueId
        self._uniqueId += 1

        return n

    def __getattr__(self, attr):
        if not self.lookup.has_key(attr):
            raise AttributeError

        return self.lookup[attr]

    def __str__(self):
        items = []
        for item, value in self.lookup.iteritems():
            items.append((value, item))

        items.sort()

        s = '%s: ' % self.__doc__
        for value, item in items:
            s += '%s=%d, ' % (item, value)

        return s[:-2]

