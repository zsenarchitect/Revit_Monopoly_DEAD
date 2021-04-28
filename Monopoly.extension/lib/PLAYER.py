from pyrevit import DB, revit
import KEYWORD

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
    forms.alert( "everyone on {} will get ${}".format(team, money/len(team_players_agents))  )
    map(lambda x: x.update_money(money/len(team_players_agents)), team_players_agents)
