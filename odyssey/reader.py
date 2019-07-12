from .frame import Frame, MismatchedFramesError

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

        while True:
            try:
                self._frames.append(Frame(self._f))
                self._frames[-1].seekToEnd()
            except EOFError:
                # n.b. f.read() does not throw EOFError, so this will only catch the exception
                # thrown internally when the table marker is not found
                break

        if self.__aggregated:
            if len(self._frames) > 1:
                aggregated_frames = [self._frames[0]]
                for frame in self._frames[1:]:
                    try:
                        aggregated_frames[-1]._append(frame)
                    except MismatchedFramesError:
                        aggregated_frames.append(frame)
                self._frames = aggregated_frames


    @property
    def frames(self):
        return self._frames


def decode_dataframes(source, columns=None):
    r = Reader(source)
    for f in r.frames:
        yield f.dataframe()


def decode_dataframe(source, columns=None):
    return reduce(lambda df1, df2: df1.append(df2), decode_dataframes(source, columns))
