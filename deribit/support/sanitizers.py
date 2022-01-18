import sys
import math
import logging

from .types import (INSTRUMENT_KIND,
                    INSTRUMENT_CURRENCY,
                    ORDER_BOOK_GROUP,
                    ORDER_TYPE,
                    TIME_IN_FORCE,
                    TRIGGER_PRICE)

from .settings import (DEFAULT_CURRENCY,
                       DEFAULT_INTERVAL,
                       DEFAULT_KIND,
                       DEFAULT_DEPTH,
                       DEFAULT_GROUP)

# ####################################################################
# LOGGING
# ####################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ######################################################################
# SANITIZERS
# ######################################################################

def sanitize(**kwargs):
    output = {}

    fields = ["instrument",
              "instrument_name",
              "kind",
              "currency",
              "depth",
              "interval",
              "group",
              "amount",
              "max_show",
              "type",
              "time_in_force",
              "trigger",
              "advanced",
              "label",
              "limit_price",
              "stop_price",
              "post_only",
              "reduce_only",
              "count",
              "include_old",
              "order_id",
              "start_seq",
              "end_seq",
              "key_id",
              "account_id",
              "password",
              "email",
              ]

    for f in fields:
        if f in kwargs:
            method = getattr(sys.modules[__name__], "sanitize_" + f)
            output[f] = method(kwargs[f])

    return output


def sanitize_kind(kind: str = None):
    if not kind:
        return DEFAULT_KIND

    kind_ = kind.lower()
    for k in INSTRUMENT_KIND:
        if k.value == kind_:
            return kind_

    if kind_ == "options":
        print("WARNING: delta kind is singular (option, not options).")
        return "option"

    if kind_ == "futures":
        print("WARNING: delta kind is singular (future, not futures).")
        return "future"

    if kind_ == "perpetual":
        print("WARNING: delta kinds do not include 'perpetual'. Use 'future' instead.")
        return "future"

    raise Exception(f"Provided instrument kind is not acceptable ({kind}).")


def sanitize_currency(currency: str = None):
    if not currency:
        return DEFAULT_CURRENCY

    currency_ = currency.lower()

    for k in INSTRUMENT_CURRENCY:
        if k.value.lower() == currency_:
            return currency_

    raise Exception("Provided instrument currency is not acceptable.")


def sanitize_instrument(name: str = None):
    if not name:
        return None
    return name.upper()


def sanitize_instrument_name(name: str = None):
    return sanitize_instrument(name=name)


def sanitize_depth(depth=None, required=False):
    # Output cannot be none
    if not depth and required:
        return DEFAULT_DEPTH

    # Output can be none
    if not depth and not required:
        return None

    # Sanitize depth
    try:
        depth_ = int(math.fabs(depth))
        if depth_ == 0:
            return DEFAULT_DEPTH
        return depth_
    except:
        return DEFAULT_DEPTH


def sanitize_group(group=None, required=False):
    # Output cannot be none
    if not group and required:
        return DEFAULT_GROUP

    # Output can be none
    if not group and not required:
        return None

    try:
        group_ = int(group)
        values = [v.value for v in ORDER_BOOK_GROUP]

        if group_ in values:
            return group_

        if group_ > max(values):
            return max(values)

        if group_ < min(values):
            return min(values)

        else:
            prev_k = 1
            for k in values:
                if group_ < k:
                    return prev_k.value
                prev_k = k

        raise Exception("Provided order book grouping value is not acceptable.")

    except:
        return DEFAULT_GROUP


def sanitize_interval(interval_ms=None):
    if not interval_ms:
        return str(DEFAULT_INTERVAL) + "ms"

    try:
        interval_ = int(interval_ms)

        if interval_ <= 1:
            return "1ms"

        return str(interval_) + "ms"

    except:
        return str(DEFAULT_INTERVAL) + "ms"


def sanitize_amount(amount):
    # Ensure that this is a number
    amount = float(amount)

    if amount == 0.0:
        print("WARNING: Try to sanitize an order amount equals to zero.")

    if amount < 0:
        raise ValueError(f"Negative amounts are not permitted for orders.")

    return amount


