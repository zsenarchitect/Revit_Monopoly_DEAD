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
import UTILITY
#from System.Collections.Generic import List
#!/usr/bin/env python
# coding=utf-8


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



def roll_dice(agent):
    use_magic_dice = False
    if use_magic_dice:
        raw_dice = magic_dice()
    else:
        raw_dice = UTILITY.dice(agent.get_luck())#this can be the dice
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
            PLAYER.move_player(agent, new_position_id)
            print "A{}:new_position_id = {}".format(agent.get_name(),new_position_id)
        except:#reach max position, return to zero
            if agent.get_direction() * dice_direction  == 1:
                new_position_id = 0
            else:
                new_position_id = _MaxMarkerID
            #print new_position_id
            PLAYER.move_player(agent, new_position_id)
            print "B{}:new_position_id = {}".format(agent.get_name(),new_position_id)

        current_marker = MARKER.get_marker_by_id(new_position_id)
        marker_title = MARKER.get_marker_title(current_marker)
        marker_description = MARKER.get_marker_description(current_marker)
        marker_data = MARKER.get_marker_data(current_marker)
        #print marker_description, marker_data
        if "*payday*" in marker_description:

            for i in range(20):
                with revit.Transaction("Animation"):
                    MONEY_GATE.spin_gate_fast()
                    revit.uidoc.RefreshActiveView()
            agent.update_money(agent.get_paycheck())
            #forms.alert("Passing Payday Gate.\nGetting ${}.".format(agent.get_paycheck()))

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
            MARKER.purchase_new_land(current_marker, agent)
        elif MARKER.get_marker_team(current_marker) == "abandon":
            MARKER.purchase_abandon_land(current_marker, agent)
        elif MARKER.get_marker_team(current_marker) == agent.get_team():
            MARKER.upgrade_land(current_marker, agent)
        else:
            MARKER.pay_land(current_marker, agent)



def play_this_player(player):
    player_name = PLAYER.get_player_name(player)
    #CAMERA.zoom_to_player(player)
    forms.alert( "Time for {}".format(player_name)  )

    #current_view = revit.doc.ActiveView
    #CAMERA.switch_view_to("$Camera_Main", revit.doc)
    #revit.uidoc.RefreshActiveView()

    with revit.TransactionGroup("Make Move for '{}'".format(player_name)):
        agent = PLAYER.player_agent(player)

        if agent.get_hold_status() != "":
            if agent.get_hold_status() == "Pit":
                agent.update_hold_pit()
            elif agent.get_hold_status() == "Starter":
                raw_dice = UTILITY.dice(agent.get_luck())
                if raw_dice >= 5:
                    PLAYER.move_player(agent, 1)
                    agent.set_hold_amount(0)
                    agent.set_hold_status("")
                else:
                    forms.alert("You need 5 or more to move on.")
            elif agent.get_hold_status() == "Hospital":
                agent.update_hold_hospital()
            else:
                agent.update_hold()

        #after those update is cleared above, you want to recheck the hold amount and move dice
        if agent.get_hold_amount() == 0 and agent.get_hold_status() == "":#if player just got hold update to 0, its hold location is still in origitnal place so need to check that as well
            roll_dice(agent)

    #sleep(2)
    #CAMERA.switch_view_to("BATTLE GROUND", revit.doc)



################## main code below #####################
_MaxMarkerID = MARKER.find_max_marker_id_on_map()
#print _MaxMarkerID
#_SpeedFactor = 0.005#speed factor, 0.01 = less wait = faster, 0.5 = longer wait time = slow

output = script.get_output()
killtime = 100
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
