import random
import math
from pyrevit import forms, DB, revit

def mm_to_feet(dist):
    print "mm to ft: {}-->{}".format(dist, (int(dist) /1000) * 3.28084)
    return (int(dist) /1000) * 3.28084

def feet_to_mm(dist):
    return (int(dist) /3.28084) * 1000

def get_pit():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.Family.Name == "PIT", generic_models)[0]

def get_ufo():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.Family.Name == "UFO", generic_models)[0]

def ufo_spin():
    ufo = get_ufo()
    para = ufo.LookupParameter("angle")
    angle = ( (para.AsDouble() / math.pi) * 180 + 1) % 360
    with revit.Transaction("Local Transaction"):
        para.Set(angle*math.pi/ 180)

def ufo_show_beam(ufo, boolean):
    with revit.Transaction("Local Transaction"):
        ufo.LookupParameter("show_beam").Set(boolean)

def ufo_set_transparency(ufo, amount):
    amount = int(amount)
    if amount > 100:
        amount = 100
    if amount < 0:
        amount = 0

    overridesetting = DB.OverrideGraphicSettings ().SetSurfaceTransparency(amount)
    with revit.Transaction("Local Transaction"):
        revit.active_view.SetElementOverrides (ufo.Id, overridesetting)

def dice(luck):
    luck = int(luck)
    sample_raw = [-2, -1, 1, 2, 3, 4, 5, 6, 10]#9 item
    #sample_raw = [20]######use me to foce a dice
    #sample_raw = [5]######use me to foce a dice
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
