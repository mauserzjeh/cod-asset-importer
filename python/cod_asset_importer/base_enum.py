class BaseEnum(type):
    def __iter__(self):
        _attr_values = []
        _vars = vars(self)
        for _name, _value in _vars.items():
            if (
                not callable(getattr(self, _name))
                and not _name.startswith("__")
                and not _name.endswith("__")
            ):
                _attr_values.append(_value)
        return iter(_attr_values)
