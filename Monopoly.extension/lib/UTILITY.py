import random
from pyrevit import forms

def mm_to_feet(dist):
    return (int(dist) /1000) * 3.28084

def dice(luck):
    luck = int(luck)
    sample_raw = [-2, -1, 1, 2, 3, 4, 5, 6, 10]#9 item
    #sample_raw = [20]######use me to foce a dice
    #sample_raw = [4]######use me to foce a dice
    sample = []
    for item in sample_raw:
        if item < 0 and luck < 30:
            sample.extend([item]*2)
        elif item >= 5 and luck > 70:
            sample.extend([item]*2)
        else:
            sample.extend([item]*1)

    random.shuffle(sample)
    #print sample
    #weight = (20, 20, 50, 50, 50, 50, 50, 50, 10)#9 item
    #return random.choices(sample, weights = weight , k = 1)[0]
    #print "dice number = {}".format(raw_dice)
    raw_dice = random.choice(sample)
    forms.alert("dice = {}".format(raw_dice))
    return raw_dice
