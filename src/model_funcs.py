import functools

from src.lib.dimension import Dimension
from src.lib.reference import RefData
from src.lib.registry import register_func_group


@register_func_group('a')
def t(t: Dimension, ref: RefData):
    """time"""
    return t


@register_func_group('b')
def num_alive(t: Dimension, data: RefData):
    """probability that life is alive at time t, given alive at time 0"""
    if t == 0:
        return 1
    else:
        return num_alive(t - 1, data) - num_deaths(t - 1, data)


@register_func_group('a')
def num_deaths(t: Dimension, data: RefData):
    """number of deaths occuring between time t-1 and t"""
    if t < 0:
        return 0
    else:
        return num_alive(t, data) * q_x_m(t, data)


@register_func_group('c')
def q_x(t: Dimension, data: RefData):
    """Annual mortality rate"""
    return data.tables['mort_table'].lookup(index_values={'age': age(t, data)}, return_col='q_x')


@register_func_group('b')
def q_x_m(t: Dimension, data: RefData):
    """Monthly mortality rate"""
    return 1 - (1 - q_x(t, data)) ** (1 / 12)


def age(t: Dimension, data: RefData):
    """age in years at time t"""
    if t == 0:
        return data.values["init_age"]
    elif t % 12 == 0:
        return age(t - 1, data) + 1
    else:
        return age(t - 1, data)


def expected_claim(t: Dimension, data: RefData):
    return data.values["sum_assured"] * num_deaths(t, data)


def v(t: Dimension, data: RefData):
    """Present value factor for time t, discounting back to time 0"""
    if t == 0:
        return 1.0
    else:
        return v(t - 1, data) / (1 + data.values['disc_rate_pm'])


@functools.lru_cache(maxsize=None)
def pv_claim(t: Dimension, data: RefData):
    """present value of the expected claim occuring at time t"""
    return expected_claim(t, data) * v(t, data)