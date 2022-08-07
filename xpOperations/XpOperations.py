from decouple import config

MAX_LV = config('MAX_LV', cast=int)
MAX_XP = config('MAX_XP', cast=int)

def convertXpLv(xp: int) -> int:
    from math import sqrt

    try:
        xp = int(xp)
    except ValueError:
        return False

    return min(int((-5 + sqrt(25 - 20 * (-2 * (xp / 100))))/10), MAX_LV)

def convertLvXp(lv: int) -> int:
    try:
        lv = int(lv)
    except ValueError:
        return False

    return min(int(500 * (((lv + 1) * lv) / 2)), MAX_XP)

def xpMissingNxtLV(lv: int, xp: int) -> int:
    try:
        lv = int(lv)
        xp = int(xp)
    except ValueError:
        return False

    return int(convertLvXp(lv + 1) - xp) if lv < MAX_LV else 0

def maxXp(xp: int) -> int:
    try:
        xp = int(xp)
    except ValueError:
        return False

    return min(xp, MAX_XP)

def maxLv(lv: int) -> int:
    try:
        lv = int(lv)
    except ValueError:
        return False

    return min(lv, MAX_LV)
