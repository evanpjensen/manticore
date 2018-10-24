
from .expression import (
    BitVec, BitVecExtract, BitVecSignExtend, BitVecZeroExtend, BitVecConstant, BitVecConcat, Bool, BitVecITE, BoolConstant, BoolITE
)
from ...utils.helpers import issymbolic
import math


def ORD(s):
    """ ORDinal
    Approximation of the `ord` function from python.
    Extract the lower 8 bits from a quantitiy.
    :param s: Quantity to extract bits from
    :type s: BitVec or int
    :rtype: BitVec or int

    """
    if isinstance(s, BitVec):
        if s.size == 8:
            return s
        else:
            return BitVecExtract(s, 0, 7)
    elif isinstance(s, int):
        return s & 0xff
    else:
        return ord(s)


def CHR(s):
    """CHaRacter
    Approximation of the `chr` function from python.
    Transforms the input queantity to a character or symbolic character.

    :param s: Quantity to transform
    :type s: BitVec or int
    :rtype: BitVec or str
    """
    if isinstance(s, BitVec):
        if s.size == 8:
            return s
        else:
            return BitVecExtract(s, 0, 8)
    elif isinstance(s, int):
        return bytes([s & 0xff])
    else:
        assert len(s) == 1
        return s


def NOT(a):
    """Bitwise not
    :param a: Quantity to NOT
    :type a: bool or :obj:`Bool` or int
    :rtype: bool or :obj:`Bool` or int

    """
    if isinstance(a, bool):
        return not a
    if isinstance(a, (Bool, int)):
        return ~a
    return a == False


def AND(a, b, *others):
    """ Logical and
    Compute the logical and of two or more values

    :param a: Quantity to AND
    :type a: int or bool or :obj:`Bool`

    :param b: Quantity to AND
    :type b: int or bool or :obj:`Bool`

    :param others: Optional quantities to AND
    :type others: list[int or bool or :obj:`Bool`]

    :rtype: bool or :obj:`Bool`

    """

    if len(others) > 0:
        b = AND(b, others[0], *others[1:])
    if isinstance(a, Bool):
        return a & b
    if isinstance(b, Bool):
        return b & a
    assert isinstance(a, bool) and isinstance(b, bool)
    return a & b


def OR(a, b, *others):
    """ Logical or
    Compute the logical or of two or more values

    :param a: Quantity to OR
    :type a: int or bool or :obj:`Bool`

    :param b: Quantity to OR
    :type b: int or bool or :obj:`Bool`

    :param others: Optional quantities to OR
    :type others: list[bool or :obj:`Bool`]

    :rtype: int or bool or :obj:`Bool`
    """

    if len(others) > 0:
        b = OR(b, others[0], *others[1:])
    if isinstance(a, Bool):
        return a | b
    if isinstance(b, Bool):
        return b | a
    result = a | b
    if isinstance(result, (BitVec, int)):
        result = ITE(result != 0, True, False)
    return result


def XOR(a, b):
    """ Exclusive or

    Compute the exclusive or of two values

    :param a: Quantity to XOR
    :type a: int or bool or :obj:`Bool`

    :param b: Quantity to XOR
    :type b: int or bool or :obj:`Bool`

    :rtype: int or bool or :obj:`Bool`

    """

    result = a ^ b
    if isinstance(result, (BitVec, int)):
        result = ITE(result != 0, True, False)
    return result


def UGT(a, b):
    """ Unsigned greater than

    Perform a test to see if a is greater than b.

    :param a: Quantity to compare
    :type a: int or bool or :obj:`Bool`

    :param b: Quantity to compare
    :type b: int or bool or :obj:`Bool`

    :rtype: bool or :obj:`Bool`

    """
    if isinstance(a, BitVec):
        return a.ugt(b)
    if isinstance(b, BitVec):
        return b.ult(a)
    if a < 0:
        a = a & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    if b < 0:
        b = b & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    return a > b


def UGE(a, b):
    """ Unsigned greater than or equal

    Perform a test to see if a is greater than or equal to b.

    :param a: Quantity to compare
    :type a: int or bool or :obj:`Bool`

    :param b: Quantity to compare
    :type b: int or bool or :obj:`Bool`

    :rtype: bool or :obj:`Bool`

    """

    if isinstance(a, BitVec):
        return a.uge(b)
    if isinstance(b, BitVec):
        return b.ule(a)
    if a < 0:
        a = a & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    if b < 0:
        b = b & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    return a >= b


def ULT(a, b):
    """ Unsigned less than

    Perform a test to see if a is less than b.

    :param a: Quantity to compare
    :type a: int or bool or :obj:`Bool`

    :param b: Quantity to compare
    :type b: int or bool or :obj:`Bool`

    :rtype: bool or :obj:`Bool`

    """

    if isinstance(a, BitVec):
        return a.ult(b)
    if isinstance(b, BitVec):
        return b.ugt(a)
    if a < 0:
        a = a & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    if b < 0:
        b = b & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    return a < b


