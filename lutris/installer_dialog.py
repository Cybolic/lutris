# -*- coding:Utf-8 -*-
###############################################################################
## Lutris
##
## Copyright (C) 2009 Mathieu Comandon strycore@gmail.com
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###############################################################################



import gtk
import runners
import os
import logging
from lutris.config import LutrisConfig
from lutris.installer_config_vbox import InstallerConfigVBox
from lutris.runner_config_vbox import RunnerConfigVBox
from lutris.system_config_vbox import SystemConfigVBox

class InstallerDialog(gtk.Dialog):
    def __init__(self,parent):
        gtk.Dialog.__init__(self)
        self.parent_window = parent
        self.set_title("Install a game")
        self.set_size_request(600,500)

        #Real name
        realname_hbox = gtk.HBox()
        self.realname_label = gtk.Label("Name")
        realname_hbox.pack_start(self.realname_label,False,False,5)
        self.realname_entry = gtk.Entry()
        realname_hbox.pack_start(self.realname_entry)
        self.vbox.pack_start(realname_hbox,False,False,5)

        self.lutris_config = LutrisConfig()

        #Runner
        #get a list of available runners
        runner_liststore = gtk.ListStore(str,str)
        runner_liststore.append(("Choose a runner for the list",""))
        for runner_cls in runners.__all__:
            runner = eval("runners."+runner_cls+"."+runner_cls+"()")
            if hasattr(runner,"description"):
                description = runner.description
            else:
                logging.debug("Please fix %s and add a description attribute" % runner_cls)
                description = ""
            if hasattr(runner,"machine"):
                machine = runner.machine
            else:
                logging.debug("Please fix % and add a machine attribute" % runner_cls)
                machine = ""
            if runner.is_installed():
                runner_liststore.append((machine+" ("+ description +")" ,runner_cls))

        self.runner_combobox = gtk.ComboBox(runner_liststore)
        self.runner_combobox.connect("changed",self.on_runner_changed)
        cell = gtk.CellRendererText()
        self.runner_combobox.pack_start(cell, True)
        self.runner_combobox.add_attribute(cell, 'text', 0)
        self.vbox.pack_start(self.runner_combobox,False,True,5)

        self.notebook = gtk.Notebook()
        self.vbox.pack_start(self.notebook)

        #Game configuration
        self.installer_config_vbox = gtk.Label("Select a runner from the list")
        self.installer_config_scrolled_window = gtk.ScrolledWindow()
        self.installer_config_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.installer_config_scrolled_window.add_with_viewport(self.installer_config_vbox)
        self.notebook.append_page(self.installer_config_scrolled_window,gtk.Label("Installer"))

        #Runner configuration
        self.runner_config_vbox = gtk.Label("Select a runner from the list")
        self.runner_config_scrolled_window = gtk.ScrolledWindow()
        self.runner_config_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.runner_config_scrolled_window.add_with_viewport(self.runner_config_vbox)
        self.notebook.append_page(self.runner_config_scrolled_window,gtk.Label("Runner configuration"))

        #System configuration
        self.system_config_vbox = SystemConfigVBox(self.lutris_config)
        self.system_config_scrolled_window = gtk.ScrolledWindow()
        self.system_config_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.system_config_scrolled_window.add_with_viewport(self.system_config_vbox)
        self.notebook.append_page(self.system_config_scrolled_window,gtk.Label("System configuration"))

        #Action area
        cancel_button = gtk.Button(None, gtk.STOCK_CANCEL)
        install_button = gtk.Button(None, gtk.STOCK_ADD)
        self.action_area.pack_start(cancel_button)
        self.action_area.pack_start(install_button)
        cancel_button.connect("clicked", self.close)
        install_button.connect("clicked", self.install_game)
        #Finish
        self.show_all()
        self.run()

    def install_game(self, button):
        """OK button pressed in the Add Game Dialog"""
        #Get name
        realname = self.realname_entry.get_text()
        #Get runner
        self.lutris_config.config["realname"] = realname
        self.lutris_config.config["runner"] = self.runner_class

        if self.runner_class and realname:
            game_identifier = self.lutris_config.save(type="game")
            self.game_info = {"Game Name": realname,"Runner": self.runner_class , "name": game_identifier}
            self.destroy()


    def on_runner_changed(self,widget):
        selected_runner = widget.get_active()
        scroll_windows_children = [self.installer_config_scrolled_window.get_children(),self.runner_config_scrolled_window.get_children(),self.system_config_scrolled_window.get_children()]
        for scroll_window_children in scroll_windows_children:
            for child in scroll_window_children:
                child.destroy()

        if selected_runner == 0:
            self.no_runner_selected()
            return

        self.runner_class = widget.get_model()[selected_runner][1]
        self.lutris_config = LutrisConfig(self.runner_class)
        logging.debug("loading config before adding game : ")
        logging.debug(self.lutris_config.config)
        #Load game box
        self.installer_config_vbox = InstallerConfigVBox(self.lutris_config)
        self.installer_config_scrolled_window.add_with_viewport(self.installer_config_vbox)
        self.installer_config_scrolled_window.show_all()

        #Load runner box
        self.runner_options_vbox = RunnerConfigVBox(self.lutris_config)
        self.runner_config_scrolled_window.add_with_viewport(self.runner_options_vbox)
        self.runner_config_scrolled_window.show_all()

        #Load system box
        self.system_config_vbox = SystemConfigVBox(self.lutris_config)
        self.system_config_scrolled_window.add_with_viewport(self.system_config_vbox)
        self.system_config_scrolled_window.show_all()


    def close(self, widget=None, other=None):
        self.destroy()

    def no_runner_selected(self):
        no_runner_label = gtk.Label("Choose a runner from the list")
        no_runner_label.show()
        self.runner_config_scrolled_window.add_with_viewport(no_runner_label)



