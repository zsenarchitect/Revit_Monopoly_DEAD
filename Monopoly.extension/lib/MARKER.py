from pyrevit import revit, DB, forms
import MATERIAL
import PLAYER
import random

def update_land_team(marker, team):
    with revit.Transaction("Local Transaction"):
        marker.LookupParameter("_property_team").Set(team)
        marker.LookupParameter("color plate mat.").Set(MATERIAL.get_material_by_name(team).Id)
        marker.LookupParameter("show_color plate").Set(1)

def update_land_value(marker, price):
    with revit.Transaction("Local Transaction"):
        marker.LookupParameter("_land_value").Set(price)
        marker.LookupParameter("_land_value_text_display").Set("${}".format(price))

def find_max_marker_id_on_map():
    safety = 100
    counter = 0
    while counter < safety:
        if get_marker_by_id(counter + 1) == None:
            return counter
        counter += 1

def get_marker_by_id(marker_id):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    for generic_model in generic_models:
        family_name = str(generic_model.Symbol.Family.Name)
        if family_name == "MAP_MARKER" and generic_model.LookupParameter("_marker_position_ID").AsInteger() == int(marker_id):
            return generic_model

def get_prison_id():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    for generic_model in generic_models:
        if generic_model.Symbol.Family.Name == "MAP_MARKER" and generic_model.LookupParameter("_marker_event_title").AsString() == "Prison":
            return generic_model.LookupParameter("_marker_position_ID").AsInteger()


def get_hospital_id():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    for generic_model in generic_models:
        if generic_model.Symbol.Family.Name == "MAP_MARKER" and generic_model.LookupParameter("_marker_event_title").AsString() == "Hospital":
            return generic_model.LookupParameter("_marker_position_ID").AsInteger()

def get_marker_description(marker):
    return marker.LookupParameter("_marker_event_description").AsString()

def get_marker_data(marker):
    return marker.LookupParameter("_marker_event_data").AsString()

def get_marker_title(marker):
    return marker.LookupParameter("_marker_event_title").AsString()

def get_marker_team(marker):
    return marker.LookupParameter("_property_team").AsString()

def get_marker_land_value(marker):
    return marker.LookupParameter("_land_value").AsInteger()


def pay_land(marker, agent):
    price = marker.LookupParameter("_land_value").AsInteger()
    team = get_marker_team(marker)
    agent.update_money(-price)
    #forms.alert("Paying {} ${}".format(team, price))
    print "Paying {} ${}".format(team, price)
    PLAYER.team_share_money(team, price)#make them evenly share the amount pay

def purchase_new_land(marker, agent):
    decision = forms.alert(msg = "Land available, do you want to buy it?", options = ["Yes, I pay $1000",\
                                                                                        "No."])
    if decision == None or "No" in decision:
        return
    inital_price = 1000
    agent.update_money(-inital_price)

    update_land_team(marker, agent.get_team())
    update_land_value(marker, inital_price)

def purchase_abandon_land(marker, agent):
    price = get_marker_land_value(marker)
    decision = forms.alert(msg = "Abandoned land available, do you want to buy it?", \
                            options = ["Yes, team pay ${}".format(price),"No."])
    if decision == None or "No" in decision:
        return

    PLAYER.team_share_money(agent.get_team(), -price)
    update_land_team(marker, agent.get_team())


def upgrade_land(marker, agent):
    price = get_marker_land_value(marker)
    pay = int(price * 0.5)
    new_price = price + pay
    maintaince_fee = int(price * 0.1)
    if random.random()*100 - 60 > agent.get_luck():
        decision = forms.alert(msg = "Earthquake! Building collaspe.\nWant to rebuild your team land to ${}?".format(price), \
                                options = ["Yes, team pay ${}".format(price),"No. Abandon it."])
        if decision == None or "No" in decision:
            update_land_team(marker, "abandon")
            return
        else:
            PLAYER.team_share_money(agent.get_team(), -price)
            return


    decision = forms.alert(msg = "Land worths ${}.\nMaintaince fee is 10%.\nWant to upgrade your team land to ${}?".format(price, new_price), \
                            options = ["Yes, team pay ${}.".format(pay),"No, I just pay ${} maintaince fee.".format(maintaince_fee), "Abandon it."])
    if decision == None or "No" in decision:
        agent.update_money(- maintaince_fee)
    elif "Abandon" in decision:
        update_land_team(marker, "abandon")
    else:
        PLAYER.team_share_money(agent.get_team(), -pay)
        #agent.update_money(- pay)
        update_land_value(marker, new_price )
