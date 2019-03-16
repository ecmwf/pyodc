

class Odb:

    def __init__(self, f):
        """Open an ODB from a file path or a file-like object"""
        if isinstance(f, str):
            self.__owned = True
            self.__f = open(f, 'rb')
        else:
            self.__owned = False
            self.__f = f

    def __del__(self):
        if self.__owned:
            self.__f.close()