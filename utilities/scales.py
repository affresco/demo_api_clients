import math


def linear(lower_bound: float, upper_bound: float, steps: int):
    spacing = (upper_bound - lower_bound) / (steps)
    return [lower_bound + i * spacing for i in range(steps + 1)]


def strikes(spot: float, rounding: int = None):
    lower_bound_rel = 0.05
    upper_bound_rel = 4.00

    rounding = rounding or int(0.01 * spot)

    if rounding > 50:
        rounding = 50 * round(rounding / 50)

    if rounding <= 1.0:
        center = rounding * round(spot / rounding)
    else:
        center = round(spot)

    lower_bound = rounding * round(lower_bound_rel * spot / rounding)
    upper_bound = rounding * round(upper_bound_rel * spot / rounding)

    scale = concentrated(lower_bound=lower_bound, upper_bound=upper_bound, center=center, steps=30, rounding=rounding)
    return scale


def concentrated(lower_bound: float, upper_bound: float, steps: int, center: float = None, factor: float = 3.0,
                 rounding: int = None):
    center = center or 0.5 * (lower_bound + upper_bound)

    # Sanity check
    assert lower_bound < upper_bound

    # Center must be inside the interval
    assert lower_bound < center < upper_bound

    # Compute square root of bounds
    one_over_factor = 1.0 / factor
    sq_lower_bound_centered = (math.fabs(lower_bound - center)) ** one_over_factor
    sq_upper_bound_centered = (math.fabs(upper_bound - center)) ** one_over_factor

    # Compute steps (careful with even and odd steps)
    lower_steps = int(0.5 * steps)
    upper_steps = int(steps) - lower_steps

    # Compute spacing
    lower_spacing = sq_lower_bound_centered / lower_steps
    upper_spacing = sq_upper_bound_centered / upper_steps

    # Build a linear scale in sqrt world
    lower_sq_scale = [sq_lower_bound_centered - i * lower_spacing for i in range(lower_steps)]
    upper_sq_scale = [i * upper_spacing for i in range(upper_steps + 1)]

    # Revert to normal space
    lower_scale = [(center - i ** factor) for i in lower_sq_scale]
    upper_scale = [(center + i ** factor) for i in upper_sq_scale]

    if rounding:
        assert rounding > 0
        rounding = int(rounding)
        lower_scale = [rounding * round(i / rounding) for i in lower_scale]
        upper_scale = [rounding * round(i / rounding) for i in upper_scale]

    # Get a unique list
    scale = sorted(set(lower_scale + upper_scale))

    # Avoid numerical issues: replace with original values
    scale[0], scale[-1] = lower_bound, upper_bound
    if center not in scale:
        scale.append(center)
        scale = sorted(scale)

    return scale
