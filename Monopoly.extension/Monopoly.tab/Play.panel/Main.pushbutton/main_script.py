__doc__ = "XXXXXXXXXX"
__title__ = "Move"

from pyrevit import forms, DB, revit, script
from time import sleep
import random
import CAMERA
from System.Collections.Generic import List
#!/usr/bin/env python
# coding=utf-8
def feet_to_mm(dist):
    return (dist/3.28084)*1000

def mm_to_feet(dist):
    return (dist /1000) * 3.28084

def dice(luck):
    luck = int(luck)
    sample_raw = [-2, -1, 1, 2, 3, 4, 5, 6, 10]#9 item
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

def find_max_marker_id_on_map():
    safety = 100
    counter = 0
    while counter < safety:
        if get_marker_by_id(counter + 1) == None:
            return counter
        counter += 1

def get_pit():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if family_name == "PIT":
            return generic_model

def get_marker_by_id(marker_id):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if family_name == "MAP_MARKER" and generic_model.LookupParameter("_marker_position_ID").AsInteger() == int(marker_id):
            return generic_model

def get_random_event_card(luck):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    random.shuffle(generic_models)
    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if family_name == "CARD":
            if luck - 50 < generic_model.LookupParameter("_property_luck").AsInteger() < luck + 50:
                return generic_model

def get_material_by_name(name):
    all_materials = DB.FilteredElementCollector(revit.doc).OfClass(DB.Material).WhereElementIsNotElementType().ToElements()
    for material in all_materials:
        #print material.Name
        if material.Name == name:
            return material

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

def pick_player(players):
    names = [get_player_name(x) for x in players]
    name = forms.SelectFromList.show(names, title = "Pick your player!", button_name='Go!')
    player = get_player_by_name(name, players)
    if player == None:
        script.exit()
    else:
        return player

def move_player(agent, target_marker_id):
    player = agent.model
    target_marker_id = int(target_marker_id)
    initial_pt = player.Location.Point
    final_pt = get_marker_by_id(target_marker_id).Location.Point
    line = DB.Line.CreateBound(initial_pt, final_pt)
    mid_pt = line.Evaluate(0.5, True)
    mid_pt_new = DB.XYZ(mid_pt.X, mid_pt.Y, mid_pt.Z + line.Length/2.0)
    arc = DB.Arc.Create(initial_pt, final_pt, mid_pt_new)
    #pt_list = List[DB.XYZ]([])
    #spline = DB.NurbSpline.Create()
    #DB.CurveElement.SetGeometryCurve(arc, False)

    step = 15
    for i in range(step + 1):
        pt_para = float(i)/step
        temp_location = arc.Evaluate(pt_para, True)
        #print temp_location.Z
        #temp_location = line.Evaluate(pt_para, True)
        player.Location.Point = temp_location
        #perspective_view = CAMERA.get_view_by_name("$Camera_Main", revit.doc)
        #CAMERA.update_camera(perspective_view, temp_location)

        safety = 0.01#so there is never division by zero
        speed = -pt_para * (pt_para - 1) + safety#faster in middle
        pause_time = 0.25 + safety - speed# 1/4 is the peak value in normalised condition
        sleep(pause_time * _SpeedFactor)
        revit.doc.Regenerate()
        revit.uidoc.RefreshActiveView()
        #revit.uidoc.UpdateAllOpenViews()

    player.Symbol.LookupParameter("_property_positionID").Set(target_marker_id)
    agent.position_id = target_marker_id

def get_player_name(player):
    family_name = player.Symbol.Family.Name
    player_family_name = family_name.split(_PlayerNameKeyword)[1]
    """
    print player_family_name
    print "!!!!"
    for para in player.Symbol.Parameters:
        print para.Definition.Name
    print "####"
    """
    player_user_name = player.Symbol.LookupParameter("_property_name").AsString()
    player_name = "{}[{}]".format(player_user_name,player_family_name)
    return player_name

def get_player_by_name(name, players):
    for player in players:
        if name == get_player_name(player):
            return player

def get_marker_description(marker):
    return marker.LookupParameter("_marker_event_description").AsString()

def get_marker_data(marker):
    return marker.LookupParameter("_marker_event_data").AsString()

def get_marker_title(marker):
    return marker.LookupParameter("_marker_event_title").AsString()