def ULE(a, b):
    """ Unsigned less than or equal

    Perform a test to see if a is less than or equal to b.

    :param a: Quantity to compare
    :type a: int or bool or :obj:`Bool`

    :param b: Quantity to compare
    :type b: int or bool or :obj:`Bool`

    :rtype: bool or :obj:`Bool`

    """

    if isinstance(a, BitVec):
        return a.ule(b)
    if isinstance(b, BitVec):
        return b.uge(a)
    if a < 0:
        a = a & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    if b < 0:
        b = b & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    return a <= b


def EXTRACT(x, offset, size):
    """ Extract bits from a :obj:`BitVec`

    Extract `size` bits from `x` starting at the specified `offset` and create a new :obj:`BitVec` or int.

    :param x: Quantity to extract bits from
    :type x: int or :obj:`BitVec`

    :param offset: Offset into x to start reading bits from
    :type offset: int

    :param size:  Number of bits to read from x
    :type size: int

    :rtype: int or :obj:`BitVec`

    """

    if isinstance(x, BitVec):
        if offset == 0 and size == x.size:
            return x
        return BitVecExtract(x, offset, size)
    else:
        return (x >> offset) & ((1 << size) - 1)


def SEXTEND(x, size_src, size_dest):
    """ Sign extend

    Create a new :obj:`BitVec` by sign extending x into a new quantity with `size_dest` bits.

    :param x: Quantity to sign extend
    :type x: int or :obj:`BitVec`

    :param size_src: number of bits before the sign bit in x
    :type size_src: int

    :param size_dest: Number of bits in the new value created from extending x
    :type size_dest: int

    :rtype: int or :obj:`BitVec`


    """

    if isinstance(x, int):
        if x >= (1 << (size_src - 1)):
            x -= 1 << size_src
        return x & ((1 << size_dest) - 1)
    assert x.size == size_src
    return BitVecSignExtend(x, size_dest)


def ZEXTEND(x, size):
    """ Zero extend
    Create a new quantity from x by means of zero extension.

    :param x: Quantity to zero extend
    :type x: int or :obj:`BitVec`

    :param size: number of bits before the sign bit in x
    :type size: int

    :rtype: int or :obj:`BitVec`

    """
    if isinstance(x, int):
        return x & ((1 << size) - 1)
    assert isinstance(x, BitVec) and size - x.size >= 0
    if size - x.size > 0:
        return BitVecZeroExtend(size, x)
    else:
        return x


def CONCAT(total_size, *args):
    """ Concatenate
    Create one large integer or :obj:`BitVec` from two or more smaller ones. The sizes of all the quantities in `args` should be the same.

    :param total_size: Total size of everything in `args`
    :type total_size: int or :obj:`BitVec`

    :param args: List of quantities to concatenate
    :type args: list[:obj:`BitVec` or int]

    :rtype: int or :obj:`BitVec`

    """

    arg_size = total_size // len(args)
    if any(issymbolic(x) for x in args):
        if len(args) > 1:
            def cast(x):
                if isinstance(x, int):
                    return BitVecConstant(arg_size, x)
                return x
            return BitVecConcat(total_size, *list(map(cast, args)))
        else:
            return args[0]
    else:
        result = 0
        for arg in args:
            result = (result << arg_size) | (arg & ((1 << arg_size) - 1))
        return result


def ITE(cond, true_value, false_value):
    """ If-than-else

    If cond evaluates to true, return the true_value, otherwise return the false_value.

    :param cond: conditional value
    :type cond: bool or :obj:`Bool`

    :param true_value: Value to return if cond evaluates to true
    :type true_value: int or bool or :obj:`BitVec` or :obj:`Bool`

    :param false_value: Value to return if cond evaluates to false
    :type false_value:  int or bool or :obj:`BitVec` or :obj:`Bool`

    :rtype: int or bool or :obj:`BitVec` or :obj:`Bool`

    """
    assert isinstance(true_value, (Bool, bool, BitVec, int))
    assert isinstance(false_value, (Bool, bool, BitVec, int))
    assert isinstance(cond, (Bool, bool))
    if isinstance(cond, bool):
        if cond:
            return true_value
        else:
            return false_value

    if isinstance(true_value, bool):
        true_value = BoolConstant(true_value)

    if isinstance(false_value, bool):
        false_value = BoolConstant(false_value)

    return BoolITE(cond, true_value, false_value)


