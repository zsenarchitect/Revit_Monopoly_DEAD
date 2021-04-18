
import os.path as op


from pyrevit import revit, DB, UI
from pyrevit import forms



# test dockable panel =========================================================

class DockableExample(forms.WPFPanel):
    panel_title = "Monoploy Game"
    panel_id = "6b59123c-e13a-43d4-a98d-11c19cd00577"
    panel_source = op.join(op.dirname(__file__), "Monoploy_UI.xaml")

    def roll_dice(self, sender, args):
        forms.alert("Voila!!!")


forms.register_dockable_panel(DockableExample)
#forms.open_dockable_panel("6b59123c-e13a-43d4-a98d-11c19cd00577")
