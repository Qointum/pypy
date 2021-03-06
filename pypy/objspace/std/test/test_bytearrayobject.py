from pypy import conftest


class AppTestBytesArray:
    def setup_class(cls):
        cls.w_runappdirect = cls.space.wrap(conftest.option.runappdirect)

    def test_basics(self):
        b = bytearray()
        assert type(b) is bytearray
        assert b.__class__ is bytearray

    def test_constructor(self):
        assert bytearray() == b""
        assert bytearray(b'abc') == b"abc"
        assert bytearray([65, 66, 67]) == b"ABC"
        assert bytearray(5) == b'\0' * 5
        assert bytearray(set(b'foo')) in (b'fo', b'of')
        raises(TypeError, bytearray, ['a', 'bc'])
        raises(ValueError, bytearray, [65, -3])
        raises(TypeError, bytearray, [65.0])
        raises(ValueError, bytearray, -1)

    def test_init_override(self):
        class subclass(bytearray):
            def __init__(self, newarg=1, *args, **kwargs):
                bytearray.__init__(self, *args, **kwargs)
        x = subclass(4, source=b"abcd")
        assert x == b"abcd"

    def test_encoding(self):
        data = "Hello world\n\u1234\u5678\u9abc\def0\def0"
        for encoding in 'utf8', 'utf16':
            b = bytearray(data, encoding)
            assert b == data.encode(encoding)
        raises(TypeError, bytearray, 9, 'utf8')

    def test_encoding_with_ignore_errors(self):
        data = "H\u1234"
        b = bytearray(data, "latin1", errors="ignore")
        assert b == b"H"

    def test_len(self):
        b = bytearray(b'test')
        assert len(b) == 4

    def test_nohash(self):
        raises(TypeError, hash, bytearray())

    def test_repr(self):
        assert repr(bytearray()) == "bytearray(b'')"
        assert repr(bytearray(b'test')) == "bytearray(b'test')"
        assert repr(bytearray(b"d'oh")) == r'bytearray(b"d\'oh")'
        assert repr(bytearray(b'd"oh')) == 'bytearray(b\'d"oh\')'
        assert repr(bytearray(b'd"\'oh')) == 'bytearray(b\'d"\\\'oh\')'
        assert repr(bytearray(b'd\'"oh')) == 'bytearray(b\'d\\\'"oh\')'

    def test_str(self):
        assert str(bytearray()) == "bytearray(b'')"
        assert str(bytearray(b'test')) == "bytearray(b'test')"
        assert str(bytearray(b"d'oh")) == r'bytearray(b"d\'oh")'

    def test_getitem(self):
        b = bytearray(b'test')
        assert b[0] == ord('t')
        assert b[2] == ord('s')
        raises(IndexError, b.__getitem__, 4)
        assert b[1:5] == bytearray(b'est')
        assert b[slice(1,5)] == bytearray(b'est')

    def test_arithmetic(self):
        b1 = bytearray(b'hello ')
        b2 = bytearray(b'world')
        assert b1 + b2 == bytearray(b'hello world')
        assert b1 * 2 == bytearray(b'hello hello ')
        assert b1 * 1 is not b1

        b3 = b1
        b3 *= 3
        assert b3 == b'hello hello hello '
        assert type(b3) == bytearray
        assert b3 is b1

    def test_contains(self):
        assert ord('l') in bytearray(b'hello')
        assert b'l' in bytearray(b'hello')
        assert bytearray(b'll') in bytearray(b'hello')
        assert memoryview(b'll') in bytearray(b'hello')

        raises(TypeError, lambda: 'foo' in bytearray(b'foobar'))

    def test_splitlines(self):
        b = bytearray(b'1234')
        assert b.splitlines()[0] == b
        assert b.splitlines()[0] is not b

        assert len(bytearray(b'foo\nbar').splitlines()) == 2
        for item in bytearray(b'foo\nbar').splitlines():
            assert isinstance(item, bytearray)

    def test_ord(self):
        b = bytearray(b'\0A\x7f\x80\xff')
        assert ([ord(b[i:i+1]) for i in range(len(b))] ==
                         [0, 65, 127, 128, 255])
        raises(TypeError, ord, bytearray(b'll'))
        raises(TypeError, ord, bytearray())

    def test_translate(self):
        b = b'hello'
        ba = bytearray(b)
        rosetta = bytearray(range(0, 256))
        rosetta[ord('o')] = ord('e')

        c = ba.translate(rosetta)
        assert ba == bytearray(b'hello')
        assert c == bytearray(b'helle')
        assert isinstance(c, bytearray)

    def test_strip(self):
        b = bytearray(b'mississippi ')

        assert b.strip() == b'mississippi'
        assert b.strip(None) == b'mississippi'

        b = bytearray(b'mississippi')

        for strip_type in bytes, memoryview:
            assert b.strip(strip_type(b'i')) == b'mississipp'
            assert b.strip(strip_type(b'm')) == b'ississippi'
            assert b.strip(strip_type(b'pi')) == b'mississ'
            assert b.strip(strip_type(b'im')) == b'ssissipp'
            assert b.strip(strip_type(b'pim')) == b'ssiss'
            assert b.strip(strip_type(b)) == b''

    def test_iter(self):
        assert list(bytearray(b'hello')) == [104, 101, 108, 108, 111]
        assert list(bytearray(b'hello').__iter__()) == [104, 101, 108, 108, 111]

    def test_compare(self):
        assert bytearray(b'hello') == bytearray(b'hello')
        assert bytearray(b'hello') < bytearray(b'world')
        assert bytearray(b'world') > bytearray(b'hello')

    def test_compare_str(self):
        assert bytearray(b'hello1') == b'hello1'
        assert not (bytearray(b'hello1') != b'hello1')
        assert b'hello2' == bytearray(b'hello2')
        assert not (b'hello1' != bytearray(b'hello1'))
        # unicode is always different
        assert not (bytearray(b'hello3') == 'world')
        assert bytearray(b'hello3') != 'hello3'
        assert 'hello3' != bytearray(b'world')
        assert 'hello4' != bytearray(b'hello4')
        assert not (bytearray(b'') == '')
        assert not ('' == bytearray(b''))
        assert bytearray(b'') != ''
        assert '' != bytearray(b'')

    def test_stringlike_operations(self):
        assert bytearray(b'hello').islower()
        assert bytearray(b'HELLO').isupper()
        assert bytearray(b'hello').isalpha()
        assert not bytearray(b'hello2').isalpha()
        assert bytearray(b'hello2').isalnum()
        assert bytearray(b'1234').isdigit()
        assert bytearray(b'   ').isspace()
        assert bytearray(b'Abc').istitle()

        assert bytearray(b'hello').count(b'l') == 2
        assert bytearray(b'hello').count(bytearray(b'l')) == 2
        assert bytearray(b'hello').count(memoryview(b'l')) == 2

        assert bytearray(b'hello').index(b'e') == 1
        assert bytearray(b'hello').rindex(b'l') == 3
        assert bytearray(b'hello').index(bytearray(b'e')) == 1
        assert bytearray(b'hello').find(b'l') == 2
        assert bytearray(b'hello').find(b'l', -2) == 3
        assert bytearray(b'hello').rfind(b'l') == 3


        # these checks used to not raise in pypy but they should
        raises(TypeError, bytearray(b'hello').index, ord('e'))
        raises(TypeError, bytearray(b'hello').rindex, ord('e'))
        raises(TypeError, bytearray(b'hello').find, ord('e'))
        raises(TypeError, bytearray(b'hello').rfind, ord('e'))

        assert bytearray(b'hello').startswith(b'he')
        assert bytearray(b'hello').startswith(bytearray(b'he'))
        assert bytearray(b'hello').startswith((b'lo', bytearray(b'he')))
        assert bytearray(b'hello').endswith(b'lo')
        assert bytearray(b'hello').endswith(bytearray(b'lo'))
        assert bytearray(b'hello').endswith((bytearray(b'lo'), b'he'))
        try:
            bytearray(b'hello').startswith([b'o'])
        except TypeError as e:
            assert 'bytes' in str(e)
        else:
            assert False, 'Expected TypeError'
        try:
            bytearray(b'hello').endswith([b'o'])
        except TypeError as e:
            assert 'bytes' in str(e)
        else:
            assert False, 'Expected TypeError'

    def test_startswith_too_large(self):
        assert bytearray(b'ab').startswith(bytearray(b'b'), 1) is True
        assert bytearray(b'ab').startswith(bytearray(b''), 2) is True
        assert bytearray(b'ab').startswith(bytearray(b''), 3) is False
        assert bytearray(b'ab').endswith(bytearray(b'b'), 1) is True
        assert bytearray(b'ab').endswith(bytearray(b''), 2) is True
        assert bytearray(b'ab').endswith(bytearray(b''), 3) is False

    def test_stringlike_conversions(self):
        # methods that should return bytearray (and not str)
        def check(result, expected):
            assert result == expected
            assert type(result) is bytearray

        check(bytearray(b'abc').replace(b'b', bytearray(b'd')), b'adc')
        check(bytearray(b'abc').replace(b'b', b'd'), b'adc')

        check(bytearray(b'abc').upper(), b'ABC')
        check(bytearray(b'ABC').lower(), b'abc')
        check(bytearray(b'abc').title(), b'Abc')
        check(bytearray(b'AbC').swapcase(), b'aBc')
        check(bytearray(b'abC').capitalize(), b'Abc')

        check(bytearray(b'abc').ljust(5),  b'abc  ')
        check(bytearray(b'abc').rjust(5),  b'  abc')
        check(bytearray(b'abc').center(5), b' abc ')
        check(bytearray(b'1').zfill(5), b'00001')
        check(bytearray(b'1\t2').expandtabs(5), b'1    2')

        check(bytearray(b',').join([b'a', bytearray(b'b')]), b'a,b')
        check(bytearray(b'abca').lstrip(b'a'), b'bca')
        check(bytearray(b'cabc').rstrip(b'c'), b'cab')
        check(bytearray(b'abc').lstrip(memoryview(b'a')), b'bc')
        check(bytearray(b'abc').rstrip(memoryview(b'c')), b'ab')
        check(bytearray(b'aba').strip(b'a'), b'b')

    def test_xjust_no_mutate(self):
        # a previous regression
        b = bytearray(b'')
        assert b.ljust(1) == bytearray(b' ')
        assert not len(b)

        b2 = b.ljust(0)
        b2 += b' '
        assert not len(b)

        b2 = b.rjust(0)
        b2 += b' '
        assert not len(b)

    def test_split(self):
        # methods that should return a sequence of bytearrays
        def check(result, expected):
            assert result == expected
            assert set(type(x) for x in result) == set([bytearray])

        b = bytearray(b'mississippi')
        check(b.split(b'i'), [b'm', b'ss', b'ss', b'pp', b''])
        check(b.split(memoryview(b'i')), [b'm', b'ss', b'ss', b'pp', b''])
        check(b.rsplit(b'i'), [b'm', b'ss', b'ss', b'pp', b''])
        check(b.rsplit(memoryview(b'i')), [b'm', b'ss', b'ss', b'pp', b''])
        check(b.rsplit(b'i', 2), [b'mississ', b'pp', b''])

        check(bytearray(b'foo bar').split(), [b'foo', b'bar'])
        check(bytearray(b'foo bar').split(None), [b'foo', b'bar'])

        check(b.partition(b'ss'), (b'mi', b'ss', b'issippi'))
        check(b.partition(memoryview(b'ss')), (b'mi', b'ss', b'issippi'))
        check(b.rpartition(b'ss'), (b'missi', b'ss', b'ippi'))
        check(b.rpartition(memoryview(b'ss')), (b'missi', b'ss', b'ippi'))

    def test_append(self):
        b = bytearray(b'abc')
        b.append(ord('d'))
        b.append(ord('e'))
        assert b == b'abcde'

    def test_insert(self):
        b = bytearray(b'abc')
        b.insert(0, ord('d'))
        assert b == bytearray(b'dabc')

        b.insert(-1, ord('e'))
        assert b == bytearray(b'dabec')

        b.insert(6, ord('f'))
        assert b == bytearray(b'dabecf')

        b.insert(1, ord('g'))
        assert b == bytearray(b'dgabecf')

        b.insert(-12, ord('h'))
        assert b == bytearray(b'hdgabecf')

        raises(TypeError, b.insert, 1, 'g')
        raises(TypeError, b.insert, 1, b'g')
        raises(TypeError, b.insert, b'g', b'o')

    def test_pop(self):
        b = bytearray(b'world')
        assert b.pop() == ord('d')
        assert b.pop(0) == ord('w')
        assert b.pop(-2) == ord('r')
        raises(IndexError, b.pop, 10)
        raises(IndexError, bytearray().pop)
        assert bytearray(b'\xff').pop() == 0xff

    def test_remove(self):
        class Indexable:
            def __index__(self):
                return ord('e')

        b = bytearray(b'hello')
        b.remove(ord('l'))
        assert b == b'helo'
        b.remove(ord('l'))
        assert b == b'heo'
        raises(ValueError, b.remove, ord('l'))
        raises(ValueError, b.remove, 400)
        raises(TypeError, b.remove, 'e')
        raises(TypeError, b.remove, 2.3)
        # remove first and last
        b.remove(ord('o'))
        b.remove(ord('h'))
        assert b == b'e'
        raises(TypeError, b.remove, 'e')
        b.remove(Indexable())
        assert b == b''

    def test_reverse(self):
        b = bytearray(b'hello')
        b.reverse()
        assert b == bytearray(b'olleh')

    def test_delitem(self):
        b = bytearray(b'abc')
        del b[1]
        assert b == bytearray(b'ac')
        del b[1:1]
        assert b == bytearray(b'ac')
        del b[:]
        assert b == bytearray()

        b = bytearray(b'fooble')
        del b[::2]
        assert b == bytearray(b'obe')

    def test_iadd(self):
        b = bytearray(b'abc')
        b += b'def'
        assert b == b'abcdef'
        assert isinstance(b, bytearray)
        raises(TypeError, b.__iadd__, "")

    def test_add(self):
        b1 = bytearray(b"abc")
        b2 = bytearray(b"def")

        def check(a, b, expected):
            result = a + b
            assert result == expected
            assert isinstance(result, bytearray)

        check(b1, b2, b"abcdef")
        check(b1, b"def", b"abcdef")
        check(b"def", b1, b"defabc")
        check(b1, memoryview(b"def"), b"abcdef")
        raises(TypeError, lambda: b1 + "def")
        raises(TypeError, lambda: "abc" + b2)

    def test_fromhex(self):
        raises(TypeError, bytearray.fromhex, 9)

        assert bytearray.fromhex('') == bytearray()
        assert bytearray.fromhex('') == bytearray()

        b = bytearray([0x1a, 0x2b, 0x30])
        assert bytearray.fromhex('1a2B30') == b
        assert bytearray.fromhex('  1A 2B  30   ') == b
        assert bytearray.fromhex('0000') == b'\0\0'

        raises(ValueError, bytearray.fromhex, 'a')
        raises(ValueError, bytearray.fromhex, 'A')
        raises(ValueError, bytearray.fromhex, 'rt')
        raises(ValueError, bytearray.fromhex, '1a b cd')
        raises(ValueError, bytearray.fromhex, '\x00')
        raises(ValueError, bytearray.fromhex, '12   \x00   34')
        raises(ValueError, bytearray.fromhex, '\u1234')

    def test_extend(self):
        b = bytearray(b'abc')
        b.extend(bytearray(b'def'))
        b.extend(b'ghi')
        assert b == b'abcdefghi'
        b.extend(memoryview(b'jkl'))
        assert b == b'abcdefghijkl'

        b = bytearray(b'world')
        b.extend([ord(c) for c in 'hello'])
        assert b == bytearray(b'worldhello')

        b = bytearray(b'world')
        b.extend(list(b'hello'))
        assert b == bytearray(b'worldhello')

        b = bytearray(b'world')
        b.extend(c for c in b'hello')
        assert b == bytearray(b'worldhello')

        raises(TypeError, b.extend, 3)
        raises(TypeError, b.extend, [b'fish'])
        raises(ValueError, b.extend, [256])
        raises(TypeError, b.extend, object())
        raises(TypeError, b.extend, [object()])
        raises(TypeError, b.extend, "unicode")

    def test_setslice(self):
        b = bytearray(b'hello')
        b[:] = [ord(c) for c in 'world']
        assert b == bytearray(b'world')

        b = bytearray(b'hello world')
        b[::2] = b'bogoff'
        assert b == bytearray(b'beolg ooflf')

        def set_wrong_size():
            b[::2] = b'foo'
        raises(ValueError, set_wrong_size)

    def test_delitem_slice(self):
        b = bytearray(b'abcdefghi')
        del b[5:8]
        assert b == b'abcdei'
        del b[:3]
        assert b == b'dei'

        b = bytearray(b'hello world')
        del b[::2]
        assert b == bytearray(b'el ol')

    def test_setitem(self):
        b = bytearray(b'abcdefghi')
        b[1] = ord('B')
        assert b == b'aBcdefghi'

    def test_setitem_slice(self):
        b = bytearray(b'abcdefghi')
        b[0:3] = b'ABC'
        assert b == b'ABCdefghi'
        b[3:3] = b'...'
        assert b == b'ABC...defghi'
        b[3:6] = b'()'
        assert b == b'ABC()defghi'
        b[6:6] = b'<<'
        assert b == b'ABC()d<<efghi'

    def test_buffer(self):
        b = bytearray(b'abcdefghi')
        buf = memoryview(b)
        assert buf[2] == b'c'
        buf[3] = b'D'
        assert b == b'abcDefghi'
        buf[4:6] = b'EF'
        assert b == b'abcDEFghi'

    def test_decode(self):
        b = bytearray(b'abcdefghi')
        u = b.decode('utf-8')
        assert isinstance(u, str)
        assert u == 'abcdefghi'
        assert b.decode().encode() == b

    def test_int(self):
        assert int(bytearray(b'-1234')) == -1234
        assert int(bytearray(b'10'), 16) == 16

    def test_float(self):
        assert float(bytearray(b'10.4')) == 10.4
        assert float(bytearray(b'-1.7e-1')) == -1.7e-1
        assert float(bytearray('.9e10', 'utf-8')) == .9e10
        import math
        assert math.isnan(float(bytearray(b'nan')))
        raises(ValueError, float, bytearray(b'not_a_number'))

    def test_reduce(self):
        assert bytearray(b'caf\xe9').__reduce__() == (
            bytearray, ('caf\xe9', 'latin-1'), None)

    def test_setitem_slice_performance(self):
        # because of a complexity bug, this used to take forever on a
        # translated pypy.  On CPython2.6 -A, it takes around 8 seconds.
        if self.runappdirect:
            count = 16*1024*1024
        else:
            count = 1024
        b = bytearray(count)
        for i in range(count):
            b[i:i+1] = b'y'
        assert bytes(b) == b'y' * count

    def test_partition_return_copy(self):
        b = bytearray(b'foo')
        assert b.partition(b'x')[0] is not b

    def test_split_whitespace(self):
        b = bytearray(b'\x09\x0A\x0B\x0C\x0D\x1C\x1D\x1E\x1F')
        assert b.split() == [b'\x1c\x1d\x1e\x1f']

    def test_maketrans(self):
        table = b'\000\001\002\003\004\005\006\007\010\011\012\013\014\015\016\017\020\021\022\023\024\025\026\027\030\031\032\033\034\035\036\037 !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`xyzdefghijklmnopqrstuvwxyz{|}~\177\200\201\202\203\204\205\206\207\210\211\212\213\214\215\216\217\220\221\222\223\224\225\226\227\230\231\232\233\234\235\236\237\240\241\242\243\244\245\246\247\250\251\252\253\254\255\256\257\260\261\262\263\264\265\266\267\270\271\272\273\274\275\276\277\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357\360\361\362\363\364\365\366\367\370\371\372\373\374\375\376\377'
        result = bytearray.maketrans(b'abc', b'xyz')
        assert result == table
        assert type(result) is bytes
