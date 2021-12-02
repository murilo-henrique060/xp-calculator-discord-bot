MAX_LV = 30000
MAX_XP = 5063625000

def convertXpLv(xp: int) -> int:
    from math import sqrt

    try:
        xp = int(xp)
    except ValueError:
        return False

    return int((-5 + sqrt(25 - 20 * (-2 * (xp / 100))))/10) 

def convertLvXp(lv: int) -> int:
    try:
        lv = int(lv)
    except ValueError:
        return False

    return int(500 * (((lv + 1) * lv) / 2)) 

def xpMissingNxtLV(lv: int, xp: int) -> int:
    try:
        lv = int(lv)
        xp = int(xp)
    except ValueError:
        return False

    return int(convertLvXp(lv + 1) - xp) if lv < MAX_LV else False

def maxXp(xp: int) -> int:
    try:
        xp = int(xp)
    except ValueError:
        return False

    return xp if xp < MAX_XP else MAX_XP

def maxLv(lv: int) -> int:
    try:
        lv = int(lv)
    except ValueError:
        return False

    return lv if lv < MAX_LV else MAX_LV
