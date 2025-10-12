from context import Ctx

def t(t):
    """time"""
    return t


def num_alive(t, ctx: Ctx):
    """probability that life is alive at time t, given alive at time 0"""
    if t == 0:
        return 1
    else:
        return num_alive(t - 1, ctx) - num_deaths(t - 1, ctx)  # deaths moved to a separate method


def num_deaths(t, ctx: Ctx):
    """number of deaths occuring between time t-1 and t"""
    if t < 0:
        return 0
    else:
        return num_alive(t, ctx) * q_x_m(t, ctx)


def q_x(t, ctx: Ctx):
    """Annual mortality rate"""
    return ctx.general_ref_data['mort_table'].lookup(column='age', value=age(t, ctx), res_col='q_x')


def q_x_m(t, ctx: Ctx):
    """Monthly mortality rate"""
    return 1 - (1 - q_x(t, ctx)) ** (1 / 12)


def age(t, ctx: Ctx):
    """age in years at time t"""
    if t == 0:
        return ctx.general_ref_data["init_age"]
    elif t % 12 == 0:
        return age(t - 1, ctx) + 1
    else:
        return age(t - 1, ctx)


def expected_claim(t, ctx: Ctx):
    return ctx.general_ref_values["sum_assured"] * num_deaths(t, ctx)


def v(t, ctx: Ctx):
    """Present value factor for time t, discounting back to time 0"""
    if t == 0:
        return 1.0
    else:
        return v(t - 1, ctx) / (1 + ctx.general_ref_values['disc_rate_pm'])


def pv_claim(t, ctx: Ctx):
    """present value of the expected claim occuring at time t"""
    return expected_claim(t, ctx) * v(t, ctx)