def get_marker_team(marker):
    return marker.LookupParameter("_property_team").AsString()


class player_agent:
    def __init__(self, generic_model):
        self.model = generic_model
        self.name = generic_model.Symbol.LookupParameter("_property_name").AsString()
        self.team = generic_model.Symbol.LookupParameter("_property_team").AsString()
        self.hold_status = generic_model.Symbol.LookupParameter("_property_hold_status").AsString()
        self.hold_amount = generic_model.Symbol.LookupParameter("_property_hold_amount").AsInteger()
        self.position_id = generic_model.Symbol.LookupParameter("_property_positionID").AsInteger()
        self.luck = generic_model.Symbol.LookupParameter("_property_luck").AsInteger()
        self.money = generic_model.Symbol.LookupParameter("_asset_money").AsInteger()
        self.is_overweight = generic_model.Symbol.LookupParameter("_property_is_overweight").AsInteger()
        self.direction = generic_model.Symbol.LookupParameter("_asset_direction").AsInteger()

    def DO_NOT_USE_update_position_id(self, id):
        self.model.Symbol.LookupParameter("_property_positionID").Set(id)

    def update_money(self, amount):
        current_money = self.model.Symbol.LookupParameter("_asset_money").AsInteger()
        self.model.Symbol.LookupParameter("_asset_money").Set(current_money + int(amount))

    def update_luck(self, amount):
        self.model.Symbol.LookupParameter("_property_luck").Set(self.luck + int(amount))

    def update_weight(self, data):
        self.model.Symbol.LookupParameter("_property_is_overweight").Set(int(data))

    def update_hold(self):
        current_hold_location = self.model.Symbol.LookupParameter("_property_hold_status").AsString()
        current_hold_amount = self.model.Symbol.LookupParameter("_property_hold_amount").AsInteger()
        if current_hold_location == None:
            current_hold_location = " holder place"

        #print "&&&&", current_hold_amount
        if current_hold_amount > 0:
            if current_hold_amount - 1 == 0:
                additiontal_note = "You will free at next round."
            else:
                additiontal_note = ""

            forms.alert("Currently staying in {}\n{} round remains.\n{}".format(current_hold_location, current_hold_amount - 1, additiontal_note))
            self.model.Symbol.LookupParameter("_property_hold_amount").Set(current_hold_amount - 1)
            if current_hold_location == "Hospital":
                forms.alert("Hospital Bill: $500")
                self.update_money(-500)

        else:
            forms.alert("You are free from {}".format(current_hold_location))
            if self.is_overweight:
                self.model.Symbol.LookupParameter("_property_is_overweight").Set(0)
                self.is_overweight = False
                forms.alert("Doctor cured your overweight")
            self.model.Symbol.LookupParameter("_property_hold_status").Set("")
            self.model.Symbol.LookupParameter("_property_hold_amount").Set(0)
            current_marker = get_marker_by_id(self.position_id)
            description = get_marker_description(current_marker)
            data = get_marker_data(current_marker)
            if "*exit*" in description:

                self.hold_amount = 0
                #update_position_id(data)
                #self.position_id = int(data)
                move_player(self, data)

    def update_pit(self):
        depth = self.model.Symbol.LookupParameter("_property_hold_amount").AsInteger()
        raw_dice = dice(self.luck)
        if raw_dice >= depth:
            self.hold_amount = 0
            self.model.Symbol.LookupParameter("_property_hold_status").Set("")
            self.model.Symbol.LookupParameter("_property_hold_amount").Set(0)
            forms.alert("it is your lucky day.\nYou only need {} to get out.".format(depth))

            #roll_dice(self)
        elif raw_dice < 0 and self.is_overweight:
            depth += 1
            forms.alert("you are too heavy, floor collaspe while jumping. \nThe pit is now {}m deep.".format(depth))
            self.model.Symbol.LookupParameter("_property_hold_amount").Set(depth)
            pit_marker = get_marker_by_id(self.position_id)
            pit_marker.LookupParameter("_marker_event_data").Set(str(depth))
            pit = get_pit()
            pit.LookupParameter("depth").Set(int(depth))
        else:
            forms.alert("you need {} or more, maybe next day.".format(depth))

        self.model.LookupParameter("Elevation from Level").Set(-mm_to_feet(depth * 1000))


    def flip_direction(self):
        current_direction = self.model.Symbol.LookupParameter("_asset_direction").AsInteger()
        self.model.Symbol.LookupParameter("_asset_direction").Set(current_direction * -1)

    def send_to_prison(self, hold_amount):

        move_player(self, -200)#100 is the id for hospital
        self.model.Symbol.LookupParameter("_property_hold_status").Set("Prison")
        self.model.Symbol.LookupParameter("_property_hold_amount").Set(int(hold_amount))

    def send_to_hospital(self, hold_amount):

        move_player(self, -100)#100 is the id for hospital
        forms.alert("Hospital Bill: $500")
        self.update_money(-500)
        self.model.Symbol.LookupParameter("_property_hold_status").Set("Hospital")
        self.model.Symbol.LookupParameter("_property_hold_amount").Set(int(hold_amount))

    def hold_in_place(self, hold_amount):
        self.model.Symbol.LookupParameter("_property_hold_status").Set("In Place")
        self.model.Symbol.LookupParameter("_property_hold_amount").Set(int(hold_amount))

    def hold_in_pit(self, depth):
        print depth
        self.model.Symbol.LookupParameter("_property_hold_status").Set("Pit")
        self.model.Symbol.LookupParameter("_property_hold_amount").Set(int(depth))
        forms.alert("The pit is {}m deep, you will need to roll {} or more to get out.".format(depth))
        self.model.LookupParameter("Elevation from Level").Set(-mm_to_feet(depth * 1000))

    def process_event(self, title, description, data):

        if title != "none":
            forms.alert("{}".format(title))

        if "*hospital*" in description:
            hold_amount = data
            self.send_to_hospital(hold_amount)
        if "*prison*" in description:
            hold_amount = data
            self.send_to_prison(hold_amount)
        if "*hold in place*" in description:
            hold_amount = data
            self.hold_in_place(hold_amount)
        if "*money*" in description:
            self.update_money(data)
        if "*walk*" in description:
            new_position_id = self.position_id + self.direction * int(data)
            move_player(self, new_position_id)
            #self.position_id = new_position_id
        if "*flip direction*" in description:
            self.flip_direction()
        if "*pit*" in description:
            self.hold_in_pit(data)

        if "*transfer*" in description:
            forms.alert("Intersection Point, switch road.")
            move_player(self, data)
        if "*luck*" in description:
            self.update_luck(data)

        if "*overweight*" in description:
            self.update_weight(data)

        if "*exchange team*" in description:
            self.exchange_team(data)

        if "*exchange money*" in description:
            self.exchange_money(data)

        if "*exchange position*" in description:
            self.exchange_position(data)



    def exchange_position(self, data):
        other = get_player_by_richness(data)

        if self.name == other.name:
            annouce_name_by_richness(data)
            return
        else:
            forms.alert("Exchanging with {}".format(other.name))

        my_id, other_id = other.position_id, self.position_id
        try:
            move_player(self, other_id)
            move_player(other, my_id)
        except:
            forms.alert("On same spot.")


    def exchange_money(self, data):
        other = get_player_by_richness(data)

        if self.name == other.name:
            annouce_name_by_richness(data)
            return
        else:
            forms.alert("Exchanging with {}".format(other.name))

        my_money, other_money = other.money, self.money
        self.model.Symbol.LookupParameter("_asset_money").Set( other_money)
        other.model.Symbol.LookupParameter("_asset_money").Set( my_money  )

    def exchange_team(self, data):
        other = get_player_by_richness(data)

        if self.name == other.name:
            annouce_name_by_richness(data)
            return
        else:
            forms.alert("Exchanging with {}".format(other.name))

        my_team, other_team = other.team, self.team

        self.model.Symbol.LookupParameter("_property_team").Set( other_team )
        other.model.Symbol.LookupParameter("_property_team").Set( my_team )
        self.model.Symbol.LookupParameter("mat.").Set( get_material_by_name(other_team).Id )
        other.model.Symbol.LookupParameter("mat.").Set( get_material_by_name(my_team).Id )

