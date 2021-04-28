__doc__ = "XXXXXXXXXX"
__title__ = "Move"

from pyrevit import forms, DB, revit, script
from time import sleep
import random
#import CAMERA
import CLOUD
import MONEY_GATE
import MARKER
import MATERIAL
import PLAYER
from System.Collections.Generic import List
#!/usr/bin/env python
# coding=utf-8

def mm_to_feet(dist):
    return (int(dist) /1000) * 3.28084

def dice(luck):
    luck = int(luck)
    sample_raw = [-2, -1, 1, 2, 3, 4, 5, 6, 10]#9 item
    sample_raw = [20]######use me to foce a dice
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




def get_pit():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.Family.Name == "PIT", generic_models)[0]



def get_random_event_card(luck):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    random.shuffle(generic_models)
    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if family_name == "CARD":
            if luck - 50 < generic_model.LookupParameter("_property_luck").AsInteger() < luck + 50:
                return generic_model



def move_player(agent, target_marker_id):
    player = agent.model
    target_marker_id = int(target_marker_id)
    initial_pt = player.Location.Point
    final_pt = MARKER.get_marker_by_id(target_marker_id).Location.Point

    try:
        line = DB.Line.CreateBound(initial_pt, final_pt)
        mid_pt = line.Evaluate(0.5, True)
        mid_pt_new = DB.XYZ(mid_pt.X, mid_pt.Y, mid_pt.Z + line.Length/2.0)
        arc = DB.Arc.Create(initial_pt, final_pt, mid_pt_new)
    except:#line too short, just update data and leave
        agent.set_position_id(target_marker_id)
        return

    wind = DB.XYZ(random.uniform(-0.1,0.2),random.uniform(-0.1,0.2),0)

    step = 15
    for i in range(step + 1):
        pt_para = float(i)/step
        temp_location = arc.Evaluate(pt_para, True)
        with revit.Transaction("frame update"):
            player.Location.Point = temp_location
            CLOUD.change_sky(wind)
            MONEY_GATE.spin_gate()


        #perspective_view = CAMERA.get_view_by_name("$Camera_Main", revit.doc)
        #CAMERA.update_camera(perspective_view, temp_location)

        safety = 0.01#so there is never division by zero
        speed = -pt_para * (pt_para - 1) + safety#faster in middle
        pause_time = 0.25 + safety - speed# 1/4 is the peak value in normalised condition

        #sleep(pause_time * _SpeedFactor)
        #revit.doc.Regenerate()
        revit.uidoc.RefreshActiveView()
        #revit.uidoc.UpdateAllOpenViews()
    agent.set_position_id(target_marker_id)

