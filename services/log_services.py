import os
from models.log_models import LogResult
from flask import current_app
from pathlib import Path


class LogService():
    """
    Responsible for all log access. Uses generator functions wherever possible
    so that loading a large file will result in streamed results rather than
    having to load the entire results in memory.
    """

    def __init__(self):
        self.hostname = current_app.config["HOST_NAME"]
        self.rootdir = current_app.config["ROOT_DIR"]

        if not self.rootdir.endswith("/"):
            self.rootdir += "/"

    def get_logs(self, file, search=None, limit=None):
        sanitized_file = self.sanitize_file(file)
        if not sanitized_file:
            return None

        logs = load_logs(sanitized_file, search, limit)

        return LogResult(file, self.hostname, logs)

    def sanitize_file(self, file):
        """
        Ensures that user isn't pulling directory traversal shenanigans.
        Provided the path is within the configured directory and the file
        exists the path is returned otherwise return None
        """
        full_file = Path(f"{self.rootdir}{file}").resolve()
        var_log = str(Path(self.rootdir).resolve())
        if full_file.is_relative_to(var_log) and os.path.isfile(full_file):
            return str(full_file)
        else:
            return None


def load_logs(filename, search, limit):
    """
    Responsible for file handle lifecycle and parameter logic.
    """
    try:
        file = open(filename)
        i = 0
        for line in reverse_lines(file):
            if limit is None or (limit is not None and i < limit):
                if line != '':  # skip empty lines
                    if search is not None:
                        if any(ele in line for ele in search):
                            yield line
                            i += 1
                    else:
                        yield line
                        i += 1
            else:
                break
    finally:
        file.close()


def reverse_file(file):
    """
    Seeks the end of the file and walks backwards in buffered chunks, yielding 
    the current buffer.
    """
    file.seek(0, os.SEEK_END)
    size = file.tell()
    offset = size
    while offset > 0:
        this_size = min(10, offset)
        offset -= this_size

        file.seek(offset, os.SEEK_SET)
        yield file.read(this_size)


def reverse_lines(file):
    """
    Examines buffers in reverse order for a given file, yielding lines as they 
    are discovered.
    """
    current_line = ''
    for buffer in reverse_file(file):
        for position in range(len(buffer) - 1, -1, -1):
            if buffer[position] == '\n':  # whatever we've collected is g2g
                yield reverse_string(current_line)
                current_line = ''  # reset the buffer
            else:
                # regular character - append to the current line
                current_line += buffer[position]

    yield reverse_string(current_line)


def reverse_string(s):
    return s[::-1]
