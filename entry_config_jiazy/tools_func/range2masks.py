import logging

def find_lsm(p, o=1):
    m = o
    i = 1
    while (True):
        if (p & m > 0):
            return m,i
        m = m << 1
        i += 1

def find_lsm2(p, o=1):
    m = o
    i = 1
    while (True):
        if (p & m == 0):
            return m,i
        m = m << 1
        i += 1

def range2masks(start, last):
    assert (0 <= start and start <= 0xFFFF)
    assert (0 <= last and last <= 0xFFFF)
    assert start < last

    masks = []
    l = 0xffff
    fp = start # From port
    tp = last # to port

    target = fp
    if (0 < fp):
        cp = fp
        i = 0
        while(True):
            cm,s = find_lsm(cp)

            e = cp | cm - 1
            m =  l & (l << s -1)
            if e > tp:
                break
            elif e == tp:
                logging.debug('Range %i - %i, finded lsm %04x, mask %04x, value %04x', cp, e, cm, m, m & cp)
                masks.append([m & cp, m])
                break

            logging.debug('Range %i - %i, finded lsm %04x, mask %04x, value %04x', cp, e, cm, m, m & cp)
            masks.append([m & cp, m])
            target = cp
            i += 1
            cp += cm

    cp = tp
    i = 0
    while(True):
        cm,s = find_lsm2(cp)

        e = cp - (cm - 1)
        m =  l & (l << s -1)
        if e < target:
            break
        elif e == target:
            logging.debug('Range %i - %i, finded lsm %04x, mask %04x, value %04x', cp, e, cm, m, m & cp)
            masks.append([m & cp, m])
            break
        logging.debug('Range %i - %i, finded lsm %04x, mask %04x, value %04x', cp, e, cm, m, m & cp)
        masks.append([m & cp, m])
        i += 1
        cp -= cm

    return masks


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    #  print "20000-25000"
    #  masks = range2masks(20000, 25000)
    #  for a in masks:
        #  print "%04x" % a[0], "%04x" % a[1]

    #  print "25-5729"
    #  masks = range2masks(0, 65535)
    #  for a in masks:
        #  print "%04x" % a[0], "%04x" % a[1]

    masks = range2masks(1025, 65535)

