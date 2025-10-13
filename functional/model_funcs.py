from functional.IndividualData import IndividualData
from functional.dimension import Dimension
from functional.general_data import GeneralData


def t(t: Dimension):
    """time"""
    return t


def num_alive(t: Dimension, general: GeneralData, individual: IndividualData):
    """probability that life is alive at time t, given alive at time 0"""
    if t == 0:
        return 1
    else:
        return num_alive(t - 1, general, individual) - num_deaths(t - 1, general, individual)


def num_deaths(t: Dimension, general: GeneralData, indidivdual: IndividualData):
    """number of deaths occuring between time t-1 and t"""
    if t < 0:
        return 0
    else:
        return num_alive(t, general, indidivdual) * q_x_m(t, general, indidivdual)


def q_x(t: Dimension, general: GeneralData, individual: IndividualData):
    """Annual mortality rate"""
    return general.tables['mort_table'].lookup(column='age', value=age(t, individual), res_col='q_x')


def q_x_m(t: Dimension, general: GeneralData, individual: IndividualData):
    """Monthly mortality rate"""
    return 1 - (1 - q_x(t, general, individual)) ** (1 / 12)


def age(t: Dimension, individual: IndividualData):
    """age in years at time t"""
    if t == 0:
        return individual.values["init_age"]
    elif t % 12 == 0:
        return age(t - 1, individual) + 1
    else:
        return age(t - 1, individual)


def expected_claim(t: Dimension, individual: IndividualData, general: GeneralData):
    return individual.values["sum_assured"] * num_deaths(t, general, individual)


def v(t: Dimension, general: GeneralData):
    """Present value factor for time t, discounting back to time 0"""
    if t == 0:
        return 1.0
    else:
        return v(t - 1, general) / (1 + general.values['disc_rate_pm'])


def pv_claim(t: Dimension, individual: IndividualData, general: GeneralData):
    """present value of the expected claim occuring at time t"""
    return expected_claim(t, individual, general) * v(t, general)
