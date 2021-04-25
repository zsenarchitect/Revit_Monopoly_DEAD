from pyrevit import DB, revit

def get_clouds():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    return filter(lambda x: x.Symbol.Family.Name == "CLOUD", generic_models)

def move_cloud(cloud, wind):


    cloud.Location.Point += wind


def change_sky(wind):
    clouds = get_clouds()
    map(move_cloud, clouds,[wind] * len(clouds))
