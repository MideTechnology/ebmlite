'''
Created on Nov 8, 2013

@author: dstokes
'''

import threading

class ThreadAwareFile(file):
    """ A 'replacement' for a standard read-only file stream that supports
        simultaneous access by multiple threads without (explicit) blocking.
        Each thread actually gets its own stream, so it can perform its own
        seeks without affecting other threads that may be reading the file.
        This functionality is transparent.

        ThreadAwareFile is read-only.
    """

    def __init__(self, *args, **kwargs):
        """ ThreadAwareFile(name[, mode[, buffering]]) -> file object

            Open a read-only file that may already be open in other threads.
            Takes the standard `file` arguments, except `mode` can only be
            read (``r``).
        """
        if len(args) > 1:
            if isinstance(args[1], basestring) and 'w' in args[1]:
                raise IOError("ThreadAwareFile is read-only")

        openNew = kwargs.pop('_new', True)

        self.initArgs = args[:]
        self.initKwargs = kwargs.copy()
        self.threads = {}
        self._busy = threading.Event() # NOT a lock; only some things block
        self.timeout = 60.0

        if openNew:
            ident = threading.currentThread().ident
            self.threads[ident] = file(*args, **kwargs)

        self.forceIdent = None


    @classmethod
    def makeThreadAware(cls, fileStream):
        """ Create a new `ThreadAwareFile` from an already-open file. If the
            object is a `ThreadAwareFile`, it is returned verbatim.
        """
        if isinstance(fileStream, cls):
            return fileStream
        elif not isinstance(fileStream, file):
            raise TypeError("Not a file: %r" % fileStream)

        newfile = cls(fileStream.name, fileStream.mode, _new=False)
        newfile.threads[newfile.getIdent()] = fileStream
        return newfile


    def getIdent(self):
        """ Get the identity of the current thread. If the attribute
            `forceIdent` is not `None`, `forceIdent` will be returned
            instead.
        """
        if self.forceIdent is not None:
            return self.forceIdent
        return threading.currentThread().ident


    def getThreadStream(self):
        """ Get (or create) the file stream for the current thread.
        """
        ident = self.getIdent()

        self._busy.wait(self.timeout)

        if ident not in self.threads:
            fp = file(*self.initArgs, **self.initKwargs)
            self.threads[ident] = fp
            return fp
        return self.threads[ident]


    def closeAll(self):
        """ Close all open streams.

            Warning: May not be thread-safe in some situations!
        """
        try:
            self._busy.set()
            for v in self.threads.values():
                v.close()
        finally:
            self._busy.clear()


    def changeFile(self, *args, **kwargs):
        """ Change the path of the file being accessed. Intended for
            maintaining access to a file after a 'Save As' without
            having to reload all the data. The arguments are the
            same as `file()`.

            Warning: May not be thread-safe in some situations!
        """
        if len(args) > 1:
            if isinstance(args[1], basestring):
                if 'w' in args[1] or 'a' in args[1]:
                    raise IOError("ThreadAwareFile is read-only")
        self.initArgs = args[:]
        self.initKwargs = kwargs.copy()

        try:
            self._busy.wait(self.timeout)
            for i in self.threads.keys():
                try:
                    self.threads.pop(i).close()
                except (KeyError, AttributeError):
                    pass
        finally:
            self._busy.clear()


    def cleanup(self):
        """ Delete all closed streams.
        """
        try:
            self._busy.wait(self.timeout)
            for i in self.threads.keys():
                if self.threads[i].closed:
                    del self.threads[i]
        finally:
            self._busy.clear()


    @property
    def closed(self):
        """ Is the file not open? Note: A thread that never accessed the file
            will get `True`.
        """
        ident = self.getIdent()
        if ident in self.threads:
            return self.threads[ident].closed
        return True


    def close(self, *args, **kwargs):
        return self.getThreadStream().close(*args, **kwargs)



    # Standard file methods, overridden

    def __format__(self, *args, **kwargs):
        return self.getThreadStream().__format__(*args, **kwargs)

    def __hash__(self, *args, **kwargs):
        return self.getThreadStream().__hash__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.getThreadStream().__iter__(*args, **kwargs)

    def __reduce__(self, *args, **kwargs):
        return self.getThreadStream().__reduce__(*args, **kwargs)

    def __reduce_ex__(self, *args, **kwargs):
        return self.getThreadStream().__reduce_ex__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self.getThreadStream().__repr__(*args, **kwargs)

    def __sizeof__(self, *args, **kwargs):
        return self.getThreadStream().__sizeof__(*args, **kwargs)

    def __str__(self, *args, **kwargs):
        return self.getThreadStream().__str__(*args, **kwargs)

    def fileno(self, *args, **kwargs):
        return self.getThreadStream().fileno(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self.getThreadStream().flush(*args, **kwargs)

    def isatty(self, *args, **kwargs):
        return self.getThreadStream().isatty(*args, **kwargs)

    def next(self, *args, **kwargs):
        return self.getThreadStream().next(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self.getThreadStream().read(*args, **kwargs)

    def readinto(self, *args, **kwargs):
        return self.getThreadStream().readinto(*args, **kwargs)

    def readline(self, *args, **kwargs):
        return self.getThreadStream().readline(*args, **kwargs)

    def readlines(self, *args, **kwargs):
        return self.getThreadStream().readlines(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self.getThreadStream().seek(*args, **kwargs)

    def tell(self, *args, **kwargs):
        return self.getThreadStream().tell(*args, **kwargs)

    def truncate(self, *args, **kwargs):
        raise IOError("Can't truncate(); ThreadAwareFile is read-only")

    def write(self, *args, **kwargs):
        raise IOError("Can't write(); ThreadAwareFile is read-only")

    def writelines(self, *args, **kwargs):
        raise IOError("Can't writelines(); ThreadAwareFile is read-only")

    def xreadlines(self, *args, **kwargs):
        return self.getThreadStream().xreadlines(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        return self.getThreadStream().__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        return self.getThreadStream().__exit__(*args, **kwargs)


    # Standard file attributes, as properties for transparency with 'real'
    # file objects. Most are read-only.

    @property
    def encoding(self):
        return self.getThreadStream().encoding

    @property
    def errors(self):
        return self.getThreadStream().errors

    @property
    def mode(self):
        return self.getThreadStream().mode

    @property
    def name(self):
        return self.getThreadStream().name

    @property
    def newlines(self):
        return self.getThreadStream().newlines

    @property
    def softspace(self):
        return self.getThreadStream().softspace

    @softspace.setter
    def softspace(self, val):
        self.getThreadStream().softspace = val
