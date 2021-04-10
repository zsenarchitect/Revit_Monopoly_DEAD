
import sys
import time
import os.path as op

from pyrevit import HOST_APP, framework
from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import routes


# test dockable panel =========================================================

class DockableExample(forms.WPFPanel):
    panel_title = "pyRevit Dockable Panel Title"
    panel_id = "6b59123c-e13a-43d4-a98d-11c19cd00577"
    panel_source = op.join(op.dirname(__file__), "DockableExample.xaml")

    def do_something(self, sender, args):
        forms.alert("Voila!!!")


forms.register_dockable_panel(DockableExample)