def annouce_name_by_richness(data):
    if data == "rich":
        return "Wow! you are the richest"
    elif data == "poor":
        return "Shame! You are the poorest!"


def get_player_by_richness(data):
    ranked_players = sorted(get_players(), key = lambda x: x.Symbol.LookupParameter("_asset_money").AsInteger())
    if data == "rich":
        return player_agent(ranked_players[-1])
    else:
        return player_agent(ranked_players[0])

def roll_dice(agent):
    raw_dice = dice(agent.luck)#this can be the dice
    if raw_dice < 0:
        dice_direction = -1
    else:
        dice_direction = 1
    total_step = abs(raw_dice)

    for step in range(total_step):
        if agent.is_overweight and step == 4:
            forms.alert("Overweight, too tied")
            agent.hold_in_place(1)
            break


        try:
            new_position_id = agent.position_id + agent.direction * dice_direction
            move_player(agent, new_position_id)

        except:#reach max position, return to zero
            if agent.direction * dice_direction  == 1:
                new_position_id = 0
            else:
                new_position_id = _MaxMarkerID
            #print new_position_id
            move_player(agent, new_position_id)


        current_marker = get_marker_by_id(new_position_id)
        marker_title = get_marker_title(current_marker)
        marker_description = get_marker_description(current_marker)
        marker_data = get_marker_data(current_marker)
        #print marker_description, marker_data
        if "*payday*" in marker_description:

            agent.update_money(marker_data)
            forms.alert("Passing Payday.\nGetting ${}.".format(marker_data))
    #print "current_position_id = {}".format(new_position_id)
    #agent.update_position_id(new_position_id)
    if "*random event*" in marker_description:
        event_card = get_random_event_card(agent.luck)

        card_title = get_marker_title(event_card)
        card_description = get_marker_description(event_card)
        card_data = get_marker_data(event_card)

        agent.process_event(card_title, card_description, card_data)
    else:
        agent.process_event(marker_title, marker_description, marker_data)


    if get_marker_title(current_marker) == "none":
        if get_marker_team(current_marker) == "":
            #print "buy new land"
            purchase_new_land(current_marker, agent)
        elif get_marker_team(current_marker) == agent.team:
            #print "upgrade my team land"
            upgrade_land(current_marker, agent)
        else:
            #print "pay land"
            pay_land(current_marker, agent)


