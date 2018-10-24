''' Common binary formats interface

Ideally you should be able to do something like code::

    from binary import Binary
    binary = Binary(filename)
    assert cpu.machine == binary.arch, "Not matching cpu"
    logger.info("Loading %s as a %s elf"%(filename, binary.arch))
    for mm in binary.maps():
        cpu.mem.mmapFile( mm )
    for th in binary.threads():
        setup(th)


There are differences between formats that make it difficult to find a simple
and common API. Interpreters? linkers? linked DLLs? If this representation doesn't work for you consider contributing back what you come up with.


'''

from .binary import Binary, CGCElf, Elf  # noqa


if __name__ == '__main__':
    import sys
    print(list(Binary(sys.argv[1]).threads()))
    print(list(Binary(sys.argv[1]).maps()))
