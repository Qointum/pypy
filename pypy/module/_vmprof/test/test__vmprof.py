
from rpython.tool.udir import udir
from pypy.tool.pytest.objspace import gettestobjspace

class AppTestVMProf(object):
    def setup_class(cls):
        cls.space = gettestobjspace(usemodules=['_vmprof', 'struct'])
        cls.tmpfile = udir.join('test__vmprof.1').open('wb')
        cls.w_tmpfileno = cls.space.wrap(cls.tmpfile.fileno())
        cls.w_tmpfilename = cls.space.wrap(cls.tmpfile.name)
        cls.tmpfile2 = udir.join('test__vmprof.2').open('wb')
        cls.w_tmpfileno2 = cls.space.wrap(cls.tmpfile2.fileno())
        cls.w_tmpfilename2 = cls.space.wrap(cls.tmpfile2.name)

    def test_import_vmprof(self):
        import struct, sys

        WORD = struct.calcsize('l')
        
        def count(s):
            i = 0
            count = 0
            i += 5 * WORD # header
            assert s[i    ] == 5    # MARKER_HEADER
            assert s[i + 1] == 0    # 0
            assert s[i + 2] == 1    # VERSION_THREAD_ID
            assert s[i + 3] == 4    # len('pypy')
            assert s[i + 4: i + 8] == b'pypy'
            i += 8
            while i < len(s):
                if s[i] == 3:
                    break
                elif s[i] == 1:
                    i += 1
                    _, size = struct.unpack("ll", s[i:i + 2 * WORD])
                    i += 2 * WORD + size * struct.calcsize("P")
                elif s[i] == 2:
                    i += 1
                    _, size = struct.unpack("ll", s[i:i + 2 * WORD])
                    count += 1
                    i += 2 * WORD + size
                else:
                    raise AssertionError(ord(s[i]))
            return count
        
        import _vmprof
        _vmprof.enable(self.tmpfileno, 0.01)
        _vmprof.disable()
        s = open(self.tmpfilename, 'rb').read()
        no_of_codes = count(s)
        assert no_of_codes > 10
        d = {}

        def exec_(code, d):
            exec(code, d)

        exec_("""def foo():
            pass
        """, d)

        _vmprof.enable(self.tmpfileno2, 0.01)

        exec_("""def foo2():
            pass
        """, d)

        _vmprof.disable()
        s = open(self.tmpfilename2, 'rb').read()
        no_of_codes2 = count(s)
        assert b"py:foo:" in s
        assert b"py:foo2:" in s
        assert no_of_codes2 >= no_of_codes + 2 # some extra codes from tests

    def test_enable_ovf(self):
        import _vmprof
        raises(_vmprof.VMProfError, _vmprof.enable, 999, 0)
        raises(_vmprof.VMProfError, _vmprof.enable, 999, -2.5)
        raises(_vmprof.VMProfError, _vmprof.enable, 999, 1e300)
        raises(_vmprof.VMProfError, _vmprof.enable, 999, 1e300 * 1e300)
        NaN = (1e300*1e300) / (1e300*1e300)
        raises(_vmprof.VMProfError, _vmprof.enable, 999, NaN)