def upgrade_land(marker, agent):
    price = marker.LookupParameter("_land_value").AsInteger()
    new_price = int(price * 1.5)
    decision = forms.alert(msg = "Want to upgrade your team land?", options = ["Yes, pay ${}".format(new_price),\
                                                                                "No."])
    if decision == None or "No" in decision:
        return

    agent.update_money(- new_price)
    marker.LookupParameter("_land_value").Set( new_price)
    marker.LookupParameter("_land_value_text_display").Set("${}".format(new_price))

def team_share_money(team, money):

    team_players_models = filter(lambda x: x.Symbol.LookupParameter("_property_team").AsString() == team, get_players())
    team_players_agents = map(lambda x: player_agent(x), team_players_models)
    #print team_players_agents, team_players_models
    forms.alert( "everyone on {} will get ${}".format(team, money/len(team_players_agents))  )
    map(lambda x: x.update_money(money/len(team_players_agents)), team_players_agents)


def pay_land(marker, agent):
    price = marker.LookupParameter("_land_value").AsInteger()
    team = get_marker_team(marker)
    agent.update_money(-price)
    forms.alert("Paying {} ${}".format(team, price))
    team_share_money(team, price)#make them evenly share the amount pay

    """
    decision = forms.alert(msg = "Do you want to buy it over to your team?", options = ["Yes, pay ${}".format(price * 1.5),\
                                                                                    "No."])
    """

def purchase_new_land(marker, agent):
    decision = forms.alert(msg = "Land available, do you want to buy it?", options = ["Yes, pay $1000",\
                                                                                        "No."])
    if decision == None or "No" in decision:
        return
    inital_price = 1000
    agent.update_money(-inital_price)

    marker.LookupParameter("_property_team").Set(agent.team)
    marker.LookupParameter("color plate mat.").Set(get_material_by_name(agent.team).Id)
    marker.LookupParameter("show_color plate").Set(1)
    marker.LookupParameter("_land_value").Set(inital_price)
    marker.LookupParameter("_land_value_text_display").Set("${}".format(inital_price))