class player_agent:
    def __init__(self, generic_model):
        self.model = generic_model

    def get_name(self):
        return self.model.Symbol.LookupParameter("_property_name").AsString()

    def get_team(self):
        return self.model.Symbol.LookupParameter("_property_team").AsString()
    def set_team(self, team):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_property_team").Set(team)
            self.model.Symbol.LookupParameter("mat.").Set( MATERIAL.get_material_by_name(team).Id )

    def get_paycheck(self):
        return self.model.Symbol.LookupParameter("_property_paycheck").AsInteger()
    def set_paycheck(self, amount):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_property_paycheck").Set(int(amount))

    def get_hold_status(self):
        return self.model.Symbol.LookupParameter("_property_hold_status").AsString()
    def set_hold_status(self, hold_status):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_property_hold_status").Set(hold_status)

    def get_hold_amount(self):
        return self.model.Symbol.LookupParameter("_property_hold_amount").AsInteger()
    def set_hold_amount(self, amount):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_property_hold_amount").Set(int(amount))

    def get_position_id(self):
        return self.model.Symbol.LookupParameter("_property_positionID").AsInteger()
    def set_position_id(self, position_id):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_property_positionID").Set(int(position_id))

    def get_direction(self):
        return self.model.Symbol.LookupParameter("_asset_direction").AsInteger()
    def set_direction(self, direction):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_asset_direction").Set(int(direction))

    def get_luck(self):
        return self.model.Symbol.LookupParameter("_property_luck").AsInteger()
    def set_luck(self, luck):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_property_luck").Set(int(luck))

    def get_money(self):
        return self.model.Symbol.LookupParameter("_asset_money").AsInteger()
    def set_money(self, money):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_asset_money").Set(int(money))

    def get_is_overweight(self):
        if 1 == self.model.Symbol.LookupParameter("_property_is_overweight").AsInteger():
            return True
        return False
    def set_is_overweight(self, boolean):
        with revit.Transaction("Local Transaction"):
            if boolean:
                self.model.Symbol.LookupParameter("_property_is_overweight").Set(1)
                return
            self.model.Symbol.LookupParameter("_property_is_overweight").Set(0)

    def set_elevation(self, depth):
        with revit.Transaction("Local Transaction"):
            print (-mm_to_feet(depth * 1000))
            self.model.LookupParameter("Elevation from Level").Set(-mm_to_feet(depth * 1000))

    def update_money(self, amount):
        self.set_money(self.get_money() + int(amount))

    def update_luck(self, amount):
        self.set_luck(self.get_luck() + int(amount))

    def update_hold(self):
        current_hold_location = self.get_hold_status()
        current_hold_amount = self.get_hold_amount()
        if current_hold_location == None:
            current_hold_location = " holder place"

        #print "&&&&", current_hold_amount
        if current_hold_amount > 0:
            if current_hold_amount - 1 == 0:
                additiontal_note = "You will free at next round."
            else:
                additiontal_note = ""

            forms.alert("Currently staying in {}\n{} round remains.\n{}".format(current_hold_location, current_hold_amount - 1, additiontal_note))
            self.set_hold_amount(current_hold_amount - 1)
            if current_hold_location == "Hospital":
                forms.alert("Hospital Bill: $500")
                self.update_money(-500)

        else:
            forms.alert("You are free from {}".format(current_hold_location))
            if self.get_is_overweight() and current_hold_location == "Hospital":
                self.set_is_overweight(False)
                forms.alert("Doctor cured your overweight")

            self.set_hold_status("")
            self.set_hold_amount(0)
            current_marker = MARKER.get_marker_by_id(self.get_position_id())
            description = MARKER.get_marker_description(current_marker)
            data = MARKER.get_marker_data(current_marker)
            if "*exit*" in description:
                move_player(self, data)# move player to marker of data id

    def update_pit(self):
        depth = self.get_hold_amount()
        raw_dice = dice(self.get_luck())
        if raw_dice >= depth:
            self.set_hold_amount(0)
            self.set_hold_status("")
            forms.alert("it is your lucky day.\nYou only need {} to get out.".format(depth))
            return

        elif raw_dice < 0 and self.get_is_overweight():
            depth += 1
            forms.alert("you are too heavy, floor collaspe while jumping. \nThe pit is now {}m deep.".format(depth))
            self.set_hold_amount(depth)
            pit_marker = MARKER.get_marker_by_id(self.get_position_id())
            pit_marker.LookupParameter("_marker_event_data").Set(str(depth))
            pit = get_pit()
            pit.LookupParameter("depth").Set(int(depth))
            self.set_elevation(depth)
        else:
            forms.alert("you need {} or more, maybe next day.".format(depth))




    def flip_direction(self):
        self.set_direction(-self.get_direction())

    def send_to_prison(self, hold_amount):

        move_player(self, MARKER.get_prison_id())
        self.set_hold_amount(hold_amount)
        self.set_hold_status("Prision")

    def send_to_hospital(self, hold_amount):

        move_player(self, MARKER.get_hospital_id())
        forms.alert("Hospital Bill: $500")
        self.update_money(-500)
        self.set_hold_amount(hold_amount)
        self.set_hold_status("Hospital")

    def hold_in_place(self, hold_amount):
        self.set_hold_amount(hold_amount)
        self.set_hold_status("In Place")

    def hold_in_pit(self, depth):
        #print depth
        self.set_hold_amount(depth)
        self.set_hold_status("Pit")
        forms.alert("The pit is {0}m deep, you will later need to roll {0} or more to get out.".format(depth))
        self.set_elevation(depth)


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
            new_position_id = self.get_position_id() + self.get_direction() * int(data)
            move_player(self, new_position_id)

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

        if self.get_name() == other.get_name():
            annouce_name_by_richness(data)
            return
        else:
            forms.alert("Exchanging with {}".format(other.get_name()))

        my_id, other_id = other.get_position_id(), self.get_position_id()
        move_player(self, other_id)
        move_player(other, my_id)
        try:
            pass
            """
            move_player(self, other_id)
            move_player(other, my_id)
            """
        except:
            forms.alert("On same spot. Swicth looks the same.")


    def exchange_money(self, data):
        other = get_player_by_richness(data)

        if self.get_name() == other.get_name():
            annouce_name_by_richness(data)
            return
        else:
            forms.alert("Exchanging with {}".format(other.get_name()))

        my_money, other_money = other.get_money(), self.get_money()
        self.set_money(other_money)
        other.set_money(my_money)
        forms.alert("{0} gives {2} to {1}\n{1} gives {3} to {0}".format(self.get_name(), \
                                                                        other.get_name(), \
                                                                        my_money, \
                                                                        other_money))

    def exchange_team(self, data):
        other = get_player_by_richness(data)

        if self.get_name() == other.get_name():
            annouce_name_by_richness(data)
            return
        else:
            forms.alert("Exchanging with {}".format(other.get_name()))

        my_team, other_team = other.get_team(), self.get_team()
        self.set_team(other_team)
        other.set_team(my_team)
        forms.alert("{0} is now in {2}\n{1} is now in {3}".format(self.get_name(), \
                                                        other.get_name(), \
                                                        other_team, \
                                                        my_team)\
                                                        )
