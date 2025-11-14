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
import threading
import re
import sys
import requests
try:
    import apt
except Exception:
    pass

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from .fingerprint import verificar_focal_tech, verificar_libfprint
from .dialog_pkg import GenericConfirmDialog
from .config import APPNAME
import gettext
gettext.bindtextdomain(APPNAME, "/usr/share/locale")
gettext.textdomain(APPNAME)
_ = gettext.gettext

verificar_lib_information = verificar_focal_tech()
erro_log  = ""
@Gtk.Template(resource_path='/org/gnome/CodecMultimedia/window.ui')
class CodecMultimediaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CodecMultimediaWindow'

    internet_banner: Adw.Banner = Gtk.Template.Child()
    install_button: Gtk.Button = Gtk.Template.Child()
    install_progress_bar: Gtk.ProgressBar = Gtk.Template.Child()
    progress_label: Gtk.Label = Gtk.Template.Child()
    title_fingerprint: Gtk.Label = Gtk.Template.Child()
    label_fingerprint: Gtk.Label = Gtk.Template.Child()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.pulse_timer_id = None 
        self.monitor = Gio.NetworkMonitor.get_default()
        self.monitor.connect("network-changed", self.on_network_changed)
        self.internet_banner.set_sensitive(True)
        self.check_network_status()
        if self.verificar_codecs_instalados():
            self.install_button.set_label(_("Remove"))
            self.install_button.set_sensitive(True)
            self.install_button.remove_css_class("suggested-action")
            self.install_button.add_css_class("destructive-action")
        if verificar_lib_information:
            self.title_fingerprint.set_visible(True)
            self.label_fingerprint.set_visible(True)
        
    @Gtk.Template.Callback()
    def on_install_button_clicked(self, button):
        texto_do_botao = self.install_button.get_label()
        if texto_do_botao == _("Install"):
           dialog = GenericConfirmDialog(
           heading_text=_("The packages will be installed. Do you wish to continue?"),
           body_text="",
           cancel_label=_("No"),
           confirm_label=_("Yes"),
           action_appearance=Adw.ResponseAppearance.SUGGESTED,
           on_cancel=self._cancel,
           on_confirm=self.iniciar_instalacao
            )
           dialog.present(self)
           self.progress_label.set_text(_("Installing..."))
           print("Executando instalação de codecs…")
        elif texto_do_botao == _("Remove"):
            print("Executando instalação de codecs…")
            dialog = GenericConfirmDialog(
            heading_text=_("The packages will be removed, do you wish to continue?"),
            body_text="",
            cancel_label=_("No"),
            confirm_label=_("Yes"),
            action_appearance=Adw.ResponseAppearance.SUGGESTED,
            on_cancel=self._cancel,
            on_confirm=self.iniciar_instalacao
             )
            dialog.present(self)
            self.progress_label.set_text(_("Removing..."))
            print("Executando remoção de codecs…")
        else:
            task_label=_("Task failed to execute")
            dialog = GenericConfirmDialog(
                    heading_text=_("Task failed"),
                    body_text=_(f"{task_label}: {erro_log}"),
                    confirm_label=_("OK"),
                    on_confirm=self._on_confirm_ok
            )
            dialog.present(self)
        
    def iniciar_instalacao(self):
        texto_do_botao = self.install_button.get_label()
        
        self.install_button.set_sensitive(False)
        self.install_progress_bar.set_visible(True)
        self.progress_label.set_visible(True)
        if texto_do_botao == _("Install"):
            self.progress_label.set_text(_("Installing..."))
            print("Executando instalação de codecs…")
        else:
            self.progress_label.set_text(_("Removing..."))
            print("Executando instalação de codecs…")
            
        if self.pulse_timer_id is None:
            self.pulse_timer_id = GLib.timeout_add(100, self.do_pulse)

        thread = threading.Thread(target=self._monitorar_instalacao_thread)
        thread.daemon = True
        thread.start()


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
    
    def do_pulse(self):
        self.install_progress_bar.pulse()
        return GLib.SOURCE_CONTINUE

    def _monitorar_instalacao_thread(self):
        texto_do_botao = self.install_button.get_label()
        if texto_do_botao == _("Install"):
            helper_script_path = "/usr/share/codec-multimedia/codec_multimedia/install_apt.py"
        else:
            helper_script_path = "/usr/share/codec-multimedia/codec_multimedia/uninstall_apt.py"
        cmd = ["pkexec", "/usr/bin/python3", "-u", helper_script_path]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,    
                text=True                  
            )
            
            stdout_output, stderr_output = process.communicate()
            
            if process.returncode == 0:
                GLib.idle_add(self.finalizar_instalacao, True, "Instalação Concluída!")
            else:
                print(f"Erro no script helper (stderr): {stderr_output}") # Loga o erro completo
                
                if stderr_output and stderr_output.strip():
                    linhas_de_erro = stderr_output.strip().splitlines()
                    ultima_linha_erro = linhas_de_erro[-1]
                    
                    if ultima_linha_erro.startswith("ERRO:"):
                        ultima_linha_erro = ultima_linha_erro.replace("ERRO:", "").strip()
                        
                    GLib.idle_add(self.finalizar_instalacao, False, f"Falha: {ultima_linha_erro}")
                else:
                    GLib.idle_add(self.finalizar_instalacao, False, "Falha (erro desconhecido)")

        except Exception as e:
            print(f"Erro ao chamar Popen/pkexec: {e}")
            GLib.idle_add(self.finalizar_instalacao, False, "Erro no Polkit")

    def finalizar_instalacao(self, sucesso: bool, mensagem: str):
        if self.pulse_timer_id is not None:
            GLib.source_remove(self.pulse_timer_id)
            self.pulse_timer_id = None
            
        self.install_progress_bar.set_visible(False)
        self.progress_label.set_visible(False)
        
        if sucesso:
            texto_do_botao = self.install_button.get_label()
            if texto_do_botao == _("Install"):
                self.install_button.set_label(_("Remove"))
                self.install_button.set_sensitive(True)
                self.install_button.remove_css_class("suggested-action")
                self.install_button.add_css_class("destructive-action")
                dialog = GenericConfirmDialog(
                    heading_text=_("Installed"),
                    body_text=_("The package was installed successfully!"),
                    confirm_label=_("OK"),
                    on_confirm=self._on_confirm_ok
                )
            else:
                self.install_button.set_label(_("Install"))
                self.install_button.set_sensitive(True)
                self.install_button.remove_css_class("destructive-action")
                self.install_button.add_css_class("suggested-action")
                dialog = GenericConfirmDialog(
                    heading_text=_("Removed"),
                    body_text=_("The packages have been successfully removed!"),
                    confirm_label=_("OK"),
                    on_confirm=self._on_confirm_ok
                )

            dialog.present(self)
        else:
            self.install_button.set_label(_("Retry"))
            self.install_button.set_sensitive(True) 
            self.install_button.remove_css_class("suggested-action")
            self.install_button.add_css_class("destructive-action")
            global erro_log
            erro_log = mensagem
            task_label=_("Task failed to execute")
            dialog = GenericConfirmDialog(
                    heading_text=_("Task failed"),
                    body_text=_(f"{task_label}: {erro_log}"),
                    confirm_label=_("OK"),
                    on_confirm=self._on_confirm_ok
            )
            dialog.present(self)

        return GLib.SOURCE_REMOVE
        
    def verificar_codecs_instalados(self) -> bool:
        caminho_arquivo = "/usr/share/codec-multimedia/codec_multimedia/codecs.txt"
        try:
            with open(caminho_arquivo, "r") as f:
                pacotes = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except FileNotFoundError:
            print(f"AVISO: {caminho_arquivo} não encontrado.", file=sys.stderr)
            return False 

        if not pacotes:
            print("AVISO: codecs.txt está vazio.")
            return False
        try:
            cache = apt.Cache()
            cache.open(None)
            
            for pkg_name in pacotes:
                pkg = cache[pkg_name]
                if not pkg.is_installed:
                    return False
            
            print("INFO: Todos os codecs de sistema estão instalados.")
            return True
            
        except KeyError as e:
            print(f"AVISO: Pacote '{e.args[0]}' não existe no APT.", file=sys.stderr)
            return False 
        except Exception as e:
            print(f"Erro ao ler o cache do APT: {e}", file=sys.stderr)
            return False

    def _cancel(self):
        return

    def _on_confirm_ok(self):
        pass
