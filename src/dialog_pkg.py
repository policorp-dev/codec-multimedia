#dialog_pkg.py

import gi
gi.require_version('Adw', '1')
from gi.repository import Adw
from .config import APPNAME

import gettext
gettext.bindtextdomain(APPNAME, "/usr/share/locale")
gettext.textdomain(APPNAME)
_ = gettext.gettext

class GenericConfirmDialog(Adw.AlertDialog):
    def __init__(self,
                 heading_text,
                 body_text,
                 confirm_label=_("OK"),
                 cancel_label=None,
                 action_appearance=Adw.ResponseAppearance.SUGGESTED,
                 on_cancel=None,
                 on_confirm=None
                 ):

        super().__init__(
            heading=heading_text,
            body=body_text
        )

        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

        if cancel_label:
            self.add_response("cancel", cancel_label)
            self.set_close_response("cancel")

            self.add_response("confirm", confirm_label)
            self.set_response_appearance("confirm", action_appearance)

            self.connect("response", self._on_confirm_response)
        else:
            self.add_response("confirm", confirm_label)
            self.set_response_appearance("confirm", action_appearance)
            self.set_close_response("confirm")
            self.connect("response", self._on_ok_response)

    def _on_confirm_response(self, dialog, response):
        if response == "confirm":
            if self._on_confirm:
                self._on_confirm()
        else:
            if self._on_cancel:
                self._on_cancel()

    def _on_ok_response(self, dialog, response):
        if response == "confirm":
            if self._on_confirm:
                self._on_confirm()
