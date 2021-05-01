from pyrevit import forms, script, DB, revit
from math import pi

def switch_view_to(view_name, doc):
    view = get_view_by_name(view_name, doc)
    revit.uidoc.ActiveView = view

def get_view_by_name(name, doc):
    views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    for view in views:
        if view.Name == name:
            return view

def zoom_to_player(player):
    return
    with revit.Transaction("redraw views"):
        revit.uidoc.ShowElements(player)
        revit.uidoc.RefreshActiveView()

def update_camera(perspective_view, target):

    old_orientation = perspective_view.GetOrientation()
    forward_direction = target - old_orientation.EyePosition
    pt0 = old_orientation.EyePosition
    pt1 = pt0 + forward_direction
    pt2 = pt0 + DB.XYZ(0,0,1)
    plane = DB.Plane.CreateByThreePoints(pt0,pt1,pt2)
    normal = plane.Normal
    up_direction = DB.Transform.CreateRotationAtPoint(normal, (90/180)*pi,old_orientation.EyePosition).OfVector(forward_direction)
    orientation = DB.ViewOrientation3D(old_orientation.EyePosition, up_direction, forward_direction)#eye,up,forward


    perspective_view.SetOrientation(orientation)