def ITEBV(size, cond, true_value, false_value):
    """  If-than-else Bitvector

    If cond evaluates to true, return the true_value, otherwise return the false_value. Differs from `ITE` in that cond may be an int or :obj:`BitVec`.

    :param cond: conditional value
    :type cond: int or bool or :obj:`BitVec` or :obj:`Bool`

    :param true_value: Value to return if cond evaluates to true
    :type true_value: int or bool or :obj:`BitVec` or :obj:`Bool`

    :param false_value: Value to return if cond evaluates to false
    :type false_value:  int or bool or :obj:`BitVec` or :obj:`Bool`

    :rtype: int or bool or :obj:`BitVec` or :obj:`Bool`

    """
    if isinstance(cond, BitVec):
        cond = cond.Bool()
    if isinstance(cond, int):
        cond = (cond != 0)

    assert isinstance(cond, (Bool, bool))
    assert isinstance(true_value, (BitVec, int))
    assert isinstance(false_value, (BitVec, int))
    assert isinstance(size, int)

    if isinstance(cond, bool):
        if cond:
            return true_value
        else:
            return false_value

    if isinstance(true_value, int):
        true_value = BitVecConstant(size, true_value)

    if isinstance(false_value, int):
        false_value = BitVecConstant(size, false_value)
    return BitVecITE(size, cond, true_value, false_value)


def UDIV(dividend, divisor):
    """ Unsigned division

    Performs unsigned integer division.

    :param Dividend: dividend or top of division expression.
    :type dividend: int or :obj:`BitVec`

    :param Divisor: divisor or botton of division expression
    :type divisor:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """
    if isinstance(dividend, BitVec):
        return dividend.udiv(divisor)
    elif isinstance(divisor, BitVec):
        return divisor.rudiv(dividend)
    assert dividend >= 0 or divisor > 0  # unsigned-es
    return dividend // divisor


def SDIV(a, b):
    """ Signed division

    Performs signed integer division.

    :param a: Dividend or top of division expression.
    :type a: int or :obj:`BitVec`

    :param b: Divisor or botton of division expression
    :type b:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """

    if isinstance(a, BitVec):
        return a // b
    elif isinstance(b, BitVec):
        return b.__rsdiv__(a)
    return int(math.trunc(float(a) / float(b)))


def SMOD(a, b):
    """ Signed modulo

    Performs signed modulo by performing finding the remainder of a signed division on a and b.

    :param a: Dividend or top of division expression.
    :type a: int or :obj:`BitVec`

    :param b: Divisor or botton of division expression
    :type b:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """

    if isinstance(a, BitVec):
        return a.smod(b)
    elif isinstance(b, BitVec):
        return b.rsmod(a)
    return int(math.fmod(a, b))


def SREM(a, b):
    """ Signed remainder

    Finds the remainder of a signed division on a and b. Differs from  operation `SMOD` when one number is negative.

    :param a: Dividend or top of division expression.
    :type a: int or :obj:`BitVec`

    :param b: Divisor or botton of division expression
    :type b:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """

    if isinstance(a, BitVec):
        return a.srem(b)
    elif isinstance(a, BitVec):
        return b.rsrem(a)
    return a % b


def UREM(a, b):
    """ Unsigned remainder

    Finds the remainder of unsigned division on a and b.

    :param a: Dividend or top of division expression.
    :type a: int or :obj:`BitVec`

    :param b: Divisor or botton of division expression
    :type b:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """


    if isinstance(a, BitVec):
        return a.urem(b)
    elif isinstance(a, BitVec):
        return b.rurem(a)
    return a % b


def simplify(value):
    """Simplify symbolic expression

    If possible, return a simplified version of the symbolic expression `value`


    :param value: Symbolic expression to be simplified
    :type value:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """
    if issymbolic(value):
        return value.simplify()
    return value


def SAR(size, a, b):
    """Shift arithmetic right

    Shift `a` to the right by `b` bits.


    :param size: Number of bits in a
    :type size:  int or :obj:`BitVec`


    :param a: Quantity to be shifted
    :type a:  int or :obj:`BitVec`


    :param b: Quantity to shift by
    :type b:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """
    assert isinstance(size, int)
    if isinstance(b, BitVec) and b.size != size:
        b = ZEXTEND(b, size)
    if isinstance(a, BitVec):
        assert size == a.size
        return a.sar(b)
    elif isinstance(b, BitVec):
        return BitVecConstant(size, a).sar(b)
    else:
        tempDest = a
        tempCount = b
        sign = tempDest & (1 << (size - 1))
        while tempCount != 0:
            tempDest = (tempDest >> 1) | sign
            tempCount = tempCount - 1
        return tempDest


def ABS(a):
    """Absolute value
    Take the absolute value of `a`

    :param a: Quantity to be shifted
    :type a:  int or :obj:`BitVec`

    :rtype: int or :obj:`BitVec`

    """
    if issymbolic(a):
        return ITEBV(a.size, a < 0, -a, a)
    else:
        return abs(a)
