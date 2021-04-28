__doc__ = "XXXXXXXXXX"
__title__ = "Reset"

from pyrevit import forms, DB, revit, script
from time import sleep
import random

from System.Collections.Generic import List

def get_marker_by_id(marker_id):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if family_name == "MAP_MARKER" and generic_model.LookupParameter("_marker_position_ID").AsInteger() == int(marker_id):
            return generic_model

def get_players():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    player_collection = []
    player_names = []
    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if _PlayerNameKeyword in family_name:
            if family_name in player_names:
                forms.alert("Should not have more than one of same {} player in game.".format(family_name))
                script.exit()
            player_collection.append(generic_model)
            player_names.append(family_name)
    return player_collection


def move_player(player, target_marker_id):
    target_marker_id = int(target_marker_id)
    initial_pt = player.Location.Point
    final_pt = get_marker_by_id(target_marker_id).Location.Point
    with revit.Transaction("temp"):
        try:
            line = DB.Line.CreateBound(initial_pt, final_pt)
            mid_pt = line.Evaluate(0.5, True)
            mid_pt_new = DB.XYZ(mid_pt.X, mid_pt.Y, mid_pt.Z + line.Length/2.0)
            arc = DB.Arc.Create(initial_pt, final_pt, mid_pt_new)
        except:#on distant too small
            player.Symbol.LookupParameter("_property_positionID").Set(target_marker_id)
            return

    step = 50
    for i in range(step + 1):
        pt_para = float(i)/step
        temp_location = arc.Evaluate(pt_para, True)


        #revit.doc.Regenerate()
        with revit.Transaction("temp"):
            player.Location.Point = temp_location
        revit.uidoc.RefreshActiveView()
        safety = 0.01#so there is never division by zero
        speed = -pt_para * (pt_para - 1) + safety#faster in middle
        pause_time = 0.25 + safety - speed# 1/4 is the peak value in normalised condition
        sleep(pause_time * 0.05)
    with revit.Transaction("temp"):
        player.Symbol.LookupParameter("_property_positionID").Set(target_marker_id)


def spot_taken(my_player):
    all_players = get_players()
    for player in all_players:
        if player.Symbol.LookupParameter("_property_name").AsString() == my_player.Symbol.LookupParameter("_property_name").AsString():
            #print "it is me"
            continue
        #print player.Location.Point,my_player.Location.Point
        if player.Location.Point.DistanceTo(my_player.Location.Point) < 2:
            #print "same spot"
            return True
    return False

def shift_player(player):
    with revit.Transaction("temp"):
        center = get_marker_by_id(-50).Location.Point
        angle = random.randrange(0,360)
        import math
        x = 3 * math.cos(angle)
        y = 3 * math.sin(angle)
        player.Location.Point = center + DB.XYZ(x, y, 0)


def reset_player(player):

    move_player(player, -50)#-50 is starter mark

    i = 0
    while spot_taken(player) or i > 100:
        #print "shifting"
        shift_player(player)
        i += 1

    with revit.Transaction("temp"):
        player.Symbol.LookupParameter("_property_hold_status").Set("Starter")
        player.Symbol.LookupParameter("_property_hold_amount").Set(1)
        player.Symbol.LookupParameter("_property_positionID").Set(-50)
        player.Symbol.LookupParameter("_property_luck").Set(50)
        player.Symbol.LookupParameter("_asset_money").Set(5000)
        player.Symbol.LookupParameter("_property_is_overweight").Set(0)
        player.Symbol.LookupParameter("_asset_direction").Set(1)
        player.Symbol.LookupParameter("_property_paycheck").Set(1000)


def reset_marker(marker):
    with revit.Transaction("reset markers"):
        marker.LookupParameter("_property_team").Set("")
        marker.LookupParameter("show_color plate").Set(0)
################## main code below #####################
_PlayerNameKeyword = "$Player_"


players = get_players()
markers = []
i = 0
while i < 200:
    if get_marker_by_id(i) != None:
        markers.append(get_marker_by_id(i))
    else:
        break
    i += 1
#print len(markers)
with revit.TransactionGroup("reset maps"):
    for player in players:
        reset_player(player)
        revit.uidoc.RefreshActiveView()


    for marker in markers:
        try:
            reset_marker(marker)
        except:
            pass
    forms.alert("All Players have been reset")
