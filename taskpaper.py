import shutil
import tempfile


class TaskPaperError(Exception):
    pass


class TaskPaperDocument(object):

    def __init__(self, path):
        self.path = path
        self.text = self._read()

    def _read(self):
        try:
            with open(self.path) as infile:
                return infile.read()
        except IOError as e:
            raise TaskPaperError("Unable to read document %s: %s" % (path, e))

    def write(self):
        """
        Write out the list of tasks.  Writes are atomic.
        """
        _, tmp_path = tempfile.mkstemp(prefix='taskpaper')
        with open(tmp_path, 'w') as outfile:
            outfile.write(self.text)

        shutil.move(tmp_path, self.path)
