import inspect

class DecoratableObject(object):
    MODE_OVERRIDE = 0
    MODE_PARAMS = 1
    MODE_RESULT = 2

    def __init__(self, fn, is_method=False):
        self._callable = fn
        self.is_method = is_method

        self._params_decoration = None
        self._result_decoration = None

    def _decorate(self, fn, mode, **kwargs):
        if mode == self.MODE_OVERRIDE:
            self._decorate_full(fn, **kwargs)
        elif mode == self.MODE_PARAMS:
            self._decorate_params(fn)
        elif mode == self.MODE_RESULT:
            self._decorate_result(fn, **kwargs)

    def _decorate_full(self, fn, needs_origin=True):
        origin = self._callable

        if needs_origin:
            if self.is_method:
                self._callable = lambda inst, *args, **kwargs: fn(inst, origin, *args, **kwargs)
            else:
                self._callable = lambda *args, **kwargs: fn(origin, *args, **kwargs)
        else:
            self._callable = fn

    def _decorate_params(self, fn):
        if not self._params_decoration:
            self._params_decoration = []

        self._params_decoration.append(fn)

    def _decorate_result(self, fn, needs_params=False):
        if not self._result_decoration:
            self._result_decoration = []

        fn._needs_params = needs_params
        self._result_decoration.append(fn)

    def __call__(self, *args, **kwargs):
        if self._params_decoration:
            for dec in self._params_decoration:
                try:
                    args, kwargs = dec(*args, **kwargs)
                except ReturnImediatelyException, e:
                    return e.ret

        res = self._callable(*args, **kwargs)

        if self._result_decoration:
            for dec in self._result_decoration:
                if dec._needs_params:
                    res = dec(res, *args, **kwargs)
                else:
                    res = dec(res)

        return res

class ReturnImediatelyException(Exception):
    def __init__(self, ret):
        super(Exception, self).__init__()
        self.ret = ret

def _check_decoratable(origin, install=True):
    if not hasattr(origin, '_decoratable_obj'):
        if inspect.ismethod(origin) and not hasattr(origin, '_decoratable_obj'):
            decoratable = DecoratableObject(origin)

            def decoratable_method(self, *args, **kwargs):
                return decoratable(self, *args, **kwargs)

            decoratable_method._decoratable_obj = decoratable

            def decoratable_decorate(fn, mode, **kwargs):
                decoratable._decorate(fn, mode, **kwargs)

            decoratable_method._decorate = decoratable_decorate

            if install:
                setattr(origin.im_class, origin.__name__, decoratable_method)

            return decoratable_method
                
        elif inspect.isfunction(origin):
            decoratable = DecoratableObject(origin)

            def decorated(*args, **kwargs):
                return decoratable(*args, **kwargs)

            decorated._decoratable_obj = decoratable

            if install:
                setattr(inspect.getmodule(origin), origin.__name__, decorated)

            decorated.__name__ = origin.__name__
            decorated.__module__ = origin.__module__

            return decorated

    return origin


def decorate(origin, needs_origin=True):
    origin = _check_decoratable(origin)

    def decorator(fn):
        origin._decoratable_obj._decorate(fn, DecoratableObject.MODE_OVERRIDE, needs_origin=needs_origin)
        
    return decorator


def _decorate_params(origin):
    origin = _check_decoratable(origin)

    def decorator(fn):
        origin._decoratable_obj._decorate(fn, DecoratableObject.MODE_PARAMS)

    return decorator

decorate.params = _decorate_params

def _decorate_result(origin, needs_params=False):
    origin = _check_decoratable(origin)

    def decorator(fn):
        origin._decoratable_obj._decorate(fn, DecoratableObject.MODE_RESULT, needs_params=needs_params)

    return decorator

decorate.result = _decorate_result

def _decorate_with(fn):
    def decorator(origin):
        origin = _check_decoratable(origin)
        origin._decoratable_obj._decorate(fn, DecoratableObject.MODE_OVERRIDE, needs_origin=True)
        return origin
    return decorator

decorate.withfn = _decorate_with

def _decorate_result_with(fn, needs_params=False):
    def decorator(origin):
        origin = _check_decoratable(origin)
        origin._decoratable_obj._decorate(fn, DecoratableObject.MODE_RESULT, needs_params=needs_params)
        return origin
    return decorator

decorate.result.withfn = _decorate_result_with

def _decorate_params_with(fn):
    def decorator(origin):
        origin = _check_decoratable(origin)
        origin._decoratable_obj._decorate(fn, DecoratableObject.MODE_PARAMS)
        return origin
    return decorator

decorate.params.withfn = _decorate_params_with