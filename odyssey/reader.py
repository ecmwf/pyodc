from .frame import Frame

from functools import reduce
import io


class Reader:

    def __init__(self, source, aggregated=False):
        self.__aggregated = aggregated
        self._frames = []

        if isinstance(source, io.IOBase):
            self._f = source
        else:
            self._f = open(source, 'rb')

        if self.__aggregated:
            raise NotImplementedError("Aggregated reader not yet implemented in python")

        while True:
            try:
                self._frames.append(Frame(self._f))
                self._frames[-1].seekToEnd()
            except EOFError:
                # n.b. f.read() does not throw EOFError, so this will only catch the exception
                # thrown internally when the table marker is not found
                break

    @property
    def frames(self):
        return self._frames


def decode_dataframes(source, columns=None):
    r = Reader(source)
    for f in r.frames:
        yield f.dataframe()


def decode_dataframe(source, columns=None):
    return reduce(lambda df1, df2: df1.append(df2), decode_dataframes(source, columns))