def play_this_player(player):
    player_name = get_player_name(player)
    forms.alert( "Time for {}".format(player_name)  )

    #current_view = revit.doc.ActiveView
    #CAMERA.switch_view_to("$Camera_Main", revit.doc)
    #revit.uidoc.RefreshActiveView()
    """
    with revit.Transaction("redraw views"):
        CAMERA.zoom_to_player(player)
        revit.doc.Regenerate()
        revit.uidoc.RefreshActiveView()
        revit.uidoc.UpdateAllOpenViews()

        sleep(1)
    """

    with revit.Transaction("Make Move for '{}'".format(player_name)):
        agent = player_agent(player)
        if agent.hold_status != "":
            if agent.hold_status == "Pit":
                agent.update_pit()
            elif agent.hold_status == "Starter":
                raw_dice = dice(agent.luck)
                if raw_dice >= 5:
                    move_player(agent, 1)
                    agent.model.Symbol.LookupParameter("_property_hold_status").Set("")
                    agent.model.Symbol.LookupParameter("_property_hold_amount").Set(0)
                    agent.hold_amount = 0
                    agent.hold_status = ""
                    #agent.position_id = 1
                else:
                    forms.alert("You need 5 or more to move on.")
            else:
                #print "update hold"
                agent.update_hold()

        #after those update above, you want to recheck the hold amount and move dice
        if agent.hold_amount == 0:
            roll_dice(agent)


    #CAMERA.switch_view_to("BATTLE GROUND", revit.doc)



################## main code below #####################
_PlayerNameKeyword = "$Player_"
_MaxMarkerID = find_max_marker_id_on_map()
#print _MaxMarkerID
_SpeedFactor = 0.005#speed factor, 0.01 = less wait = faster, 0.5 = longer wait time = slow

output = script.get_output()
killtime = 100
output.self_destruct(killtime)

players = get_players()

"""
player = pick_player(players)
play_this_player(player)
"""

map(play_this_player, players)






"""
DisplacementElement class


"""
########note to self to research
#GUI window?
#how did select from para window show extra icon  instance/type by list?
#try to search from directory the name used for revit tab manager?

"""
from datetime import date
print date.today()
"""


"""
FREQUENTLY_SELECTED_CATEGORIES = [
    DB.BuiltInCategory.OST_Areas,
    DB.BuiltInCategory.OST_AreaTags,
    DB.BuiltInCategory.OST_AreaSchemeLines,
    DB.BuiltInCategory.OST_Columns,
    DB.BuiltInCategory.OST_StructuralColumns,
    DB.BuiltInCategory.OST_Dimensions,
    DB.BuiltInCategory.OST_Doors,
    DB.BuiltInCategory.OST_Floors,
    DB.BuiltInCategory.OST_StructuralFraming,
    DB.BuiltInCategory.OST_Furniture,
    DB.BuiltInCategory.OST_Grids,
    DB.BuiltInCategory.OST_Rooms,
    DB.BuiltInCategory.OST_RoomTags,
    DB.BuiltInCategory.OST_CurtainWallPanels,
    DB.BuiltInCategory.OST_Walls,
    DB.BuiltInCategory.OST_Windows,
    DB.BuiltInCategory.OST_Ceilings,
    DB.BuiltInCategory.OST_SectionBox,
    DB.BuiltInCategory.OST_ElevationMarks,
    DB.BuiltInCategory.OST_Parking
]
"""



"""
keynotes = DB.FilteredElementCollector(revit.doc,revit.active_view.Id)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()
"""

"""# ICollections format: System.Collections.Generic.List[DB.date type]([list data])
    shapes = [shapes list]
    shape_collection = System.Collections.Generic.List[DB.ElementId]([x.Id for x in shapes])
    revit.active_view.IsolateElementsTemporary(shape_collection)
"""

"""##Rhino - Rhino3dmIO

Rhino3dmIO is a subset of RhinoCommon and it gives you access to openNurbs, allowing you to, amongst other things, read and write 3dm files.
>>> from rpw.extras.rhino import Rhino as rc
>>> pt1 = rc.Geometry.Point3d(0,0,0)
>>> pt2 = rc.Geometry.Point3d(10,10,0)
>>> line1 = rc.Geometry.Line(pt1, pt2)
>>> line1.Length
14.142135623730951
>>>
>>> pt1 = rc.Geometry.Point3d(10,0,0)
>>> pt2 = rc.Geometry.Point3d(0,10,0)
>>> line2 = rc.Geometry.Line(pt1, pt2)
>>>
>>> rc.Geometry.Intersect.Intersection.LineLine(line1, line2)
(True, 0.5, 0.5)
>>>
>>> file3dm = f = rc.FileIO.File3dm()
>>> file3md_options = rc.FileIO.File3dmWriteOptions()
>>> file3dm.Objects.AddLine(line1)
>>> filepath = 'c:/folder/test.3dm'
>>> file3dm.Write(filepath, file3md_options)
"""

