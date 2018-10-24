import io

from elftools.elf.elffile import ELFFile


class Binary:
    """Baseclass for representing binary file formats
    """

    magics = {}
    """Dict of str: :obj:`Binary`
    A mapping between "magic numbers" and binary representations.
    """

    def __new__(cls, path):
        if cls is Binary:
            cl = cls.magics[open(path, 'rb').read(4)]
            return cl(path)
        else:
            return super(Binary, cls).__new__(cls)

    def __init__(self, path):
        """Binary Constructor
            Args:
                path (str): path of the file on the filesystem.

        """
        self.path = path
        """Path of the binary on the filesystem.
        """

        self.magic = Binary.magics[open(path, 'rb').read(4)]
        """The Binary's "magic number" """

    def arch(self):
        pass

    def maps(self):
        """Representation of file sections

        :return: generator yielding tuples representing (virtual_address, virtual_allocation_size, memory_permissions, section_name, section_disk_offset, section_file_size )
        :rtype: generator[tuple[int, int, str, str, int, int]]
        """
        pass

    def threads(self):
        """Representation of thread execution at load time.

        :return: generator of 2-tuples in the form (state,{register:value})
        :rtype: generator[tuple[str, dict[str,int]]]
        """
        pass


class CGCElf(Binary):

    @staticmethod
    def _cgc2elf(filename):
        # hack begin so we can use upstream Elftool
        with open(filename, 'rb') as fd:
            stream = io.BytesIO(fd.read())
            stream.write(b'\x7fELF')
            stream.name = fd.name
            return stream

    def __init__(self, filename):
        super().__init__(filename)
        stream = self._cgc2elf(filename)
        self.elf = ELFFile(stream)
        self.arch = {'x86': 'i386', 'x64': 'amd64'}[self.elf.get_machine_arch()]

        assert 'i386' == self.arch
        assert self.elf.header.e_type in ['ET_EXEC']

    def maps(self):
        for elf_segment in self.elf.iter_segments():
            if elf_segment.header.p_type not in ['PT_LOAD', 'PT_NULL', 'PT_PHDR', 'PT_CGCPOV2']:
                raise Exception("Not Supported Section")

            if elf_segment.header.p_type != 'PT_LOAD' or elf_segment.header.p_memsz == 0:
                continue

            flags = elf_segment.header.p_flags
            # PF_X 0x1 Execute - PF_W 0x2 Write - PF_R 0x4 Read
            perms = ['   ', '  x', ' w ', ' wx', 'r  ', 'r x', 'rw ', 'rwx'][flags & 7]
            if 'r' not in perms:
                raise Exception("Not readable map from cgc elf not supported")

            # CGCMAP--
            assert elf_segment.header.p_filesz != 0 or elf_segment.header.p_memsz != 0
            yield ((elf_segment.header.p_vaddr,
                    elf_segment.header.p_memsz,
                    perms,
                    elf_segment.stream.name, elf_segment.header.p_offset, elf_segment.header.p_filesz))

    def threads(self):
        yield (('Running', {'EIP': self.elf.header.e_entry}))


class Elf(Binary):
    def __init__(self, filename):
        super().__init__(filename)
        self.elf = ELFFile(open(filename, 'rb'))
        self.arch = {'x86': 'i386', 'x64': 'amd64'}[self.elf.get_machine_arch()]
        assert self.elf.header.e_type in ['ET_DYN', 'ET_EXEC', 'ET_CORE']

        # Get interpreter elf
        self.interpreter = None

        for elf_segment in self.elf.iter_segments():
            if elf_segment.header.p_type != 'PT_INTERP':
                continue
            self.interpreter = Elf(elf_segment.data()[:-1])
            break
        if self.interpreter is not None:
            assert self.interpreter.arch == self.arch
            assert self.interpreter.elf.header.e_type in ['ET_DYN', 'ET_EXEC']

    def maps(self):
        for elf_segment in self.elf.iter_segments():
            if elf_segment.header.p_type != 'PT_LOAD' or elf_segment.header.p_memsz == 0:
                continue

            flags = elf_segment.header.p_flags
            # PF_X 0x1 Execute - PF_W 0x2 Write - PF_R 0x4 Read
            perms = ['   ', '  x', ' w ', ' wx', 'r  ', 'r x', 'rw ', 'rwx'][flags & 7]
            if 'r' not in perms:
                raise Exception("Not readable map from cgc elf not supported")

            # CGCMAP--
            assert elf_segment.header.p_filesz != 0 or elf_segment.header.p_memsz != 0
            yield ((elf_segment.header.p_vaddr,
                    elf_segment.header.p_memsz,
                    perms,
                    elf_segment.stream.name, elf_segment.header.p_offset, elf_segment.header.p_filesz))

    def getInterpreter(self):
        """Get the dynamic linker
        Returns the dynamic linker(if it is specified) as an :obj:`Elf` object otherwise, return none.

        :rtype: :obj:`Elf` or None
        """
        return self.interpreter

    def threads(self):
        yield (('Running', {'EIP': self.elf.header.e_entry}))


Binary.magics = {b'\x7fCGC': CGCElf,
                 b'\x7fELF': Elf}
