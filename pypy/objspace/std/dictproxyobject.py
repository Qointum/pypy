from rpython.rlib import rerased

from pypy.interpreter.error import OperationError, oefmt
from pypy.objspace.std.dictmultiobject import (
    DictStrategy, create_iterator_classes)
from pypy.objspace.std.typeobject import unwrap_cell


class DictProxyStrategy(DictStrategy):
    erase, unerase = rerased.new_erasing_pair("dictproxy")
    erase = staticmethod(erase)
    unerase = staticmethod(unerase)

    def __init__(w_self, space):
        DictStrategy.__init__(w_self, space)

    def getitem(self, w_dict, w_key):
        space = self.space
        w_lookup_type = space.type(w_key)
        if space.is_true(space.issubtype(w_lookup_type, space.w_unicode)):
            return self.getitem_str(w_dict, space.str_w(w_key))
        else:
            return None

    def getitem_str(self, w_dict, key):
        return self.unerase(w_dict.dstorage).getdictvalue(self.space, key)

    def setitem(self, w_dict, w_key, w_value):
        space = self.space
        if space.is_w(space.type(w_key), space.w_unicode):
            self.setitem_str(w_dict, self.space.str_w(w_key), w_value)
        else:
            raise OperationError(space.w_TypeError, space.wrap("cannot add non-string keys to dict of a type"))

    def setitem_str(self, w_dict, key, w_value):
        w_type = self.unerase(w_dict.dstorage)
        try:
            w_type.setdictvalue(self.space, key, w_value)
        except OperationError, e:
            if not e.match(self.space, self.space.w_TypeError):
                raise
            if not w_type.is_cpytype():
                raise
            # Allow cpyext to write to type->tp_dict even in the case
            # of a builtin type.
            # Like CPython, we assume that this is only done early
            # after the type is created, and we don't invalidate any
            # cache.  User code shoud call PyType_Modified().
            w_type.dict_w[key] = w_value

    def setdefault(self, w_dict, w_key, w_default):
        w_result = self.getitem(w_dict, w_key)
        if w_result is not None:
            return w_result
        self.setitem(w_dict, w_key, w_default)
        return w_default

    def delitem(self, w_dict, w_key):
        space = self.space
        w_key_type = space.type(w_key)
        if space.is_w(w_key_type, space.w_unicode):
            key = self.space.str_w(w_key)
            if not self.unerase(w_dict.dstorage).deldictvalue(space, key):
                raise KeyError
        else:
            raise KeyError

    def length(self, w_dict):
        return len(self.unerase(w_dict.dstorage).dict_w)

    def w_keys(self, w_dict):
        space = self.space
        w_type = self.unerase(w_dict.dstorage)
        return space.newlist([_wrapkey(space, key)
                              for key in w_type.dict_w.iterkeys()])

    def values(self, w_dict):
        return [unwrap_cell(self.space, w_value) for w_value in self.unerase(w_dict.dstorage).dict_w.itervalues()]

    def items(self, w_dict):
        space = self.space
        w_type = self.unerase(w_dict.dstorage)
        return [space.newtuple([_wrapkey(space, key),
                                unwrap_cell(space, w_value)])
                for (key, w_value) in w_type.dict_w.iteritems()]

    def clear(self, w_dict):
        space = self.space
        w_type = self.unerase(w_dict.dstorage)
        if not w_type.is_heaptype():
            raise oefmt(space.w_TypeError,
                        "can't clear dictionary of type '%N'", w_type)
        w_type.dict_w.clear()
        w_type.mutated(None)

    def getiterkeys(self, w_dict):
        return self.unerase(w_dict.dstorage).dict_w.iterkeys()
    def getitervalues(self, w_dict):
        return self.unerase(w_dict.dstorage).dict_w.itervalues()
    def getiteritems(self, w_dict):
        return self.unerase(w_dict.dstorage).dict_w.iteritems()
    def wrapkey(space, key):
        return _wrapkey(space, key)
    def wrapvalue(space, value):
        return unwrap_cell(space, value)

def _wrapkey(space, key):
    # keys are utf-8 encoded identifiers from type's dict_w
    return space.wrap(key.decode('utf-8'))

create_iterator_classes(DictProxyStrategy)
