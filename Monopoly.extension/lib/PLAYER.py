from pyrevit import DB, revit, forms
import KEYWORD
import MARKER
import random
import CLOUD
import MONEY_GATE
import UTILITY
#import CAMERA
import MATERIAL
from time import sleep

def fix_overlap_player(player):
    i = 0
    while spot_taken(player) or i > 100:
        #print "shifting"
        shift_player(player)
        i += 1

def spot_taken(my_player):
    all_players = get_players()
    for player in all_players:
        if player.Symbol.LookupParameter("_property_name").AsString() == my_player.Symbol.LookupParameter("_property_name").AsString():
            #print "it is me"
            continue
        #print player.Location.Point,my_player.Location.Point
        if player.Location.Point.DistanceTo(my_player.Location.Point) < 1:
            #print "same spot"
            return True
    return False

def shift_player(player):
    with revit.Transaction("temp"):
        center = player.Location.Point
        angle = random.randrange(0,360)
        import math
        x = 1.5 * math.cos(angle)
        y = 1.5 * math.sin(angle)
        player.Location.Point = center + DB.XYZ(x, y, 0)

def annouce_name_by_richness(data):
    if data == "rich":
        return "Wow! you are the richest"
    elif data == "poor":
        return "Shame! You are the poorest!"


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
        return self.model.LookupParameter("_property_positionID").AsInteger()
    def set_position_id(self, position_id):
        with revit.Transaction("Local Transaction"):
            self.model.LookupParameter("_property_positionID").Set(int(position_id))

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
            print (-UTILITY.mm_to_feet(depth * 1000))
            self.model.LookupParameter("Elevation from Level").Set(-UTILITY.mm_to_feet(depth * 1000))

    def get_hat(self):
        return filter(lambda x: x.Name == "HAT", map(lambda x: revit.doc.GetElement(x), self.model.GetSubComponentIds ()))[0]

    def hat_set_text(self, text):
        if isinstance(text, int):
            mat_name = "money_positive" if text > 0 else "money_negative"
            final_text = "{}${}".format("-" if text < 0 else "", abs(text))
            #print final_text
            with revit.Transaction("Local Transaction"):
                self.model.Symbol.LookupParameter("_hat_text").Set(final_text)
                self.model.Symbol.LookupParameter("_hat_text_mat.").Set(MATERIAL.get_material_by_name(mat_name).Id)
                self.model.Symbol.LookupParameter("_hat_text_length").Set(UTILITY.mm_to_feet((len(final_text)/5) * 1800))#make it propertional to the 1800 length

            return
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_hat_text").Set(text)

    def hat_set_elevation(self, dist):
        #print "f", dist
        with revit.Transaction("Local Transaction"):
            self.model.LookupParameter("_hat_elevation").Set(dist)
        #revit.uidoc.RefreshActiveView()

    def hat_set_visibility(self, boolean):
        with revit.Transaction("Local Transaction"):
            self.model.Symbol.LookupParameter("_hat_visibility").Set(boolean)

    def hat_set_transparency(self, amount):
        amount = int(amount)
        if amount > 100:
            amount = 100
        if amount < 0:
            amount = 0

        overridesetting = DB.OverrideGraphicSettings ().SetSurfaceTransparency(amount)
        with revit.Transaction("Local Transaction"):
            revit.active_view.SetElementOverrides (self.get_hat().Id, overridesetting)

    def update_money(self, amount):
        self.set_money(self.get_money() + int(amount))

        self.hat_set_text(int(amount))
        self.hat_set_visibility(True)
        step = 20
        for i in range(step):
            #print "i = {}".format(i)
            if i > step / 2:
                transparency = 100/(step/2.0)*(i+1) - 100#see the graphic from sketchbook
            else:
                transparency = 0
            #print transparency
            self.hat_set_elevation(i/ 10.00)
            self.hat_set_transparency(transparency)
            revit.uidoc.RefreshActiveView()
            #move iso piece higher and apply fading and turn off eventually
        self.hat_set_visibility(False)
        self.hat_set_elevation(0)

    def update_luck(self, amount):
        self.set_luck(self.get_luck() + int(amount))

    def update_weight(self, amount):
        self.set_is_overweight(amount)

    def update_hold(self):
        current_hold_location = self.get_hold_status()
        current_hold_amount = self.get_hold_amount()
        if current_hold_location == None:
            current_hold_location = "holder place"

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
            if self.get_is_overweight():
                self.set_is_overweight(False)
                forms.alert("Doctor cured your overweight")

            self.set_hold_status("")
            self.set_hold_amount(0)
            current_marker = MARKER.get_marker_by_id(self.get_position_id())
            description = MARKER.get_marker_description(current_marker)
            data = MARKER.get_marker_data(current_marker)
            print "generic update hold data = {}".format(data)
            if "*exit*" in description:
                move_player(self, data)# move player to marker of data id

    def update_hold_prison(self):
        current_hold_location = self.get_hold_status()
        current_hold_amount = self.get_hold_amount()

        if current_hold_amount > 0:
            if current_hold_amount - 1 == 0:
                additiontal_note = "You will free at next round."
            else:
                additiontal_note = ""

            forms.alert("Currently staying in {}\n{} round remains.\n{}".format(current_hold_location, current_hold_amount - 1, additiontal_note))
            self.set_hold_amount(current_hold_amount - 1)


        else:
            forms.alert("You are free from {}".format(current_hold_location))

            self.set_hold_status("")
            self.set_hold_amount(0)
            current_marker = MARKER.get_marker_by_id(self.get_position_id())
            description = MARKER.get_marker_description(current_marker)
            data = MARKER.get_marker_data(current_marker)
            print "prison exit data = {}".format(data)
            move_player(self, data)# move player to marker of data id

    def update_hold_hospital(self):
        current_hold_location = self.get_hold_status()
        current_hold_amount = self.get_hold_amount()

        if current_hold_amount > 0:
            if current_hold_amount - 1 == 0:
                additiontal_note = "You will free at next round."
            else:
                additiontal_note = ""

            forms.alert("Currently staying in {}\n{} round remains.\n{}".format(current_hold_location, current_hold_amount - 1, additiontal_note))
            self.set_hold_amount(current_hold_amount - 1)
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
            print "hospital exit data = {}".format(data)
            move_player(self, data)# move player to marker of data id

    def update_hold_UFO(self):
        current_hold_location = self.get_hold_status()
        current_hold_amount = self.get_hold_amount()

        if current_hold_amount > 0:
            if current_hold_amount - 1 == 0:
                additiontal_note = "You will free at next round."
            else:
                additiontal_note = ""

            forms.alert("Currently staying in {}\n{} round remains.\n{}".format(current_hold_location, current_hold_amount - 1, additiontal_note))
            self.set_hold_amount(current_hold_amount - 1)


        else:
            forms.alert("You are free from {}".format(current_hold_location))
            """
            animation UFO come back and rotae and show player
            """
            self.set_hold_status("")
            self.set_hold_amount(0)



    def update_hold_pit(self):
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
            pit = UTILITY.get_pit()
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

    def hold_in_UFO(self, hold_amount):
        self.set_hold_amount(hold_amount)
        self.set_hold_status("UFO")

        ufo = UTILITY.get_ufo()
        with revit.Transaction("Local"):
            ufo.Location.Point = self.model.Location.Point
        step = 60
        for i in range(step):
            UTILITY.ufo_spin()
            revit.uidoc.RefreshActiveView()
        """
        ufo animation to rotate  show , decede, and hide player transparency, then hide UFO
        """

    def process_event(self, title, description, data):

        if title != "none" and "*" not in title:
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

        if "*UFO*" in description:
            self.hold_in_UFO(data)

        if "*payday*" in description:
            print "Get additional pay!"
            self.update_money(self.get_paycheck())

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
        try:
            move_player(self, other_id)
            move_player(other, my_id)
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





