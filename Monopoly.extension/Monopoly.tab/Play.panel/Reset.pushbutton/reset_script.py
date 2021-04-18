__doc__ = "XXXXXXXXXX"
__title__ = "Reset"

from pyrevit import forms, DB, revit, script
from time import sleep


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
                forms.alert("Should not have more than one of same player in game.")
                script.exit()
            player_collection.append(generic_model)
            player_names.append(family_name)
    return player_collection


def move_player(player, target_marker_id):
    target_marker_id = int(target_marker_id)
    initial_pt = player.Location.Point
    final_pt = get_marker_by_id(target_marker_id).Location.Point

    line = DB.Line.CreateBound(initial_pt, final_pt)
    mid_pt = line.Evaluate(0.5, True)
    mid_pt_new = DB.XYZ(mid_pt.X, mid_pt.Y, mid_pt.Z + line.Length/2.0)
    arc = DB.Arc.Create(initial_pt, final_pt, mid_pt_new)

    step = 50
    for i in range(step + 1):
        pt_para = float(i)/step
        temp_location = arc.Evaluate(pt_para, True)
        player.Location.Point = temp_location

        revit.doc.Regenerate()
        revit.uidoc.RefreshActiveView()
        safety = 0.01#so there is never division by zero
        speed = -pt_para * (pt_para - 1) + safety#faster in middle
        pause_time = 0.25 + safety - speed# 1/4 is the peak value in normalised condition
        sleep(pause_time * 0.05)
    player.Symbol.LookupParameter("_property_positionID").Set(target_marker_id)

def reset_player(player):
    try:
        move_player(player, -50)
    except:
        pass

    player.Symbol.LookupParameter("_property_hold_status").Set("Starter")
    player.Symbol.LookupParameter("_property_hold_amount").Set(1)
    player.Symbol.LookupParameter("_property_positionID").Set(-50)
    player.Symbol.LookupParameter("_property_luck").Set(50)
    player.Symbol.LookupParameter("_asset_money").Set(1000)
    player.Symbol.LookupParameter("_property_is_overweight").Set(0)
    player.Symbol.LookupParameter("_asset_direction").Set(1)


################## main code below #####################
_PlayerNameKeyword = "$Player_"


players = get_players()
with revit.Transaction("reset players"):
    for player in players:
        reset_player(player)

    forms.alert("All Players have been reset")
