#!/bin/env python3

def assignIntervals(container, leftGetter, rightGetter):
    intervals = []
    for (i, el) in enumerate(container):
        intervals.append((leftGetter(el), rightGetter(el), i))
    intervals = sorted(intervals)
    if len(intervals) == 0:
        return [[]]
    slots = [[intervals[0]]]
    for it in intervals[1:]:
        place_found = None
        max_smaller = None
        for place in range(len(slots)):
            right_edge_of_slot = slots[place][-1][1]
            if max_smaller != None and max_smaller >= right_edge_of_slot:
                continue
            if right_edge_of_slot <= it[0]:
                place_found = place
                max_smaller = right_edge_of_slot
        if place_found != None:
            slots[place_found].append(it)
        else:
            slots.append([it])
    return slots

def rearrangeIntervals(its, priorityGetter):
    if len(its) == 0: return its
    its = sorted(its, key = lambda ints: (0, min([priorityGetter(it) for it in ints])) if len(ints)>0 else (-1,0))
    return its

def widenIntervals(its):
    # its: a return value of assignIntervals
    def intersectsSlot(interval, slot):
        for w in its[slot]:
            if interval[1] > w[0] and interval[0] < w[1]:
                return True
        return False
    def findLastSlotFor(interval, slot):
        lastSlot = slot + 1
        while lastSlot < len(its) and not intersectsSlot(interval, lastSlot):
            lastSlot += 1
        return lastSlot - 1
    def findFirstSlotFor(interval, slot):
        firstSlot = slot - 1
        while firstSlot >= 0 and not intersectsSlot(interval, firstSlot):
            firstSlot -= 1
        if firstSlot == -1:
            return 0
        return slot
    ret = {"max_slots" : len(its)}
    data = []
    for slot, intervals in enumerate(its):
        for inte in intervals:
            lastSlot = findLastSlotFor(inte, slot)
            firstSlot = findFirstSlotFor(inte, slot)
            data.append({"interval" :inte, "slot": firstSlot, "lastSlot": lastSlot})
    ret["intervals"] = sorted(data, key = lambda x : (x["interval"][0], x["slot"]))
    return ret
            
        
    
                        
def test_interv():
    its = assignIntervals([(800, 900), (830, 930), (900, 1990), (900,1030), (1100, 1200), (920, 1300)],
                          lambda el : el[0],
                          lambda el : el[1])
    assert(its == [[(800, 900, 0), (900, 1030, 3), (1100, 1200, 4)], [(830, 930, 1)], [(900, 1990, 2)], [(920, 1300, 5)]])
    wi = widenIntervals(its)
    assert(wi == {'max_slots': 4, 'intervals': [{'interval': (800, 900, 0), 'slot': 0, 'lastSlot': 0}, {'interval': (830, 930, 1), 'slot': 1, 'lastSlot': 1},
                                                {'interval': (900, 1030, 3), 'slot': 0, 'lastSlot': 0}, {'interval': (900, 1990, 2), 'slot': 2, 'lastSlot': 2},
                                                {'interval': (920, 1300, 5), 'slot': 3, 'lastSlot': 3}, {'interval': (1100, 1200, 4), 'slot': 0, 'lastSlot': 1}]})

"""
its = assignIntervals([(800, 900), (830, 930), (900, 1990), (900,1030), (1100, 1200), (920, 1300)],
                      lambda el : el[0],
                      lambda el : el[1])

print(its)
print(widenIntervals(its))
"""
