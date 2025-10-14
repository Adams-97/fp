from functional.dimension import Dimension
from functional.reference import RefData


def t(t: Dimension, ref: RefData):
    """time"""
    return t


def num_alive(t: Dimension, data: RefData):
    """probability that life is alive at time t, given alive at time 0"""
    if t == 0:
        return 1
    else:
        return num_alive(t - 1, data) - num_deaths(t - 1, data)


def num_deaths(t: Dimension, data: RefData):
    """number of deaths occuring between time t-1 and t"""
    if t < 0:
        return 0
    else:
        return num_alive(t, data) * q_x_m(t, data)


def q_x(t: Dimension, data: RefData):
    """Annual mortality rate"""
    return data.tables['mort_table'].lookup(column='age', value=age(t, data), res_col='q_x')


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


def pv_claim(t: Dimension, data: RefData):
    """present value of the expected claim occuring at time t"""
    return expected_claim(t, data) * v(t, data)
