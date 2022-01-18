from decorator import decorator

def to_list(x) -> list:
    if not isinstance(x, list):
        return [x]
    return x


def to_bool(v: str) -> bool:
    if isinstance(v, bool):
        return v
    return v.lower() in ("yes", "true", "t", "1")


def args_to_list(**deco_kwargs):

    def _parse_arguments_into_list(func, *args, **kwargs):
        to_list_pos = list(deco_kwargs.values())
        tmp = [val if pos not in to_list_pos else to_list(val) for pos, val in enumerate(args)]
        new_args = tuple(tmp)
        return func(*new_args, **kwargs)

    return decorator(_parse_arguments_into_list)

def str2bool(v):
    if isinstance(v, bool):
        return v
    return v.lower() in ("yes", "true", "t", "1")
