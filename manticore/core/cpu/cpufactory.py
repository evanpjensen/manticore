from .x86 import AMD64Cpu, I386Cpu, AMD64LinuxSyscallAbi, I386LinuxSyscallAbi, I386CdeclAbi, SystemVAbi
from .arm import Armv7Cpu, Armv7CdeclAbi, Armv7LinuxSyscallAbi


class CpuFactory(object):
    """ CPU Helper Class

    Helper methods useful for constructing :obj:`Platforms`
    """
    _cpus = {
        'i386': I386Cpu,
        'amd64': AMD64Cpu,
        'armv7': Armv7Cpu,
    }

    @staticmethod
    def get_cpu(mem, machine):
        """ Get CPU

        Given a machine as a string, return an appropriate cpu object instantiated with mem.
        :param machine: Target machine
        :type machine: str

        :param machine: Target machine
        :type machine: str

        :rtype: :obj:`Cpu`
        """
        return CpuFactory._cpus[machine](mem)

    @staticmethod
    def get_function_abi(cpu, os, machine):
        """ Get function ABI

        Return suitable function ABI for a given combination of CPU, operating system and machine.

        :param cpu: Target cpu
        :type cpu: str
        :param os: Target operating system
        :type os: str
        :param machine: Target computer architecture
        :type machine: str

        :rtype: :obj:`Abi`
        """
        if os == 'linux' and machine == 'i386':
            return I386CdeclAbi(cpu)
        elif os == 'linux' and machine == 'amd64':
            return SystemVAbi(cpu)
        elif os == 'linux' and machine == 'armv7':
            return Armv7CdeclAbi(cpu)
        else:
            return NotImplementedError("OS and machine combination not supported: {}/{}".format(os, machine))

    @staticmethod
    def get_syscall_abi(cpu, os, machine):
        """ Get syscall ABI

        Return suitable syscall ABI for a given combination of CPU, operating system and machine.

        :param os: Target operating system
        :type os: str
        :param machine: Target computer architecture
        :type machine: str

        :rtype: :obj:`SyscallAbi`
        """

        if os == 'linux' and machine == 'i386':
            return I386LinuxSyscallAbi(cpu)
        elif os == 'linux' and machine == 'amd64':
            return AMD64LinuxSyscallAbi(cpu)
        elif os == 'linux' and machine == 'armv7':
            return Armv7LinuxSyscallAbi(cpu)
        else:
            return NotImplementedError("OS and machine combination not supported: {}/{}".format(os, machine))
