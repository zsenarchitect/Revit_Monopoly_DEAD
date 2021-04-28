from pyrevit import DB, revit

def get_material_by_name(name):
    all_materials = DB.FilteredElementCollector(revit.doc).OfClass(DB.Material).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Name == name, all_materials)[0]
