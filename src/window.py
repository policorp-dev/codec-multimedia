# window.py
#
# Copyright 2025 lucas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import gi
import subprocess
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

@Gtk.Template(resource_path='/org/gnome/CodecMultimedia/window.ui')
class CodecMultimediaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CodecMultimediaWindow'
    
    internet_banner: Adw.Banner = Gtk.Template.Child()
    install_button: Gtk.Button = Gtk.Template.Child()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.monitor = Gio.NetworkMonitor.get_default()
        self.monitor.connect("network-changed", self.on_network_changed)
        self.internet_banner.set_sensitive(True)
        # 4. Faça uma verificação inicial
        self.check_network_status()
    
    @Gtk.Template.Callback()
    def on_install_button_clicked(self, button):
        print("Executando instalação de codecs…")
        
    def iniciar_instalacao(self):
        print("Executando instalação de codecs…")
        
    def check_network_status(self):
            if self.monitor.get_network_available():
                self.internet_banner.set_revealed(False)
                self.install_button.set_sensitive(True) 
            else:
                self.internet_banner.set_visible(True) 
                self.internet_banner.set_revealed(True)
                self.install_button.set_sensitive(False)

    def on_network_changed(self, monitor, is_available):
        print(f"O status da rede mudou. Disponível: {is_available}")
        self.check_network_status()

    @Gtk.Template.Callback()
    def on_retry_connection_clicked(self, banner):
        try:
            with open("/.flatpak-info", "r"):
                subprocess.Popen(["flatpak-spawn", "--host", "gnome-control-center", "wifi"])
                return
        except FileNotFoundError:
            pass

        try:
            subprocess.Popen(["gnome-control-center", "wifi"])
        except Exception:
            pass
            