def annouce_name_by_richness(data):
    if data == "rich":
        return "Wow! you are the richest"
    elif data == "poor":
        return "Shame! You are the poorest!"


def get_player_by_richness(data):
    ranked_players = sorted(PLAYER.get_players(), key = lambda x: x.Symbol.LookupParameter("_asset_money").AsInteger())
    if data == "rich":
        return player_agent(ranked_players[-1])
    else:
        return player_agent(ranked_players[0])

def roll_dice(agent):
    use_magic_dice = False
    if use_magic_dice:
        raw_dice = magic_dice()
    else:
        raw_dice = dice(agent.get_luck())#this can be the dice
    if raw_dice < 0:
        dice_direction = -1
    else:
        dice_direction = 1
    total_step = abs(raw_dice)

    for step in range(total_step):
        if agent.get_is_overweight() and step == 4:
            forms.alert("Overweight, too tied, stay here.")
            agent.hold_in_place(1)
            break


        try:
            new_position_id = agent.get_position_id() + agent.get_direction() * dice_direction
            move_player(agent, new_position_id)

        except:#reach max position, return to zero
            if agent.get_direction() * dice_direction  == 1:
                new_position_id = 0
            else:
                new_position_id = _MaxMarkerID
            #print new_position_id
            move_player(agent, new_position_id)


        current_marker = MARKER.get_marker_by_id(new_position_id)
        marker_title = MARKER.get_marker_title(current_marker)
        marker_description = MARKER.get_marker_description(current_marker)
        marker_data = MARKER.get_marker_data(current_marker)
        #print marker_description, marker_data
        if "*payday*" in marker_description:
            agent.update_money(agent.get_paycheck())
            for i in range(20):
                with revit.Transaction("Animation"):
                    MONEY_GATE.spin_gate_fast()
                    revit.uidoc.RefreshActiveView()
            forms.alert("Passing Payday Gate.\nGetting ${}.".format(agent.get_paycheck()))

    #print "current_position_id = {}".format(new_position_id)
    #agent.update_position_id(new_position_id)
    if "*random event*" in marker_description:
        event_card = get_random_event_card(agent.get_luck())

        card_title = MARKER.get_marker_title(event_card)
        card_description = MARKER.get_marker_description(event_card)
        card_data = MARKER.get_marker_data(event_card)

        agent.process_event(card_title, card_description, card_data)
    else:
        agent.process_event(marker_title, marker_description, marker_data)


    if MARKER.get_marker_title(current_marker) == "none":
        if MARKER.get_marker_team(current_marker) == "":
            #print "buy new land"
            MARKER.purchase_new_land(current_marker, agent)
        elif MARKER.get_marker_team(current_marker) == agent.get_team():
            #print "upgrade my team land"
            MARKER.upgrade_land(current_marker, agent)
        else:
            #print "pay land"
            MARKER.pay_land(current_marker, agent)



def play_this_player(player):
    player_name = PLAYER.get_player_name(player)
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

    with revit.TransactionGroup("Make Move for '{}'".format(player_name)):
        agent = player_agent(player)

        if agent.get_hold_status() != "":
            if agent.get_hold_status() == "Pit":
                agent.update_pit()
            elif agent.get_hold_status() == "Starter":
                raw_dice = dice(agent.get_luck())
                if raw_dice >= 5:
                    move_player(agent, 1)
                    agent.set_hold_amount(0)
                    agent.set_hold_status("")
                else:
                    forms.alert("You need 5 or more to move on.")
            else:
                #print "update hold"
                agent.update_hold()

        #after those update is cleared above, you want to recheck the hold amount and move dice
        if agent.get_hold_amount() == 0:
            roll_dice(agent)


    #CAMERA.switch_view_to("BATTLE GROUND", revit.doc)



################## main code below #####################

_MaxMarkerID = MARKER.find_max_marker_id_on_map()
#print _MaxMarkerID
_SpeedFactor = 0.005#speed factor, 0.01 = less wait = faster, 0.5 = longer wait time = slow



output = script.get_output()
killtime = 1000
output.self_destruct(killtime)

players = PLAYER.get_players()

"""
player = PLAYER.pick_player(players)
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
