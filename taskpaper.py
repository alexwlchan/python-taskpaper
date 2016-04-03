import collections
import re
import shutil
import tempfile


TaskPaperTag = collections.namedtuple('TaskPaperTag', 'name value')

TAG_REGEX = re.compile(
    r'\B'                          # non-word boundary
    r'@'                           # literal @ character
    r'(?P<name>[a-z0-9\.\-_]+)'    # tag name
    r'(?:\((?P<value>[^)]*)\))?',  # tag value (optional)
    flags=re.IGNORECASE
)


class TaskPaperError(Exception):
    pass


class TaskPaperItem(object):

    # Number of spaces per indentation level
    tab_size = 4

    def __init__(self, text):
        # Strip trailing whitespace from the name.
        self._text = text.rstrip()

        self.tags = []
        self.body_text = self._text

        self._parse()

    def _parse(self):
        # Separate the list of tags from the body text
        m = TAG_REGEX.findall(self._text)
        if m is not None:
            self.tags.extend([TaskPaperTag(*t) for t in m])

        self.body_text = re.sub(TAG_REGEX, '', self._text).strip()

    def __repr__(self):
        return '%s(text=%r)' % (type(self).__name__, self._text)

    def __str__(self):
        components = [self.body_text]
        for tag in self.tags:
            if tag.value:
                components.append('@{tag.name}({tag.value})'.format(tag=tag))
            else:
                components.append('@{tag.name}'.format(tag=tag))
        return ' '.join(components)

    def add_tag(self, name, value=None):
        """
        Add a new tag with the given name and value.
        """
        self.tags.append(TaskPaperTag(name, value))

    def remove_tag(self, name, value=None):
        """
        Remove all tags with the given name and value.  If 'value' is None,
        every tag with this name is removed.
        """
        for tag in self.tags:
            if (tag.name == name) and (value is None or tag.value == value):
                self.tags.remove(tag)



class TaskPaperDocument(object):

    def __init__(self, path):
        self.path = path
        self.text = self._read()

    def __repr__(self):
        return '%s(path=%r)' % (type(self).__name__, self.path)

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
