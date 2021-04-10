__doc__ = "XXXXXXXXXX"
__title__ = "Move"

from pyrevit import forms, DB, revit, script
from time import sleep
import random
import CAMERA
from System.Collections.Generic import List
#!/usr/bin/env python
# coding=utf-8

def dice():
    sample_raw = [-2, -1, 1, 2, 3, 4, 5, 6, 10]#9 item
    sample = []
    for item in sample_raw:
        if item < 0:
            sample.extend([item]*2)
        elif item <=6:
            sample.extend([item]*6)
        else:
            sample.extend([item]*1)

    random.shuffle(sample)
    #print sample
    weight = (20, 20, 50, 50, 50, 50, 50, 50, 10)#9 item
    #return random.choices(sample, weights = weight , k = 1)[0]
    #print "dice number = {}".format(raw_dice)
    raw_dice = random.choice(sample)
    forms.alert("dice = {}".format(raw_dice))
    return raw_dice

def get_marker_by_id(marker_id):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if family_name == "MAP_MARKER" and generic_model.LookupParameter("_marker_position_ID").AsInteger() == marker_id:
            return generic_model

def get_random_event_card():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    random.shuffle(generic_models)
    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        #print family_name
        if family_name == "CARD":
            return generic_model


def get_marker_description(marker):
    return marker.LookupParameter("_marker_event_description").AsString()

def get_marker_data(marker):
    return marker.LookupParameter("_marker_event_data").AsString()

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
    return player

def move_player(player, target_marker_id):
    initial_pt = player.Location.Point
    """
    vector = DB.XYZ(5,0,0)
    final_pt = initial_pt + vector
    """
    final_pt = get_marker_by_id(target_marker_id).Location.Point

    line = DB.Line.CreateBound(initial_pt, final_pt)
    mid_pt = line.Evaluate(0.5, True)
    mid_pt_new = DB.XYZ(mid_pt.X, mid_pt.Y, mid_pt.Z + line.Length/5.0)
    arc = DB.Arc.Create(initial_pt, final_pt, mid_pt_new)
    #pt_list = List[DB.XYZ]([])
    #spline = DB.NurbSpline.Create()
    #DB.CurveElement.SetGeometryCurve(arc, False)


    step = 50
    for i in range(step + 1):
        pt_para = float(i)/step
        temp_location = arc.Evaluate(pt_para, True)
        #print temp_location.Z
        #temp_location = line.Evaluate(pt_para, True)
        player.Location.Point = temp_location


        #perspective_view = CAMERA.get_view_by_name("$Camera_Main", revit.doc)
        #CAMERA.update_camera(perspective_view, temp_location)


        revit.doc.Regenerate()
        revit.uidoc.RefreshActiveView()
        revit.uidoc.UpdateAllOpenViews()
        safety = 0.01#so there is never division by zero
        speed = -pt_para * (pt_para - 1) + safety#faster in middle
        pause_time = 0.25 + safety - speed# 1/4 is the peak value in normalised condition
        factor = 0.02#speed factor, 0.01 = less wait = faster, 0.5 = longer wait time = slow
        sleep(pause_time * factor)

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

class player_agent:
    def __init__(self, generic_model):
        self.model = generic_model
        #self.name = generic_model.Symbol.LookupParameter("_property_name").AsString()
        self.position_id = generic_model.Symbol.LookupParameter("_property_positionID").AsInteger()
        #self.luck = generic_model.Symbol.LookupParameter("_property_luck").AsInteger()
        #self.money = generic_model.Symbol.LookupParameter("_asset_money").AsInteger()
        self.direction = generic_model.Symbol.LookupParameter("_asset_direction").AsInteger()

    def update_position_id(self, id):
        self.model.Symbol.LookupParameter("_property_positionID").Set(id)

    def update_money(self, amount):
        current_money = self.model.Symbol.LookupParameter("_asset_money").AsInteger()
        self.model.Symbol.LookupParameter("_asset_money").Set(current_money + int(amount))

    def update_hold(self, amount):
        current_hold_location = self.model.Symbol.LookupParameter("_property_hold_status").AsString()
        current_hold_amount = self.model.Symbol.LookupParameter("_property_hold_amount").AsInteger()
        if current_hold_location:
            forms.alert("Currently staying in {}".format(current_hold_location))
        #self.model.Symbol.LookupParameter("_asset_money").Set(current_money + int(amount))

    def send_to_hospital(self, hold_amount):

        move_player(agent.model, 100)#100 is the id for hospital
        self.model.Symbol.LookupParameter("_property_hold_status").Set("Hospital")
        self.model.Symbol.LookupParameter("_property_hold_amount").Set(int(hold_amount))

    def hold_in_place(self, hold_amount):
        self.model.Symbol.LookupParameter("_property_hold_status").Set("In Place")
        self.model.Symbol.LookupParameter("_property_hold_amount").Set(int(hold_amount))

    def process_event(self, card):
        title = event_card.LookupParameter("_marker_event_title").AsString()
        description = event_card.LookupParameter("_marker_event_description").AsString()
        data = event_card.LookupParameter("_marker_event_data").AsString()
        forms.alert("{}".format(title))
        if "*hospital*" in description:
            hold_amount = data
            agent.send_to_hospital(hold_amount)
        if "*hold in place*" in description:
            hold_amount = data
            agent.hold_in_place(hold_amount)
        if "*money*" in description:
            agent.update_money(data)
        if "*walk*" in description:
            new_position_id = agent.position_id + agent.direction * data
            move_player(agent.model, new_position_id)
            agent.position_id = new_position_id


        pass



################## main code below #####################
_PlayerNameKeyword = "$Player_"
_MaxMarkerID = 31
#user_name_para_guid = #"_property_name"




players = get_players()
player = pick_player(players)
player_name = get_player_name(player)


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
    raw_dice = dice()#this can be the dice
    if raw_dice < 0:
        dice_direction = -1
    else:
        dice_direction = 1
    total_step = abs(raw_dice)

    for step in range(total_step):
        try:
            new_position_id = agent.position_id + agent.direction * dice_direction
            move_player(agent.model, new_position_id)
            agent.position_id = new_position_id
        except:#reach max position, return to zero
            new_position_id = 0 if dice_direction == 1 else _MaxMarkerID
            move_player(agent.model, new_position_id)
            agent.position_id = new_position_id

        current_marker = get_marker_by_id(new_position_id)
        marker_description = get_marker_description(current_marker)
        marker_data = get_marker_data(current_marker)
        #print marker_description, marker_data
        if "*payday*" in marker_description:

            agent.update_money(marker_data)
            forms.alert("Passing Payday.\nGetting ${}.".format(marker_data))



    #print "current_position_id = {}".format(new_position_id)
    agent.update_position_id(new_position_id)
    if "*random event*" in marker_description:
        event_card = get_random_event_card()
        agent.process_event(event_card)
    if "*hospital*" in marker_description:
        agent.send_to_hospital(marker_data)

#CAMERA.switch_view_to("BATTLE GROUND", revit.doc)
output = script.get_output()
killtime = 30
output.self_destruct(killtime)






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