def get_players():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: KEYWORD._PlayerNameKeyword() in x.Symbol.Family.Name, generic_models)

def get_player_name(player):
    family_name = player.Symbol.Family.Name
    player_family_name = family_name.split(KEYWORD._PlayerNameKeyword())[1]
    player_user_name = player.Symbol.LookupParameter("_property_name").AsString()
    player_name = "{}[{}]".format(player_user_name,player_family_name)
    return player_name

def get_player_by_name(name, players):
    return filter(lambda x: get_player_name(x) == name, players)[0]

def pick_player(players):
    names = [get_player_name(x) for x in players]
    name = forms.SelectFromList.show(names, title = "Pick your player!", button_name='Go!')
    player = get_player_by_name(name, players)
    if player == None:
        script.exit()
    else:
        return player

def team_share_money(team, money):

    team_players_models = filter(lambda x: x.Symbol.LookupParameter("_property_team").AsString() == team, get_players())
    team_players_agents = map(lambda x: player_agent(x), team_players_models)
    #print team_players_agents, team_players_models
    #forms.alert( "everyone on {} will get ${}".format(team, money/len(team_players_agents))  )
    print "everyone on {} will get ${}".format(team, money/len(team_players_agents))
    map(lambda x: x.update_money(money/len(team_players_agents)), team_players_agents)

def get_player_by_richness(data):
    ranked_players = sorted(get_players(), key = lambda x: x.Symbol.LookupParameter("_asset_money").AsInteger())
    if data == "rich":
        return player_agent(ranked_players[-1])
    else:
        return player_agent(ranked_players[0])

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

    wind = DB.XYZ(random.random()-0.25,random.random()-0.25,0)
    print "wind = {}".format(wind)

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
    fix_overlap_player(agent.model)
    #CAMERA.zoom_to_player(player)
