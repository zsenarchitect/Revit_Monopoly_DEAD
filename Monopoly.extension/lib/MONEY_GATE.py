from pyrevit import DB, revit
import math

def get_gate():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    return filter(lambda x: x.Symbol.Family.Name == "MONEY_GATE", generic_models)[0]

def spin_gate():

    gate = get_gate()
    para = gate.LookupParameter("angle")
    angle = ( (para.AsDouble() / math.pi) * 180 + 1) % 360
    para.Set(angle*math.pi/ 180)

def spin_gate_fast():

    gate = get_gate()
    para = gate.LookupParameter("angle")
    angle = ( (para.AsDouble() / math.pi) * 180 + 37) % 360
    para.Set(angle*math.pi/ 180)
