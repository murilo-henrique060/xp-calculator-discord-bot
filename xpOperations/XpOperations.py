def convertXpLv(Xp):
    from math import sqrt

    Lv = int((-5 + sqrt(25 - 20 * (-2 * (Xp / 100))))/10)

    return Lv

def convertLvXp(Lv):
    Xp = 500 * (((Lv + 1) * Lv) / 2)

    return Xp

def xpMissingNxtLV(Lv,Xp):
    XpNxLv = int(convertLvXp(Lv + 1) - Xp)

    return XpNxLv