"""
output = pyrevit.output.get_output()
output.print_image(r'C:\image.gif')
"""




"""
no_sheet_views.sort(key = lambda x: x.ViewType, reverse = True)
"""


"""
with forms.WarningBar(title='Pick title corner point'):
    ref_pt = revit.pick_point()
"""


"""
sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to do temperory template')
"""

"""
res = forms.alert(options = ["mark title corners at sheets", "remove existing marks from sheets."], msg = "I want to [.....]")

if "remove" in res:
    option = False
elif "mark" in res:
    option = True
else:
    script.exit()
"""

"""
forms.alert(msg = '{0} FILES RENAMED.'.format(sheetcount), sub_msg = fail_text)
"""



"""
from pyrevit import forms
items = ['item1', 'item2', 'item3']
res = forms.SelectFromList.show(items, button_name='Select Item')
if res == 'item1':
    do_stuff()
~~~~~
ops = [viewsheet1, viewsheet2, viewsheet3]
res = forms.SelectFromList.show(ops,
                                multiselect=False,
                                name_attr='Name',
                                button_name='Select Sheet')
if res.Id == viewsheet1.Id:
    do_stuff()
~~~
forms.SelectFromList.show(
        {'All': '1 2 3 4 5 6 7 8 9 0'.split(),
         'Odd': '1 3 5 7 9'.split(),
         'Even': '2 4 6 8 0'.split()},
        title='MultiGroup List',
        group_selector_title='Select Integer Range:',
        multiselect=True
    )
~~~
ops = {'Sheet Set A': [viewsheet1, viewsheet2, viewsheet3],
       'Sheet Set B': [viewsheet4, viewsheet5, viewsheet6]}
res = forms.SelectFromList.show(ops,
                                multiselect=True,
                                name_attr='Name',
                                group_selector_title='Sheet Sets',
                                button_name='Select Sheets')
if res.Id == viewsheet1.Id:
    do_stuff()
~~~
from pyrevit import forms

class MyOption(forms.TemplateListItem):
    @property
    def name(self):
        return "Option: {}".format(self.item)

ops = [MyOption('op1'), MyOption('op2', checked=True), MyOption('op3')]
res = forms.SelectFromList.show(ops,
                                multiselect=True,
                                button_name='Select Item')
~~~

selected_views = forms.SelectFromList.show(no_sheet_views,
                                multiselect=True,
                                name_attr='Name',
                                title = "Those views are not on sheet",
                                button_name= "Mark them with 'NoSheet-' prefix",
                                filterfunc=lambda x: x.ViewType not in [DB.ViewType.Legend, DB.ViewType.Schedule])
"""


"""
DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()

.OfCategory(DB.BuiltInCategory.OST_Massing)
"""



"""
with revit.Transaction("Mark NoSheet Views"):
    for view in selected_views:
        new_name = "NoSheet-" + view.Name
        view.Parameter[DB.BuiltInParameter.VIEW_NAME].Set(new_name)
"""



"""
def final_print_table():
	table_data = []
	for item in view_item_collection:
		if item.view_name in view_item_collection_selected:
			#temp_list = [item.critical_level_text, item.view_name, item.line_count]
			temp_list = [ item.critical_level_text, item.view_name, item.line_count, output.linkify(item.id, title = "Go To View")]
			table_data.append(temp_list)

	output.print_table(table_data=table_data,title="Bad Views by Line Count ",columns=[ "Critical Level", "View Name", "Line Count", "View Link"],formats=['', '{}', '{} Lines', '{}'])
"""



"""
selection = revit.get_selection()

if len(selection) > 1:
    forms.alert("Please select 1 tags only.")
    script.exit()

if "Tags" not in selection[0].Category.Name:
    forms.alert("This is not a tag.")
    script.exit()
"""
"""
ref_tag = revit.doc.GetElement(get_ref_tag_id())
"""
