from math import floor, sqrt
from decouple import config

MAX_LV = config('MAX_LV', cast=int)
MAX_XP = config('MAX_XP', cast=int)

def lv_to_xp(lv:int, xp_per_level:int = 500) -> int:
    """Convert a level to the corresponding XP amount."""
    return floor((xp_per_level  * (lv ** 2 + lv)) / 2)

def xp_to_lv(xp:int, max_level:int, xp_per_level:int = 500) -> int:
    """Convert an XP amount to the corresponding level."""
    return min(max_level, floor((- xp_per_level + sqrt(xp_per_level * (xp_per_level + 8 * xp))) / (2 * xp_per_level)))

def xp_nxt_lv(xp:int, max_level:int, xp_per_level:int = 500) -> int:
    """Calculate the XP amount needed to reach the next level."""
    return lv_to_xp(xp_to_lv(xp, max_level, xp_per_level) + 1, xp_per_level) - xp