def sanitize_type(type: str = None):
    if not type:
        return None

    type = type.lower()
    for k in ORDER_TYPE:
        if type == k.value.lower():
            return k.value

    raise ValueError(f"Invalid order type received {type}.")


def sanitize_time_in_force(time_in_force: str = None):
    if not time_in_force:
        return TIME_IN_FORCE.GOOD_TIL_CANCELLED.value

    time_in_force = time_in_force.lower()
    for k in ORDER_TYPE:
        if time_in_force == k.value.lower():
            return k.value

    raise ValueError(f"Invalid time in force received {time_in_force}.")


def sanitize_trigger(trigger=None):
    if not trigger:
        return TRIGGER_PRICE.INDEX.value

    trigger = trigger.lower()
    for k in TRIGGER_PRICE:
        if trigger == k.value.lower():
            return k.value

    raise ValueError(f"Invalid trigger type received for stop order {trigger}.")


def sanitize_advanced(advanced: bool = False):
    return advanced


def sanitize_label(label: str = None):
    if not label:
        return None
    else:
        return label


def sanitize_limit_price(limit_price: float = None):
    if not limit_price:
        return None

    # Ensure that this is a number
    limit_price = float(limit_price)

    if limit_price == 0.0:
        print("WARNING: Try to sanitize an limit price equals to zero.")

    if limit_price < 0:
        raise ValueError(f"Negative limit prices are not permitted for orders.")

    return limit_price


def sanitize_stop_price(stop_price: float = None):
    if not stop_price:
        return None

    # Ensure that this is a number
    stop_price = float(stop_price)

    if stop_price == 0.0:
        print("WARNING: Try to sanitize an stop price equals to zero.")

    if stop_price < 0:
        raise ValueError(f"Negative stop prices are not permitted for orders.")

    return stop_price


def sanitize_max_show(max_show: float = None):
    if not max_show:
        return None

    # Ensure that this is a number
    max_show = float(max_show)

    if max_show < 0:
        raise ValueError(f"Negative stop prices are not permitted for orders.")

    return max_show


def sanitize_post_only(post_only: bool = False):
    return post_only


def sanitize_reduce_only(reduce_only: bool = False):
    return reduce_only


def sanitize_include_old(include_old: bool = False):
    if include_old is None:
        return False
    return include_old


def sanitize_count(count: int = None):
    if not count:
        return None

    count = int(count)

    if count == 0:
        print("WARNING: Try to retrieve zero (0) old trades. Reset to default.")
        return None

    if count < 0:
        print(f"Negative count are not permitted for retrieving old trades.")
        count = math.fabs(count)
        return int(count)

    return count


def sanitize_order_id(order_id: str):
    return order_id


def sanitize_start_seq(start_seq=None):
    if not start_seq:
        return None

    if isinstance(start_seq, int) or isinstance(start_seq, float):
        if start_seq < 1:
            return 1
        else:
            return int(math.fabs(start_seq))

    try:
        return int(math.fabs(float(start_seq)))

    except:
        logging.warning(f"End sequence (end_seq) could not be parsed: {start_seq}.")
        return 1


def sanitize_end_seq(end_seq=None):
    if not end_seq:
        return None

    if isinstance(end_seq, int) or isinstance(end_seq, float):
        return int(math.fabs(end_seq))

    try:
        return int(math.fabs(float(end_seq)))

    except:
        logging.warning(f"End sequence (end_seq) could not be parsed: {end_seq}.")
        return None


def sanitize_account_id(account_id=None):
    if not account_id:
        raise ValueError(f"Account id (int) is required.")
    return int(account_id)


def sanitize_key_id(key_id=None):
    if not key_id:
        raise ValueError(f"Key id (int) is required.")
    return int(key_id)


def sanitize_password(password=None):
    if not password:
        raise ValueError(f"Password is required.")
    return str(password)


def sanitize_email(email=None):
    if not email:
        raise ValueError(f"Email is required.")
    if not "@" in str(email):
        raise ValueError(f"Invalid email format was provided.")
    return str(email)
