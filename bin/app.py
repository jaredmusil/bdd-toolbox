# -*- coding: utf-8 -*-

"""
This Program contains various convenience functions useful for BDD style
tests development. For example the tags tab will scan a given folder for
.story files and make a unique list of all the @tag TAG: annotations.
This list is then used for requirements tracking and work assignments.
Additionally the metrics and tests tabs can be used to satisfy release
requirements and quickly perform local tests.

Author:   Jared Musil
Email:    jared.musil.kbw5@gmail.com
"""

# New Features
# TODO  Tags tab totals
# TODO  Test tab integration with jenkins
# TODO  Refactor to MVC design

# Bugs
# TODO load regular filepaths, not the "//" eacaped slashes filepath
# TODO Highlight bad syntax

import os
import re
import csv
import json
import time
import webbrowser
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from tkinter.filedialog import asksaveasfile

import selenium_server_standalone

__author__ = "Jared Musil"
__email__ = "jared.musil@gmail.com"

class BDDToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title('BDD Toolbox')
        #self.root.iconbitmap(os.path.dirname(os.path.abspath('__file__')) + '\\img\\logo.ico')

        # TODO Finish splash screen - add state messages like "Creating GUI | loading settings | updating tabs |"
        with SplashScreen(root, 'img\\splash-screen.gif', 2):
            self.__init_variables()
            self.__load_settings()
            self.__load_requirements_from_settings()
            self.__init_widgets(root)

            # if config.json is present, then pre-load the data file paths
            # try:
            #self.update_stories()
            # except:
            #    self.show_error("config.json file is missing or corrupt. Please manually enter your file locations")

    def __init_variables(self):
        print('- Initialising variables')
        self.app_root = os.path.dirname(os.path.abspath('__file__'))
        self.data_root = self.app_root + '\\data'
        self.results_root = self.data_root + '\\results'
        # TODO implement save method using results directory

        self.settings = {}
        self.stories = []
        self.metatags_key = []
        self.metatags_key_value = []
        self.sites = {}
        self.filepath_stories = tk.StringVar()
        self.requirement_number = 0
        self.img = Icons()

        self.requirement = tk.StringVar()
        self.metatag = tk.StringVar()
        self.metatag_stories = tk.StringVar()
        self.metatag_scenerios = tk.StringVar()
        self.metatag_coverage = tk.StringVar()
        self.count_requirements = tk.StringVar()
        self.count_stories = tk.StringVar()
        self.count_scenerios = tk.StringVar()
        self.coverage_requirements = tk.StringVar()

        # These should all get overwritten with real values before they are displayed to the user...
        self.requirement.set('NA')
        self.metatag.set('NA')
        self.metatag_stories.set('NA')
        self.metatag_scenerios.set('NA')
        self.metatag_coverage.set('NA')
        self.count_requirements.set('NA')
        self.count_stories.set('NA')
        self.count_scenerios.set('NA')

    def __init_widgets(self, parent):
        print('- Creating GUI')
        # root geometry
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # add tabs
        self.nb = ttk.Notebook(root)
        self.nb.grid(row=0, column=0, sticky=tk.NSEW)

        self.__init_data()
        self.__init_menu()
        self.__init_tabs(self.nb)
        self.__init_tab_data()

    def __init_data(self):
        print('--- Processing Settings')
        self.count_requirements.set(len(self.read_all_requirements('Usecases')))
        self.count_stories.set(len(self.read_all_stories()))
        self.count_scenerios.set(len(self.read_all_scenerios()))

        reqs = int(self.count_requirements.get())
        stories = int(self.count_stories.get())
        scenerios = int(self.count_scenerios.get())
        prompt_user_for_data = ((reqs == 0) or (stories == 0) or (scenerios == 0))

        attempts = 0
        if (prompt_user_for_data):
            while (attempts < 3):
                with InitSettings(root):
                    attempts += 1

    def __init_menu(self):
        print('--- Creating Menu')

        menu = tk.Menu(root)

        file = tk.Menu(menu, tearoff=0)
        file.add_command(label="Load Settings", command=lambda: self.update_label_filepath(self.filepath_stories))
        file.add_command(label="Configure Settings", command=self.show_settings)
        file.add_separator()
        file.add_command(label="Save Stories", command=lambda: self.save('stories.txt', self.read_all_stories()))
        file.add_command(label="Save Scenerios", command=lambda: self.save('scenerios.txt', self.read_all_scenerios()))
        file.add_command(label="Save Stories & Scenerios", command=lambda: self.save('stories-and-scenerios.txt', self.read_all_stories_and_scenerios()))
        file.add_command(label="Save Stories, Scenerios, & Steps", command=lambda: self.save('stories-scenerios-steps.txt', self.read_all_stories_scenerios_and_steps()))
        menu.add_cascade(label="File", menu=file)

        edit = tk.Menu(menu, tearoff=0)
        edit.add_command(label="Selenium Server", command=lambda: self.on_selenium_server_start)
        edit.add_command(label="Selenium Server As User", command=lambda: self.on_selenium_server_start_as)
        menu.add_cascade(label="Run", menu=edit)

        edit = tk.Menu(menu, tearoff=0)
        edit.add_command(label="jBehave", command=lambda: webbrowser.open('http://jbehave.org/'))
        edit.add_command(label="Serenity", command=lambda: webbrowser.open('http://thucydides.info/docs/serenity/'))
        edit.add_command(label="Selenium", command=lambda: webbrowser.open('http://www.seleniumhq.org/docs/'))
        menu.add_cascade(label="Documentation", menu=edit)

        help = tk.Menu(menu, tearoff=0)
        help.add_command(label="About...", command=self.show_about)
        menu.add_cascade(label="Help", menu=help)

        root.config(menu=menu)

    def __init_tabs(self, parent):
        self.__init_tab_requirements(parent)
        self.__init_tab_browse(parent)
        self.__init_tab_tag(parent)
        self.__init_tab_execute(parent)

    def __init_tab_data(self):
        self.update_variables()

        # Requirements Tab
        self.update_tab_requirements()

        # Browse Tab
        self.nb.tab_browse.pane.combobox_meta['values'] = self.metatags_key
        self.nb.tab_browse.pane.combobox_meta.current(0)

        selection = self.nb.tab_browse.pane.combobox_meta.get()

        self.populate_meta_tree(self.filepath_stories.get(), '@metatag')
        self.populate_test_tree(self.nb.tab_browse.pane.tree_bdd)

        # Tag Tab
        self.populate_story_tree(self.nb.tab_tag.pane.top.pane.left.tree)

    def __init_tab_requirements(self, parent):
        print('--- Creating Tab Requirements')
        parent.tab_requirements = ttk.Frame()
        tab = parent.tab_requirements
        parent.add(tab, text='Requirements')

        # variables
        tab.selected_requirement = tk.StringVar()
        tab.selected_requirement.set("Usecases")

        # widgets
        tab.settings = ttk.Frame(tab)
        tab.settings.combobox = ttk.Combobox(tab.settings, textvariable=tab.selected_requirement, state='readonly')
        tab.settings.combobox.bind("<<ComboboxSelected>>", self.on_requirements_combobox_change)
        tab.settings.button = ttk.Button(tab.settings, text='Settings', command=self.show_settings, image=self.img.settings, compound=tk.RIGHT)
        tab.requirement = ttk.Frame(tab)
        tab.footer = ttk.Frame(tab)
        tab.footer.requirements_label = ttk.Label(tab.footer, text='Requirements:')
        tab.footer.requirements_val = ttk.Label(tab.footer, textvar=self.count_requirements)
        tab.footer.coverage_label = ttk.Label(tab.footer, text='Coverage:')
        tab.footer.coverage_val = ttk.Label(tab.footer, text='TODO ##%')
        tab.footer.url_label = ttk.Label(tab.footer, text='Link:')
        tab.footer.url_val = ttk.Label(tab.footer, text='TODO: Lotus Notes URL to go here...')

        # geometry
        tab.settings.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(5, 0))
        tab.settings.combobox.grid(row=0, column=0, sticky=tk.EW, padx=5)
        tab.settings.button.grid(row=0, column=1, sticky=tk.E)
        tab.requirement.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        tab.footer.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=(0, 5))
        tab.footer.requirements_label.grid(row=0, column=0, sticky=tk.NSEW)
        tab.footer.requirements_val.grid(row=0, column=1, sticky=tk.NSEW)
        tab.footer.coverage_label.grid(row=0, column=2, sticky=tk.NSEW)
        tab.footer.coverage_val.grid(row=0, column=3, sticky=tk.NSEW)
        tab.footer.url_label.grid(row=0, column=4, sticky=tk.NSEW)
        tab.footer.url_val.grid(row=0, column=5, sticky=tk.NSEW)

        # weights
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        tab.settings.grid_columnconfigure(0, weight=1)
        tab.requirement.grid_rowconfigure(1, weight=1)
        tab.requirement.grid_columnconfigure(0, weight=1)

    #def __init_tab_testcases(self, parent):
    #    parent.tab_stories = ttk.Frame()
    #    tab = parent.tab_stories
    #    parent.add(tab, text='Testcases')
    #
    #    #tab.columns = ('Tests')
    #    # tab.story_filepath = tk.StringVar()
    #    # tab.story_filepath.set(filepath_stories.get())
    #
    #    # widgets
    #    tab.settings = ttk.Frame(tab)
    #    tab.settings.entry = ttk.Entry(tab.settings, textvariable=self.filepath_stories)
    #    tab.settings.entry.bind('<Return>', lambda event: self.update_stories())
    #    tab.settings.button = ttk.Button(tab.settings, text='Browse', command=lambda: self.update_label_filepath(self.filepath_stories))
    #    tab.stories = ttk.Frame(tab)
    #    tab.tree_bdd = ttk.Treeview(tab.stories)#, columns=tab.columns)
    #    tab.tree_bdd.bind("<Double-3>", lambda event, t=tab: self.show_editor(t))
    #    # tab.tree['show'] = 'headings'
    #    #tab.tree.heading(text='Tests', column=0, command=lambda c=0: sortby(tab.tree, c, 0))
    #    #tab.tree.column('Tests', width=400)
    #    tab.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.tree_bdd.yview)
    #    tab.xscroll = ttk.Scrollbar(orient=tk.HORIZONTAL, command=tab.tree_bdd.xview)
    #    tab.footer = ttk.Frame(tab)
    #  # tab.footer.show = ttk.LabelFrame(tab.footer, text='Show')
    #    # tab.footer.display_scenerios = ttk.Checkbutton(tab.footer, text='Scenerios')
    #    # tab.footer.display_stories = ttk.Checkbutton(tab.footer, text='Stories')
    #
    #   # geometry
    #    tab.settings.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=(5, 0))
    #    tab.settings.entry.grid(row=0, column=0, sticky=tk.EW, padx=5)
    #    tab.settings.button.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5))
    #    tab.stories.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
    #    tab.tree_bdd.grid(in_=tab.stories, row=0, column=0, sticky=tk.NSEW)
    #    tab.yscroll.grid(in_=tab.stories, row=0, column=1, sticky=tk.NS)
    #    tab.xscroll.grid(in_=tab.stories, row=1, column=0, sticky=tk.EW)
    #    tab.footer.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=(0, 5))
    #
    #
    #    # weights
    #    tab.grid_columnconfigure(0, weight=1)
    #    tab.grid_rowconfigure(1, weight=1)
    #    tab.settings.grid_columnconfigure(0, weight=1)
    #    tab.stories.grid_rowconfigure(0, weight=1)
    #    tab.stories.grid_columnconfigure(0, weight=1)
    #
    #    tab.tree_bdd['yscroll'] = tab.yscroll.set
    #    tab.tree_bdd['xscroll'] = tab.xscroll.set
    #
    #    self.populate_tests(tab.tree_bdd)
    #
    #    tab.tree_bdd.tag_configure('invalid', background='red')
    #
    # def __init_tab_stories(self, parent):
    #     parent.tab_stories = ttk.Frame()
    #     tab = parent.tab_stories
    #     parent.add(tab, text='Stories')
    #
    #     tab.columns = ('Story')
    #     # tab.story_filepath = tk.StringVar()
    #     # tab.story_filepath.set(filepath_stories.get())
    #
    #     # widgets
    #     tab.settings = ttk.Frame(tab)
    #     tab.settings.entry = ttk.Entry(tab.settings, textvariable=self.filepath_stories)
    #     tab.settings.entry.bind('<Return>', lambda event: self.update_stories())
    #     tab.settings.button = ttk.Button(tab.settings, image=self.img.open, command=lambda: self.update_label_filepath(self.filepath_stories))
    #     tab.stories = ttk.Frame(tab)
    #     tab.tree = ttk.Treeview(tab.stories, columns=tab.columns)
    #     tab.tree.bind("<Double-3>", lambda event, t=tab: self.show_editor(t))
    #     tab.tree['show'] = 'headings'
    #     tab.tree.heading(text='Story', column=0, command=lambda c=0: sortby(tab.tree, c, 0))
    #     tab.tree.column('Story', width=400)
    #     tab.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.tree.yview)
    #     tab.xscroll = ttk.Scrollbar(orient=tk.HORIZONTAL, command=tab.tree.xview)
    #     tab.footer = ttk.Frame(tab)
    #     tab.footer.save_stories = ttk.Button(tab.footer, text='Save Stories', command=lambda: self.save('stories.txt', self.read_all_stories()))
    #     tab.footer.save_scenerios = ttk.Button(tab.footer, text='Save Scenerios', command=lambda: self.save('stories.txt', self.read_all_scenerios()))
    #
    #     # geometry
    #     tab.settings.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=(5, 0))
    #     tab.settings.entry.grid(row=0, column=0, sticky=tk.EW, padx=5)
    #     tab.settings.button.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5))
    #     tab.stories.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
    #     tab.tree.grid(in_=tab.stories, row=0, column=0, sticky=tk.NSEW)
    #     tab.yscroll.grid(in_=tab.stories, row=0, column=1, sticky=tk.NS)
    #     tab.xscroll.grid(in_=tab.stories, row=1, column=0, sticky=tk.EW)
    #     tab.footer.grid(row=2, column=0, sticky=tk.NSEW, padx=0, pady=(0, 5))
    #     tab.footer.save_stories.grid(row=0, column=0, sticky=tk.EW, padx=5)
    #     tab.footer.save_scenerios.grid(row=0, column=1, sticky=tk.EW, padx=5)
    #
    #     # weights
    #     tab.grid_columnconfigure(0, weight=1)
    #     tab.grid_rowconfigure(1, weight=1)
    #     tab.settings.grid_columnconfigure(0, weight=1)
    #     tab.stories.grid_rowconfigure(0, weight=1)
    #     tab.stories.grid_columnconfigure(0, weight=1)
    #
    #     tab.tree['yscroll'] = tab.yscroll.set
    #     tab.tree['xscroll'] = tab.xscroll.set
    #
    #     self.populate_stories(tab)
    #
    #     tab.tree.tag_configure('invalid', background='red')
    #
    # def __init_tab_scenerios(self, parent):
    #     parent.tab_scenerios = ttk.Frame()
    #     tab = parent.tab_scenerios
    #     parent.add(tab, text='Scenerios')
    #
    #     tab.columns = ('Scenerios')
    #     # tab.story_filepath = tk.StringVar()
    #     # tab.story_filepath.set(filepath_stories.get())
    #
    #     # widgets
    #     tab.settings = ttk.Frame(tab)
    #     tab.settings.entry = ttk.Entry(tab.settings, textvariable=self.filepath_stories)
    #     tab.settings.entry.bind('<Return>', lambda event: self.update_stories())
    #     tab.settings.button = ttk.Button(tab.settings, image=self.img.open, command=lambda: self.update_label_filepath(self.filepath_stories))
    #     tab.scenerios = ttk.Frame(tab)
    #     tab.tree = ttk.Treeview(tab.scenerios, columns=tab.columns)
    #     tab.tree['show'] = 'headings'
    #     tab.tree.heading(text='Scenerios', column=0, command=lambda c=0: sortby(tab.tree, c, 0))
    #     tab.tree.column('Scenerios', width=400)
    #     tab.tree.bind("<Double-3>", lambda event, t=tab: self.show_editor(t))
    #     tab.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.tree.yview)
    #     tab.xscroll = ttk.Scrollbar(orient=tk.HORIZONTAL, command=tab.tree.xview)
    #     tab.footer = ttk.Frame(tab)
    #
    #     # geometry
    #     tab.settings.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=(5, 0))
    #     tab.settings.entry.grid(row=0, column=0, sticky=tk.EW, padx=5)
    #     tab.settings.button.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5))
    #     tab.scenerios.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
    #     tab.tree.grid(in_=tab.scenerios, row=0, column=0, sticky=tk.NSEW)
    #     tab.yscroll.grid(in_=tab.scenerios, row=0, column=1, sticky=tk.NS)
    #     tab.xscroll.grid(in_=tab.scenerios, row=1, column=0, sticky=tk.EW)
    #     tab.footer.grid(row=2, column=0, sticky=tk.NSEW, padx=0, pady=(0, 5))
    #
    #     # weights
    #     tab.grid_columnconfigure(0, weight=1)
    #     tab.grid_rowconfigure(1, weight=1)
    #     tab.settings.grid_columnconfigure(0, weight=1)
    #     tab.scenerios.grid_rowconfigure(0, weight=1)
    #     tab.scenerios.grid_columnconfigure(0, weight=1)
    #
    #     tab.tree['yscroll'] = tab.yscroll.set
    #     tab.tree['xscroll'] = tab.xscroll.set
    #
    #     self.populate_scenerios(tab)
    #
    #     tab.tree.tag_configure('invalid', background='red')

    def __init_tab_browse(self, parent):
        print('--- Creating Tab Browse')
        parent.tab_browse = ttk.Frame()
        tab = parent.tab_browse
        parent.add(tab, text='Browse')

        # variables
        key_columns = ("Key", "Count", "Percent", "Coverage")
        value_columns = ("Story", "Tag")
        self.meta_keys = tk.StringVar()
        self.meta_values = tk.StringVar()
        self.meta_keys.set('NA')
        self.meta_values.set('NA')

        # widgets
        tab.header = ttk.Frame(tab)
        tab.header.combobox = ttk.Entry(tab.header, textvariable=self.filepath_stories)
        tab.header.combobox.bind('<Return>', self.update_stories())
        tab.header.button = ttk.Button(tab.header, text='Browse', command=lambda: self.update_story_filepath(), image=self.img.folder, compound=tk.RIGHT)

        # left pane
        tab.pane = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        tab.pane.frame_meta = ttk.Frame(tab.pane)
        tab.pane.add(tab.pane.frame_meta)
        tab.pane.tree_meta = ttk.Treeview(tab.pane.frame_meta, columns=key_columns)
        tab.pane.tree_meta['show'] = 'headings'
        tab.pane.tree_meta.heading(text='Key', column=0, anchor=tk.W, command=lambda c=1: sortby(tab.pane.tree_meta, c, 0))
        tab.pane.tree_meta.heading(text='Count', column=1, anchor=tk.W, command=lambda c=2: sortby(tab.pane.tree_meta, c, 0))
        tab.pane.tree_meta.heading(text='Percent', column=2, anchor=tk.W, command=lambda c=3: sortby(tab.pane.tree_meta, c, 0))
        tab.pane.tree_meta.heading(text='Coverage', column=3, anchor=tk.W, command=lambda c=4: sortby(tab.pane.tree_meta, c, 0))
        tab.pane.tree_meta.column('Key', width=160)
        tab.pane.tree_meta.column('Count', width=40)
        tab.pane.tree_meta.column('Percent', width=50)
        tab.pane.tree_meta.column('Coverage', width=60)
        tab.pane.tree_meta.bind("<Double-3>", lambda event, t=tab: self.show_editor(t))
        tab.pane.frame_meta_yscroll = ttk.Scrollbar(tab.pane.frame_meta, command=tab.pane.tree_meta.yview, orient='vertical')
        tab.pane.combobox_meta = ttk.Combobox(tab.pane.frame_meta, textvariable=self.metatag, state='readonly')
        tab.pane.combobox_meta.bind('<<ComboboxSelected>>', self.on_metatag_combobox_change)
        tab.pane.coverage_matrix = ttk.Button(tab.pane.frame_meta, text='Generate Coverage Matrix', command=self.show_coverage_matrix)

        # right pane
        tab.pane.frame_bdd = ttk.Frame(tab.pane)
        tab.pane.add(tab.pane.frame_bdd)
        tab.pane.tree_bdd = ttk.Treeview(tab.pane.frame_bdd)#, columns=value_columns)
        tab.pane.tree_bdd.bind("<Double-3>", lambda event, t=tab: self.show_editor(t))
        ##tab.tree_bdd['show'] = 'headings'
        ##tab.tree_bdd.heading(text='Story', column=0, anchor=tk.W, command=lambda c=0: sortby(tab.tree_bdd, c, 0))
        ##tab.tree_bdd.heading(text='Tag', column=1, anchor=tk.W, command=lambda c=1: sortby(tab.tree_bdd, c, 0))
        ##tab.tree_bdd.column('Story', width=400)
        ##tab.tree_bdd.column('Tag', width=75)
        tab.frame_bdd_yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.pane.tree_bdd.yview)
        tab.frame_bdd_xscroll = ttk.Scrollbar(orient=tk.HORIZONTAL, command=tab.pane.tree_bdd.xview)

        # footer
        tab.footer = ttk.Frame(tab)
        tab.footer.label_keys = ttk.Label(tab.footer, text='Keys:')
        tab.footer.label_keys_count = ttk.Label(tab.footer, textvar=self.meta_keys)
        tab.footer.label_value = ttk.Label(tab.footer, text='Values:')
        tab.footer.label_value_count = ttk.Label(tab.footer, textvar=self.meta_values)
        tab.footer.count_stories = ttk.Label(tab.footer, text='Stories:')
        tab.footer.count_stories_count = ttk.Label(tab.footer, textvar=self.count_stories)
        tab.footer.count_scenerios = ttk.Label(tab.footer, text='Scenerios:')
        tab.footer.count_scenerios_count = ttk.Label(tab.footer, textvar=self.count_scenerios)
        tab.footer.how_to_edit_stories_text = ttk.Label(tab.footer, text='To edit individual steps in a selected story, double right-click on a selected story to open the BDD story editor.')
        #TODO create global boolean variable to toggle 'show full filepath' for stories
        #tab.checkbox_full_filepath = ttk.Checkbutton(tab.footer, text='Show full filepath?', variable=self.show_tag_value_filepath)

        # geometry
        tab.header.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        tab.header.combobox.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
        tab.header.button.grid(row=0, column=1, sticky=tk.EW)
        # tab.settings_button.grid(row=0, column=1, sticky=tk.E)
        tab.pane.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=(0, 5))
        tab.pane.tree_meta.grid(row=0, column=0, sticky=tk.NSEW)
        tab.pane.frame_meta_yscroll.grid(row=0, column=1, sticky=tk.NS)
        tab.pane.combobox_meta.grid(row=1, column=0, pady=(5, 5), sticky=tk.EW)
        tab.pane.coverage_matrix.grid(row=2, column=0, pady=(0, 5), sticky=tk.EW)
        tab.pane.tree_bdd.grid(in_=tab.pane.frame_bdd, row=0, column=0, sticky=tk.NSEW)
        tab.frame_bdd_yscroll.grid(in_=tab.pane.frame_bdd, row=0, column=1, sticky=tk.NS)
        tab.frame_bdd_xscroll.grid(in_=tab.pane.frame_bdd, row=1, column=0, sticky=tk.EW)
        tab.footer.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=0)
        tab.footer.label_keys.grid(row=0, column=0, sticky=tk.NSEW, padx=0)
        tab.footer.label_keys_count.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5))
        tab.footer.label_value.grid(row=1, column=0, sticky=tk.NSEW, padx=0)
        tab.footer.label_value_count.grid(row=1, column=1, sticky=tk.NSEW, padx=(0, 5))
        tab.footer.count_stories.grid(row=0, column=2, sticky=tk.NSEW, padx=0)
        tab.footer.count_stories_count.grid(row=0, column=3, sticky=tk.NSEW, padx=(0, 5))
        tab.footer.count_scenerios.grid(row=1, column=2, sticky=tk.NSEW, padx=0)
        tab.footer.count_scenerios_count.grid(row=1, column=3, sticky=tk.NSEW, padx=(0, 5))
        tab.footer.how_to_edit_stories_text.grid(row=0, column=4, sticky=tk.NSEW, padx=(5, 5))
        #tab.checkbox_full_filepath.grid(row=0, column=10, sticky=tk.NSEW)

        # weight
        tab.grid_rowconfigure(1, weight=1)  # Pane
        tab.grid_columnconfigure(0, weight=1)  # meta tag treeview
        tab.header.grid_columnconfigure(0, weight=1)
        tab.pane.frame_meta.grid_rowconfigure(0, weight=1)
        tab.pane.frame_meta.grid_columnconfigure(0, weight=1)
        tab.pane.frame_bdd.grid_rowconfigure(0, weight=1)
        tab.pane.frame_bdd.grid_columnconfigure(0, weight=1)

        # actions
        tab.pane.tree_meta['yscrollcommand'] = tab.pane.frame_meta_yscroll.set
        tab.pane.tree_bdd['yscroll'] = tab.frame_bdd_yscroll.set
        tab.pane.tree_bdd['xscroll'] = tab.frame_bdd_xscroll.set

        tab.pane.tree_bdd.tag_configure('invalid', background='red')

        #self.populate_tests(tab.pane.tree_bdd)
        #self.populate_stories(tab.pane.tree_meta)

        #self.nb.tab_browse.pane.combobox_meta['values'] = self.metatags_key_value

    def __init_tab_tag(self, parent):
        print('--- Creating Tab Tag')
        parent.tab_tag = ttk.Frame()
        tab = parent.tab_tag
        parent.add(tab, text='Tag')

        # variables
        browser = tk.IntVar()
        left_headings = ('Left',)
        right_headings = ('Right',)

        # widgets
        tab.pane = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        tab.pane.top = ttk.Frame(tab.pane)
        tab.pane.add(tab.pane.top)
        tab.pane.top.pane = ttk.PanedWindow(tab.pane.top, orient=tk.HORIZONTAL)
        tab.pane.top.pane.left = ttk.Frame(tab.pane.top.pane)
        tab.pane.top.pane.add(tab.pane.top.pane.left)
        tab.pane.top.pane.left.tree = ttk.Treeview(tab.pane.top.pane.left, columns=left_headings)
        tab.pane.top.pane.left.tree['show'] = 'headings'
        tab.pane.top.pane.left.tree.heading(text='Stories Available', column=0, anchor=tk.W, command=lambda c=0: sortby(tab.pane.top.pane.left.tree, c, 0))
        tab.pane.top.pane.left.tree.column('Left', width=356)
        tab.pane.top.pane.left.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.pane.top.pane.left.tree.yview)
        tab.pane.top.pane.left.add = ttk.Label(tab.pane.top.pane.left, text='<', background='#%02x%02x%02x' % (220, 220, 220))
        tab.pane.top.pane.left.add.bind('<Button-1>', lambda e, t=tab: self.on_test_remove(t))
        tab.pane.top.pane.left.add.bind('<Enter>', lambda e: tab.pane.top.pane.left.add.config(background='#%02x%02x%02x' % (200, 200, 200)))
        tab.pane.top.pane.left.add.bind('<Leave>', lambda e: tab.pane.top.pane.left.add.config(background='#%02x%02x%02x' % (220, 220, 220)))
        tab.pane.top.pane.right = ttk.Frame(tab.pane.top.pane)
        tab.pane.top.pane.add(tab.pane.top.pane.right)
        tab.pane.top.pane.right.remove = ttk.Label(tab.pane.top.pane.right, text='>',background='#%02x%02x%02x' % (220, 220, 220))
        tab.pane.top.pane.right.remove.bind('<Button-1>', lambda e, t=tab: self.on_test_add(t))
        tab.pane.top.pane.right.remove.bind('<Enter>', lambda e: tab.pane.top.pane.right.remove.config(background='#%02x%02x%02x' % (200, 200, 200)))
        tab.pane.top.pane.right.remove.bind('<Leave>', lambda e: tab.pane.top.pane.right.remove.config(background='#%02x%02x%02x' % (220, 220, 220)))
        tab.pane.top.pane.right.tree = ttk.Treeview(tab.pane.top.pane.right, columns=right_headings)
        tab.pane.top.pane.right.tree['show'] = 'headings'
        tab.pane.top.pane.right.tree.heading(text='Stories To Add Metatag', column=0, anchor=tk.W, command=lambda c=0: sortby(tab.pane.top.pane.right.tree, c, 0))
        tab.pane.top.pane.right.tree.column('Right', width=356)
        tab.pane.top.pane.right.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.pane.top.pane.right.tree.yview)
        tab.pane.bottom = ttk.Frame(tab.pane)
        tab.pane.add(tab.pane.bottom)
        tab.pane.bottom.tag = ttk.LabelFrame(tab.pane.bottom, text='Bulk add or remove a metatag')
        tab.pane.bottom.tag.label = ttk.Label(tab.pane.bottom.tag, text='@')
        tab.pane.bottom.tag.entry = ttk.Entry(tab.pane.bottom.tag, width='18')
        tab.pane.bottom.tag.add = ttk.Button(tab.pane.bottom.tag, image=self.img.add, command=lambda: self.on_keys_double_click)
        tab.pane.bottom.tag.remove = ttk.Button(tab.pane.bottom.tag, image=self.img.delete, command=lambda: self.on_keys_double_click)
        tab.pane.bottom.log = ttk.LabelFrame(tab.pane.bottom, text='Log')
        tab.pane.bottom.log.text = tk.Text(tab.pane.bottom.log, height='16', relief=tk.FLAT, background='#%02x%02x%02x' % (240, 240, 237))
        tab.pane.bottom.log.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.pane.bottom.log.text.yview)

        # geometry
        tab.pane.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        tab.pane.top.pane.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.top.pane.left.tree.grid(row=0, column=1, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.top.pane.left.yscroll.grid(in_=tab.pane.top.pane.left, row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.top.pane.left.add.grid(row=0, column=2, sticky=tk.NSEW, padx=(0, 2), pady=0)
        tab.pane.top.pane.right.remove.grid(row=0, column=0, sticky=tk.NSEW, padx=(2, 0), pady=0)
        tab.pane.top.pane.right.tree.grid(row=0, column=1, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.top.pane.right.yscroll.grid(in_=tab.pane.top.pane.right, row=0, column=2, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.bottom.tag.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.bottom.tag.label.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 2), pady=(0, 5))
        tab.pane.bottom.tag.entry.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        tab.pane.bottom.tag.add.grid(row=0, column=2, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        tab.pane.bottom.tag.remove.grid(row=0, column=3, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        tab.pane.bottom.log.grid(row=1, column=0, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.bottom.log.text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        tab.pane.bottom.log.yscroll.grid(in_=tab.pane.bottom.log, row=0, column=1, sticky=tk.NS)

        # weights
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tab.pane.top.grid_rowconfigure(0, weight=1)
        tab.pane.top.grid_columnconfigure(0, weight=1)
        tab.pane.top.pane.left.grid_rowconfigure(0, weight=1)
        tab.pane.top.pane.left.grid_columnconfigure(1, weight=1)
        tab.pane.top.pane.right.grid_rowconfigure(0, weight=1)
        tab.pane.top.pane.right.grid_columnconfigure(1, weight=1)
        tab.pane.bottom.grid_columnconfigure(0, weight=1)
        tab.pane.bottom.grid_rowconfigure(1, weight=1)  # log fills up extra space
        #tab.pane.bottom.grid_rowconfigure(2, weight=1)
        tab.pane.bottom.tag.grid_columnconfigure(1, weight=1)  # Metatag input
        tab.pane.bottom.log.grid_columnconfigure(0, weight=1)
        tab.pane.bottom.log.grid_rowconfigure(0, weight=1)


        tab.pane.top.pane.left.tree['yscroll'] = tab.pane.top.pane.left.yscroll.set
        tab.pane.top.pane.right.tree['yscroll'] = tab.pane.top.pane.right.yscroll.set
        tab.pane.bottom.log.text['yscroll'] = tab.pane.bottom.log.yscroll.set

        # self.populate_story_tree(tab.pane.top.pane.left.tree)
        # tab.pane.top.pane.right.tree.insert('', 'end', value='', tags=('',))

    def __init_tab_execute(self, parent):
        print('--- Creating Tab Execute')
        parent.tab_execute = ttk.Frame()
        tab = parent.tab_execute
        parent.add(tab, text='Execute')

        # variables
        browser = tk.IntVar()
        webdriver_remote_url = 'http://127.0.0.1:5555/wd/hub'
        m2_settings = r'--settings C:\users\kbw5\.m2\settings.xml'
        serenity_filepath = r'file://' + self.filepath_stories.get() + r'\target\site\serenity\index.html'
        serenity_report = serenity_filepath.replace('/', '\\')
        self.relative_story_names_to_run = ''
        self.command = r'call mvn verify serenity:aggregate -Dmetafilter="+smoke" -Dwebdriver.driver=iexplorer -Dwebdriver.ie.driver=5555 -Dwebdriver.remote.url=' + webdriver_remote_url + ' -Dserenity.take.screenshots=FOR_FAILURES -Dmaven.tests.failure.ignore=true ' + m2_settings

        # widgets
        tab.body = ttk.Frame(tab)
        tab.body.metafilter = ttk.LabelFrame(tab.body, text='Metafilter')
        tab.body.metafilter.entry = ttk.Entry(tab.body.metafilter)
        tab.body.metafilter.button = ttk.Button(tab.body.metafilter, image=self.img.help, command=lambda: webbrowser.open('http://jbehave.org/reference/stable/meta-filtering.html'))
        tab.body.runas = ttk.LabelFrame(tab.body, text='Run As')
        tab.body.runas.run_as_checkbox = ttk.Checkbutton(tab.body.runas)
        tab.body.runas.username_label = ttk.Label(tab.body.runas, text='Username:')
        tab.body.runas.username_entry = ttk.Entry(tab.body.runas, width='18')
        tab.body.runas.password_label = ttk.Label(tab.body.runas, text='Password:')
        tab.body.runas.password_entry = ttk.Entry(tab.body.runas, width='18', show="*")
        tab.body.browser = ttk.LabelFrame(tab.body, text='Browser')
        tab.body.browser.ie = tk.Radiobutton(tab.body.browser, text='Internet Explorer', variable=browser, value=1, indicatoron=0)
        tab.body.browser.chrome = tk.Radiobutton(tab.body.browser, text='Chrome', variable=browser, value=2, indicatoron=0)
        tab.body.browser.firefox = tk.Radiobutton(tab.body.browser, text='FireFox', variable=browser, value=3, indicatoron=0)
        tab.body.browser.phantomjs = tk.Radiobutton(tab.body.browser, text='PhantomJS', variable=browser, value=4, indicatoron=0)
        tab.body.test = ttk.LabelFrame(tab.body, text='Test')
        tab.body.test.run = ttk.Button(tab.body.test, text='Run Tests', command=lambda: self.on_test_execution(tab.body))
        tab.body.test.results = ttk.Button(tab.body.test, text='View Results', command=lambda: webbrowser.open(serenity_report))
        tab.body.maven = ttk.LabelFrame(tab.body, text='Maven')
        tab.body.maven.show_hide = ttk.Label(tab.body.maven, text='+', background='#%02x%02x%02x' % (220, 220, 220))
        tab.body.maven.show_hide.bind('<Button-1>', lambda e: print('Expand maven command'))
        tab.body.maven.text = tk.Text(tab.body.maven, height='1', relief=tk.FLAT, background='#%02x%02x%02x' % (240, 240, 237))
        tab.body.maven.text.insert(tk.INSERT, self.command)
        tab.body.log = ttk.LabelFrame(tab.body, text='Log')
        tab.body.log.text = tk.Text(tab.body.log, height='16', relief=tk.FLAT, background='#%02x%02x%02x' % (240, 240, 237))
        tab.body.log.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.body.log.text.yview)

        # geometry
        tab.body.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        tab.body.metafilter.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW, padx=(0, 0), pady=(0, 0))
        tab.body.metafilter.entry.grid(row=0, column=0, sticky=tk.NSEW, padx=(5, 0), pady=(0, 5))
        tab.body.metafilter.button.grid(row=0, column=1, sticky=tk.NSEW, padx=(5, 0), pady=(0, 5))
        tab.body.runas.grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(0, 0))
        tab.body.runas.run_as_checkbox.grid(row=0, column=0, sticky=tk.NSEW, padx=(5, 0), pady=(0, 5))
        tab.body.runas.username_label.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 2), pady=(0, 5))
        tab.body.runas.username_entry.grid(row=0, column=2, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        tab.body.runas.password_label.grid(row=0, column=3, sticky=tk.NSEW, padx=(0, 2), pady=(0, 5))
        tab.body.runas.password_entry.grid(row=0, column=4, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        tab.body.browser.grid(row=1, column=1, sticky=tk.NSEW, padx=(0, 5), pady=0)
        tab.body.browser.ie.grid(row=0, column=0, sticky=tk.NSEW, padx=(5, 0), pady=(0, 5))
        tab.body.browser.chrome.grid(row=0, column=1, sticky=tk.NSEW, padx=(5, 0), pady=(0, 5))
        tab.body.browser.firefox.grid(row=0, column=2, sticky=tk.NSEW, padx=(5, 0), pady=(0, 5))
        tab.body.browser.phantomjs.grid(row=0, column=3, sticky=tk.NSEW, padx=(5, 5), pady=(0, 5))
        tab.body.test.grid(row=1, column=2, sticky=tk.NSEW)
        tab.body.test.run.grid(row=0, column=0, sticky=tk.NSEW, padx=(5, 5), pady=(0, 5))
        tab.body.test.results.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        tab.body.maven.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW, padx=0, pady=0)
        tab.body.maven.text.grid(row=0, column=0, sticky=tk.NSEW, padx=(5, 2), pady=(0, 5))
        tab.body.maven.show_hide.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        tab.body.log.grid(row=3, column=0, columnspan=3, sticky=tk.NSEW, padx=0, pady=(0, 0))
        tab.body.log.text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=(0, 5))
        tab.body.log.yscroll.grid(in_=tab.body.log, row=0, column=1, sticky=tk.NS)

        # weights
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tab.body.grid_columnconfigure(0, weight=1)
        tab.body.grid_rowconfigure(3, weight=1)
        tab.body.metafilter.grid_columnconfigure(0, weight=1)
        tab.body.runas.grid_columnconfigure(2, weight=1)
        tab.body.runas.grid_columnconfigure(4, weight=1)
        tab.body.maven.grid_rowconfigure(0, weight=1)
        tab.body.maven.grid_columnconfigure(0, weight=1)
        tab.body.log.grid_rowconfigure(0, weight=1)
        tab.body.log.grid_columnconfigure(0, weight=1)

        # actions
        tab.body.log.text['yscroll'] = tab.body.log.yscroll.set

        #self.populate_story_tree(tab.pane.top.pane.left.tree)
        # tab.pane.top.pane.right.tree.insert('', 'end', value='', tags=('',))

    def __init_footer(self):
        # widgets
        self.footer = ttk.Frame(root)
        self.footer.label = ttk.Label(self.footer, text='Story file location not yet set')
        # self.footer.save = ttk.Button(self.footer, image=self.img.run, command=lambda: self.save())

        # geometry
        self.footer.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        self.footer.label.grid(row=0, column=0, sticky=tk.NSEW)
        # self.footer.save.grid(row=0, column=4, sticky=tk.NSEW)

        # weights
        self.footer.grid_columnconfigure(0, weight=1)

    # -----------------------------------------------------------------------------

    def __load_settings(self):
        print('- Loading Settings')
        try:
            with open(self.data_root + '\\settings.json', encoding="utf8") as settings_filepath:
                self.settings = json.load(settings_filepath)
            self.filepath_stories.set(self.settings['Stories'])

        except:
            # TODO refactor show_error() into a popup / modal
            self.show_error("config.json file is missing or corrupt. Please manually enter your file locations")

    def __load_requirements_from_settings(self):
        # TODO check if requirements are null
        print(self.settings)
        for key, value in self.settings['Requirements'].items():
            self.settings[key] = tk.StringVar()
            self.settings[key].set(value)
        print("SETTINGS", self.settings)

    def read_usecase_headers(self):
        selection = self.nb.tab_requirements.settings.combobox.get()

        for requirement in self.settings.keys():
            if selection == requirement:
                filepath = self.settings[requirement].get()

        file = open(filepath, encoding="utf8")
        data = csv.reader(file)
        headers = next(data)
        return tuple(headers)

    def read_metatags(self, directory):
        list_of_metatags = []
        for path, directorys, files in os.walk(directory):
            for file in files:
                with open(path + '\\' + file, 'r') as story:
                    for line in story:
                        if '@' in line and '@' == line[0]:
                            if line not in list_of_metatags:
                                list_of_metatags.append(line)

        if len(list_of_metatags) <= 0:
            list_of_metatags.append('No @metatags found')

        self.metatags_key_value = sorted(list_of_metatags)

    def read_metatags_key_only(self, directory):
        list_of_metatags = []
        for path, directorys, files in os.walk(directory):
            for file in files:
                with open(path + '\\' + file, 'r') as story:
                    for line in story:
                        # Only select metadata, AKA lines that start with "@"
                        if '@' in line and '@' == line[0]:
                            # Now that we know its metadata, strip away any trailing data
                            # Example:
                            #    "@usecase 5" becomes "@usecase"
                            #    "@requirement 14" becomes "@requirement"
                            line_split = line.split(' ')
                            metatag_key = line_split[0]

                            # filter out repeated metatag keys
                            if metatag_key not in list_of_metatags:
                                list_of_metatags.append(metatag_key)

        # If the directory has not been set, this will likely have a length of zero
        if len(list_of_metatags) <= 0:
            list_of_metatags.append('No key / value metatags found')

        self.metatags_key = sorted(list_of_metatags)

    def read_story(self, name):
        text = ''
        for path, directorys, files in os.walk(self.filepath_stories.get()):
            for file in files:
                if file == name:
                    with open(path + '\\' + file, 'r') as story:
                        for line in story:
                            text += line
        return text

    def read_scenerios_in_file(self, directory, filename):
        scenerios = []

        with open(directory + '/' + filename, 'r') as story:
            for line in story:
                if "Scenario:" == line[:9]:
                    scenerios.append(line)
        return scenerios

    def read_scenerios_and_steps_in_file(self, directory, filename):
        steps = []

        with open(directory + '/' + filename, 'r') as story:
            for line in story:
                if "scenario:" == line[:9].lower():
                    steps.append('-- ' + line)
                if (
                    'given' == line[:5].lower() or
                    'when' == line[:4].lower() or
                    'then' == line[:4].lower() or
                    'and' == line[:3].lower()
                ): steps.append('---- ' + line)
        return steps

    def read_metatag_data(self, directory, metatag, with_stories):
        metatags = []
        for path, directorys, files in os.walk(directory):
            for file in files:
                story_specific_metatags = self.read_metatag_data_with_filename(path, file, metatag, with_stories)
                metatags.extend(story_specific_metatags)

        if not with_stories:
            metatags = self.filter_unique_list(metatags)

        return sorted(metatags)

    def read_metatag_data_with_filename(self, path, file, metatag, with_stories):
        metatags = []
        with open(path + '/' + file, 'r') as story:
            for line in story:
                if metatag in line:
                    if with_stories:
                        offset = len(metatag) + len(': ')
                        metatags.append(file + ' ' + line[offset:])
                    else:
                        l = line.partition(':')[2]
                        metatags.append(l[1:])
        return metatags

    def read_stories(self, directory):
        stories = []
        for path, directorys, files in os.walk(directory):
            for file in files:
                if file.endswith('.story'):
                    stories.append(file)
        return sorted(stories)

    def read_all_stories(self):
        stories = []
        filepath = self.filepath_stories.get()

        for path, dirs, files in os.walk(filepath):
            for file in files:
                stories.append(file)
        stories.sort()
        return stories

    def read_all_scenerios(self):
        scenerios = []
        filepath = self.filepath_stories.get()

        for path, dirs, files in os.walk(filepath):
            for file in files:
                scenerios_in_file = self.read_scenerios_in_file(path, file)
                scenerios.extend(scenerios_in_file)
        scenerios.sort()
        return scenerios

    def read_all_stories_and_scenerios(self):
        combined = []
        filepath = self.filepath_stories.get()

        for path, dirs, files in os.walk(filepath):
            for file in files:
                combined.append(file)
                scenerios_in_file = self.read_scenerios_in_file(path, file)
                for scenerio in scenerios_in_file:
                    combined.append('-- ' + scenerio)
        return combined

    def read_all_stories_scenerios_and_steps(self):
        combined = []
        filepath = self.filepath_stories.get()

        for path, dirs, files in os.walk(filepath):
            for file in files:
                combined.append(file)
                steps_in_file = self.read_scenerios_and_steps_in_file(path, file)
                for step in steps_in_file:
                    combined.append(step)
        return combined

    def read_all_requirements(self, requirement):
        #TODO try/catch bad settings.json file
        try:
            file = open(self.settings[requirement].get(), encoding="utf8")
        except:
            print('Bad settings.json requirement, prompting for file')
            file = askopenfilename(title='Load a requirements file (.json only)', filetypes=((".json files","*.json"),("all files","*.*")))

        data = csv.reader(file)

        requirements = []
        for row in data:
            requirements.append(row[0])
        requirements.pop(0)  # Dont count the header
        return requirements

    def find_story_from_scenerio(self, scenerio):
        found_story = ''
        filepath = self.filepath_stories.get()
        for path, dirs, files in os.walk(filepath):
            for file in files:
                with open(filepath + '/' + file, 'r') as story:
                    for line in story:
                        if line == scenerio:
                            found_story = story
                            break
        return found_story

    def get_selected_story(self):
        return self.metatag.get()

    def get_selected_requirement(self):
        return self.nb.tab_requirements.settings.combobox.get()

    def create_setting(self, parent, key, value):
        index = self.requirement_number

        setting = self.settings[key]
        label = ttk.Label(parent, text=key)
        entry = ttk.Entry(parent, textvariable=self.settings[key], width=60)
        button = ttk.Button(parent, image=self.img.open, command=lambda: self.update_label_filepath(setting))

        label.grid(row=index, column=0, sticky=tk.EW, padx=(0, 0), pady=(5, 0))
        entry.grid(row=index, column=1, sticky=tk.NSEW, padx=(5, 0), pady=(5, 0))
        button.grid(row=index, column=2, sticky=tk.EW, padx=(5, 0), pady=(5, 0))

        # parent.grid_columnconfigure(index, weight=1)

        self.requirement_number += 1

    def get_maven_command(self):
        webdriver_remote_url = r'http://127.0.0.1:5555/wd/hub'
        webdriver_driver = r'iexplorer'
        webdriver_ie_driver = r'5555'
        serenity_take_screenshots = r'FOR_FAILURES'
        m2_settings = r'--settings C:\users\kbw5\.m2\settings.xml'

        command = r'call mvn'\
                  + ' tests'\
                  + ' serenity:aggregate'\
                  + ' -Dwebdriver.driver=' + webdriver_driver\
                  + ' -Dwebdriver.ie.driver=' + webdriver_ie_driver\
                  + ' -Dwebdriver.remote.url=' + webdriver_remote_url\
                  + ' -Dserenity.take.screenshots=' + serenity_take_screenshots\
                  + ' -Dmaven.tests.failure.ignore=true ' \
                  + ' -Dmetafilter="+smoke'\
                  + m2_settings

                  # + self.relative_story_names_to_run \

                  #+ ' -DrelativeStoryNamesToRun=' + self.relative_story_names_to_run\
                  #+ ' -DincludeAllSubFoldersInStoryPath=' + include_all_sub_folders_in_story_path\
        return command

    def create_tree_requirements_widgets(self):
        # variables
        tab = self.nb.tab_requirements
        tab.columns = self.read_usecase_headers()

        # frame widgets
        tab.requirement.treeview = ttk.Treeview(tab.requirement, columns=tab.columns)
        tab.requirement.treeview['show'] = 'headings'
        tab.requirement.treeview.heading(text='1', column=0, anchor=tk.W, command=lambda c=0: sortby(tab.requirement.treeview, c, 0))
        tab.requirement.treeview.heading(text='2', column=1, anchor=tk.W, command=lambda c=1: sortby(tab.requirement.treeview, c, 0))
        tab.requirement.treeview.column('0', width=400)
        tab.requirement.treeview.column('1', width=100)
        tab.requirement.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=tab.requirement.treeview.yview)
        tab.requirement.xscroll = ttk.Scrollbar(orient=tk.HORIZONTAL, command=tab.requirement.treeview.xview)

        # frame widget placement
        tab.requirement.treeview.grid(in_=tab.requirement, row=1, column=0, sticky=tk.NSEW)
        tab.requirement.yscroll.grid(in_=tab.requirement, row=1, column=1, sticky=tk.NS)
        tab.requirement.xscroll.grid(in_=tab.requirement, row=2, column=0, sticky=tk.EW)

        tab.requirement.treeview['yscroll'] = tab.requirement.yscroll.set
        tab.requirement.treeview['xscroll'] = tab.requirement.xscroll.set

    def populate_test_tree(self, tree):
        print("--- Populating test tree")
        filepath = self.filepath_stories.get()
        for path, dirs, files in os.walk(filepath):
            for file in files:
                tree.insert('', 'end', file, text=file)

                scenerios = []
                with open(path + '/' + file, 'r') as story:
                    for line in story:
                        if "Scenario:" == line[:9]:
                            scenerios.append(line)
                scenerios.sort()

                for scenerio in scenerios:
                    tree.insert(file, 'end', text=scenerio)

    def populate_scenerio_tree(self, tab):
        print("--- Populating scenerio tree")
        scenerios = self.read_all_scenerios()
        for scenerio in scenerios:
            scenerio = scenerio[:-1]
            tab.tree_bdd.insert('', 'end', value=(scenerio,))

    def populate_story_tree(self, tree):
        print("--- Populating story tree")
        stories = self.read_all_stories()
        for story in stories:
            tag = 'valid'
            if ' ' in story:
                tag = 'invalid'
                print('This story contains a space in its filename:', story)
            if '.story' not in story:
                tag = 'invalid'
                print('This story does not have a lower case extension of .story', story)
            tree.insert('', 'end', value=story, tags=(tag,))

        #self.count_story.set(len(stories))

    def update_stories(self):
        #self.update_variables()

        # Only update if the dropdown is empty
        #if (len(self.get_selected_requirement()) == 0):
        #    self.update_tab_requirements_dropdown()

        # Only update if the dropdown is empty
        #if (len(self.get_selected_story()) == 0):
        #    self.update_tab_browse_meta_dropdown()

        #self.update_tabs()
        self.update_tab_browse()

    def update_variables(self):
        self.stories = []
        self.stories.extend(self.read_stories(self.filepath_stories.get()))
        try:
            self.read_metatags(self.filepath_stories.get())
            self.read_metatags_key_only(self.filepath_stories.get())
        except:
            self.metatags_key = []
            self.metatags_key_value = ['']

    #def update_tabs(self):
    #    self.update_tab_requirements()
    #    self.update_tab_browse()

    def update_tab_requirements(self):
        print('* Updating tab - Requirements')

        # Populate dropdown
        self.nb.tab_requirements.settings.combobox['values'] = list(self.settings['Requirements'].copy().keys())

        # Populate tree
        self.create_tree_requirements_widgets()
        self.populate_requirements_tree()

        self.count_requirements.set(len(self.read_all_requirements(self.get_selected_requirement())))

    def update_tab_browse(self):
        print('* Updating tab - Browse')
        directory = self.filepath_stories.get()
        metatag = self.metatag.get()
        # values = self.read_metatag_data(directory, metatag, False)

        #if metatag[0] != '@':
        #    metatag = '@tag ' + self.metatag.get()

        #self.update_tab_browse_tree_meta(directory, metatag)
        #self.update_tab_browse_tree_bdd(directory, metatag)

    def populate_meta_tree(self, directory, prefix_metatag):
        tree = self.nb.tab_browse.pane.tree_meta
        stories = self.filepath_stories.get()

        # Toggle between all metatags, or a specific metatag key
        if prefix_metatag == '@metatag':
            metatag_list = self.metatags_key
        else:
            metatag_list = self.read_metatag_data(stories, prefix_metatag, False)

        key_count = len(metatag_list)
        value_requirement_count = 0
        value_business_rule_count = 0
        value_usecase_count = 0

        # How many distinct metatag values do we have?
        metatag_values = 0
        for index, value in enumerate(metatag_list):
            values_list = self.read_metatag_data(directory, value, True)
            metatag_values += len(values_list)

            # Keep track of predefined requirements
            if (value == '@requirement'):
                value_requirement_count += 1

            # Is this a business rule?
            if (value == '@business_rule'):
                value_business_rule_count += 1

            # Is this a usecase?
            if (value == '@usecase'):
                value_usecase_count += 1

        # clear treeview contents
        tree.delete(*tree.get_children())

        try:
            for index, value in enumerate(metatag_list):
                values_list = self.read_metatag_data(directory, value, True)
                key_count = len(values_list)
                key_percentage = '{:.1%}'.format(key_count / metatag_values)  # One decimal format (0.00%)

                count_usecases = len(self.read_all_requirements('Usecases'))
                count_business_data = len(self.read_all_requirements('Business Data'))

                # Is this a business requirement?
                if (value == '@business_rule'):
                    val_coverage = '{:.1%}'.format(key_count / count_business_data)  # One decimal format (0.00%)
                elif (value == '@usecase'):
                    val_coverage = '{:.1%}'.format(key_count / count_usecases)  # One decimal format (0.00%)
                else:
                    val_coverage = '~'  # Only provide coverage for requirements that are listed in the requirements tab

                tree.insert('', 'end', values=(value, key_count, key_percentage, val_coverage))

        except Exception as e:
            pass

        self.meta_values.set(metatag_values)
        self.meta_keys.set(key_count)

    def update_tab_browse_tree_bdd(self, directory, tag):
        tree = self.nb.tab_browse.tree_bdd
        columns = self.read_usecase_headers()

        # clear treeview contents
        tree.delete(*tree.get_children())

        try:
            for index, item in enumerate(self.read_metatag_data(directory, tag, True)):
                tree.insert('', 'end', values=item)
        except Exception as e:
            pass

    #def update_label_directory(self, label):
    #    label.set(askdirectory())

    def update_label_filepath(self, label):
        filepath = askopenfilename(initialdir='data', title='Load a settings file (.json only)', filetypes=((".json files","*.json"),("all files","*.*")))  # returns an empty string on cancel
        if filepath != '':
            label.set(os.path.join(filepath))

    def update_story_filepath(self):
        filepath = askdirectory (initialdir='', title='Where are your test .story files located?')  # returns an empty string on cancel
        if filepath != '':
            self.filepath_stories.set(os.path.join(filepath))

    def populate_requirements_tree(self):
        requirement = self.nb.tab_requirements.settings.combobox.get()
        tree = self.nb.tab_requirements.requirement.treeview
        file = open(self.settings[requirement].get(), encoding="utf8")
        data = csv.reader(file)

        # tags found - Update tags tab
        for i_row, row in enumerate(data):
            if i_row == 0:
                for i_header, header in enumerate(self.nb.tab_requirements.columns):
                    tree.heading(column=i_header, text=header, anchor=tk.W)
            else:
                tree.insert('', 'end', text=row, values=row)

    def update_tab_requirements_dropdown(self):
        self.nb.tab_requirements.settings.combobox['values'] = self.settings.keys()
        self.nb.tab_requirements.settings.combobox.current(0)

    def delete_tree_requirements_widgets(self):
        self.nb.tab_browse.requirement.treeview.delete()

    def filter_unique_list(self, sequence):
        return list(set(sequence))

    def save(self, file, list):
        file = asksaveasfile(mode='w', defaultextension=".txt")

        if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return

        for item in list:
            file.write(item[:-1] + '\n')

        file.close()

    # Actions / clicks
    # -----------------------------------------------------------------------------

    def on_test_add(self, tab):
        left = tab.pane.top.pane.left.tree
        right = tab.pane.top.pane.right.tree
        left_selection = left.item(left.selection())['values']

        if left_selection != '':
            right.insert('', 'end', text=left_selection, values=left_selection)
            left.delete(left.selection())

        stories = ''
        for line in right.get_children():
            for value in right.item(line)['values']:
                stories = stories + value + ','
        stories = stories[:-1]
        self.relative_story_names_to_run = stories + ' '
        tab.pane.bottom.maven.text.delete('1.0', 'end-1c')
        tab.pane.bottom.maven.text.insert(tk.INSERT, self.get_maven_command())

    def on_test_remove(self, tab):
        left = tab.pane.top.pane.left.tree
        right = tab.pane.top.pane.right.tree
        right_selection = right.item(right.selection())["values"]

        if right_selection != '':
            left.insert('', 'end', text=right_selection, values=(right_selection,))
            right.delete(right.focus())

        stories = ''
        for line in right.get_children():
            for value in right.item(line)['values']:
                stories = stories + value + ','
        stories = stories[:-1]
        self.relative_story_names_to_run = stories + ' '
        tab.pane.bottom.maven.text.delete('1.0', 'end-1c')
        tab.pane.bottom.maven.text.insert(tk.INSERT, self.get_maven_command())

    def on_test_execution(self, tab):
        tab.pane.bottom.log.text.insert(tk.INSERT, 'Starting Tests\nPlease be patient while they run in the background\n\n------\n\n')

        os.chdir(self.filepath_stories.get())
        os.chdir('..')
        os.chdir('..')
        os.chdir('..')
        os.chdir('..')
        input = tab.pane.bottom.maven.text.get('1.0', 'end-1c')
        input_list = input.split(' ')  # avoid the 'input line too long error' that happens when a line is > 255 chars

        process = subprocess.Popen(input_list, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            nextline = process.stdout.readline()
            if nextline == b'' and process.poll() != None:
                break
            tab.pane.bottom.log.text.insert(tk.END, nextline.decode('utf-8'))
            tab.pane.bottom.log.text.update_idletasks()

        # output = process.communicate()[0]
        exitCode = process.returncode
        process.terminate()

        # process.terminate()

        # display cmd text
        # tab.pane.bottom.log.text.insert(tk.END, output)
        # tab.pane.bottom.log.text.insert(tk.END, '\n')
        # only show errors if they actually happen
        if exitCode is not 0:
            pass
            # tab.pane.bottom.log.text.insert(tk.END,'ERROR(S):\n ')
            # tab.pane.bottom.log.text.insert(tk.END,error)
            # tab.pane.bottom.log.text.insert(tk.END,'\n')

    def on_selenium_server_start(self):
        cmd = 'java.exe -Dwebdriver.ie.driver=' + self.app_root + '\extra\IEDriverServer.exe -jar ' + self.app_root + '\extra\selenium-server-standalone-2.43.1.jar -port 5555"'
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
        output, error = process.communicate()
        print(cmd)
        process.terminate()

    def on_selenium_server_start_as(self):
        selenium_server_standalone.server()

    def on_story_edit(self, event):
        tree = self.nb.tab_stories.tree
        item = tree.item(tree.selection())["values"][0]
        print("Key click: ", item[:-1])

    def on_keys_double_click(self, event):
        tree = self.nb.tab_tags.keys_treeview
        item = tree.item(tree.selection())["values"][0]

        print("Key click: ", item[:-1])

        directory = self.filepath_stories.get()
        metatag_list = self.read_metatag_data(directory, item, False)
        self.meta_values.set(len(metatag_list))

        # TODO filter story values by user selection

    def on_metatag_combobox_change(self, event):
        combobox = self.nb.tab_browse.header.combobox
        if combobox != '':
            #self.update_stories()
            self.update_variables()
            self.update_tab_browse()

    def on_requirements_combobox_change(self, event):
        combobox = self.nb.tab_requirements.settings.combobox
        if combobox != '':
            #self.update_stories()
            self.update_variables()
            self.update_tab_requirements()

    def show_settings(self):
        top_level = tk.Toplevel()
        top_level.title('Settings')
        # TODO This will error after test execution becaue the os.path.dirname has been changed and the icon cant be found
        # top_level.iconbitmap(os.path.dirname(os.path.abspath('__file__')) + '\\img\\transparent.ico')
        top_level.iconbitmap(os.path.dirname(os.path.abspath('__file__')) + '\\img\\settings.ico')

        # widgets
        frame = ttk.Frame(top_level)
        settings = ttk.Frame(frame)
        for key, value in sorted(self.settings.items()):
            self.create_setting(settings, key, value)

        # geometry
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        settings.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # weights
        top_level.grid_rowconfigure(0, weight=1)
        top_level.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        settings.grid_columnconfigure(1, weight=1)

    def show_about(self):
        information = 'BDD Toolbox\nJared Musil\njared.musil.kbw5@gmail.com\n\nCREDITS\nFugue Icons\nURL: http://p.yusukekamiyamane.com\nLicense: CC Attribution 4.0'

        top_level = tk.Toplevel()
        top_level.title('')
        # TODO This will error after test execution becaue the os.path.dirname has been changed and the icon cant be found
        # top_level.iconbitmap(os.path.dirname(os.path.abspath('__file__')) + '\\img\\transparent.ico')

        # widgets
        frame = ttk.Frame(top_level)
        about = ttk.Frame(frame)
        background = tk.PhotoImage('about.gif')
        contents = tk.Label(frame, text=information, image=background, compound=tk.CENTER)

        # geometry
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        about.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        contents.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # weights
        top_level.grid_rowconfigure(0, weight=1)
        top_level.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        about.grid_columnconfigure(1, weight=1)

    def show_coverage_matrix(self):
        text = 'Coverage matrix to go here...'

        top_level = tk.Toplevel()
        top_level.title('')
        # TODO This will error after test execution becaue the os.path.dirname has been changed and the icon cant be found
        # top_level.iconbitmap(os.path.dirname(os.path.abspath('__file__')) + '\\img\\transparent.ico')

        # widgets
        frame = ttk.Frame(top_level)
        about = ttk.Frame(frame)
        contents = tk.Label(frame, text=text, image=self.img.information_blue, compound=tk.LEFT)

        # geometry
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        about.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        contents.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # weights
        top_level.grid_rowconfigure(0, weight=1)
        top_level.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        about.grid_columnconfigure(1, weight=1)

    def show_editor(self, tab):

        def on_save():
            # Overwrite opened file
            for path, directorys, files in os.walk(self.filepath_stories.get()):
                for file in files:
                    if file == item:
                        print('Overwriting', file)
                        f = open(path + '\\' + file, 'r+')
                        edits = text.get('1.0', 'end-1c')
                        print('----------------------------------------------------------------------------------------')
                        print(edits)
                        f.seek(0)
                        f.write(edits)
                        f.truncate()
                        f.close()
                        break
            return text

        def on_bigger():
            # Make the font 2 points bigger
            size = frame.custom_font['size']
            frame.custom_font.configure(size=size+2)

        def on_smaller():
            # Make the font 2 points smaller
            size = frame.custom_font['size']

            # if the font gets too small, it will start getting bigger. Stop it before that happens.
            if size > 2:
                frame.custom_font.configure(size=size-2)

        def on_toggle_monospaceing():
            family = frame.custom_font['family']
            if family == monospaced:
                frame.custom_font.configure(family=proportional)
            else:
                frame.custom_font.configure(family=monospaced)

        def on_hightlight_syntax():
            regexs = {}
            regexs['NARRATIVE'] = re.compile('(\W|^)(Narrative:|In order to|As a|I want to)(\W|$)')
            regexs['SCENARIO'] = re.compile('(\W|^)Scenario:(\W|$)')
            regexs['META_KEYWORD'] = re.compile('(\W|^)Meta:(\W|$)')
            regexs['META'] = re.compile('(\W|^)@(\W|$)')
            regexs['KEYWORD'] = re.compile('(\W|^)(Given|When|Then|And)(\W|$)')
            regexs['EXAMPLES_TABLE'] = re.compile('(\W|^)Examples(\W|$)')
            text.tag_configure('NARRATIVE', foreground='Blue')
            text.tag_configure('SCENARIO', foreground='Purple')
            text.tag_configure('META_KEYWORD', foreground ='Orange')
            text.tag_configure('META', foreground ='Green')
            text.tag_configure('KEYWORD', foreground='Orange')
            text.tag_configure('EXAMPLES_TABLE', foreground='Red')

            for line_index, line in enumerate(story.split('\n')):
                for regex in regexs.keys():
                    try:  # to find text to color
                        start_index, end_index = regexs[regex].search(line).span()
                        line_offset_by_one = str(1+ line_index)
                        start = line_offset_by_one + '.' + str(start_index)
                        end = line_offset_by_one + '.' + str(end_index)

                        text.tag_add(regex, start, end)
                    except:
                        pass  # regex match failed

        # item = tab.tree.item(tab.tree.selection())["values"][0]
        item = tab.pane.tree_bdd.selection()
        item = str(item)
        item = item[2:-3]

        # If the user clicked on anything other than a story, dont show the editor
        if (item[-6:] != '.story'):
            return

        story = self.read_story(item)

        # TODO allow user to edit story by choosing ascenarioo
        #     try:
        #         # get story from scenerio
        #         print('---', item[-6:], type(item))
        #         story = self.find_story_from_scenerio(item)
        #         print('$$$$$$$$$$$$$$$$$$$$$$$$')
        #     except:
        #         story = 'Selected story file "' + str(item[0]) + '" does not have a .story file extension'
        # else:
        #     story = self.read_story(item)
        #     print('+++', story, type(item))

        top_level = tk.Toplevel()
        top_level.title('')
        top_level.iconbitmap(os.path.dirname(os.path.abspath('__file__')) + '\\img\\transparent.ico')
        frame = ttk.Frame(top_level)
        monospaced = 'Lucida Sans Typewriter'
        proportional = 'TkFixedFont'

        # story = 'Scenario: This story will be replaced with the one you clicked on soon...\nMeta:\n@tag usecase: 15.0\n@tag status: Completed\nGiven I have some pre-requisite\nWhen I do some action\nThen I must see result X\nExamples:\n|A|B|\n|C|D|'
        frame.custom_font = font.Font(family=monospaced, size=10)

        # widgets
        editor = ttk.Frame(frame)
        settings = ttk.Frame(editor)
        text = tk.Text(editor, font=frame.custom_font)
        text.insert(tk.INSERT, story)

        # highlight text by default
        on_hightlight_syntax()
        # text.yscroll = ttk.Scrollbar(orient=tk.VERTICAL, command=text.yview)
        # text['yscroll'] = text.yscroll.set
        save = ttk.Button(settings, text='Save', command=on_save)
        highlight = ttk.Button(settings, text='Highlight', command=on_hightlight_syntax)
        increase_font = ttk.Button(settings, text='Increase Fontsize', command=on_bigger)
        reduce_font = ttk.Button(settings, text='Reduce Fontsize', command=on_smaller)
        toggle_font = ttk.Button(settings, text='Monospaced', command=on_toggle_monospaceing)

        # geometry
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        editor.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        # text.yscroll.grid(in_=editor, row=0, column=1, sticky=tk.NS)
        settings.grid(row=1, column=0, sticky=tk.NSEW, padx=0, pady=(5, 0))
        highlight.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=0)
        increase_font.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5), pady=0)
        reduce_font.grid(row=0, column=2, sticky=tk.NSEW, padx=(0, 5), pady=0)
        toggle_font.grid(row=0, column=3, sticky=tk.NSEW, padx=(0, 5), pady=0)
        save.grid(row=0, column=4, sticky=tk.NSEW, padx=(0, 5), pady=0)

        # weights
        top_level.grid_rowconfigure(0, weight=1)
        top_level.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        editor.grid_rowconfigure(0, weight=1)
        editor.grid_columnconfigure(0, weight=1)
        text.grid_rowconfigure(0, weight=1)
        text.grid_columnconfigure(0, weight=1)

    def show_error(self, message):
        # variables
        self.error_message = tk.StringVar()
        self.error_message.set(message)

        # wrapper
        self.error = ttk.Frame(root)
        self.error.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=(0, 5))

        # widgets
        self.error.icon = ttk.Label(self.error, image=self.img.information_blue)
        self.error.status = ttk.Label(self.error, textvariable=self.error_message)
        self.error.cancel = ttk.Button(self.error, image=self.img.delete, command=lambda:self.error.grid_remove())

        # geometry
        self.error.icon.grid(row=1, column=0, sticky=tk.NSEW)
        self.error.status.grid(row=1, column=1, sticky=tk.NSEW, padx=5)
        self.error.cancel.grid(row=1, column=3, sticky=tk.NSEW)

        # weights
        self.error.grid_columnconfigure(2, weight=1)

class SplashScreen:
    def __init__(self, root, file, wait):
        self.__root = root
        self.__file = file
        self.__wait = wait + time.clock()

    def __enter__(self):
        # Hide the root while it is built.
        self.__root.withdraw()
        # Create components of splash screen.
        window = tk.Toplevel(self.__root)
        canvas = tk.Canvas(window)
        splash = tk.PhotoImage(master=window, file=self.__file)
        # Get the screen's width and height.
        scrW = window.winfo_screenwidth()
        scrH = window.winfo_screenheight()
        # Get the images's width and height.
        imgW = splash.width()
        imgH = splash.height()
        # Compute positioning for splash screen.
        Xpos = (scrW - imgW) // 2
        Ypos = (scrH - imgH) // 2
        # Configure the window showing the logo.
        window.overrideredirect(True)
        window.geometry('+{}+{}'.format(Xpos, Ypos))
        # Setup canvas on which image is drawn.
        canvas.configure(width=imgW, height=imgH, highlightthickness=0)
        canvas.grid()
        # Show the splash screen on the monitor.
        canvas.create_image(imgW // 2, imgH // 2, image=splash)
        window.update()
        # Save the variables for later cleanup.
        self.__window = window
        self.__canvas = canvas
        self.__splash = splash

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure that required time has passed.
        now = time.clock()
        if now < self.__wait:
            time.sleep(self.__wait - now)
        # Free used resources in reverse order.
        del self.__splash
        self.__canvas.destroy()
        self.__window.destroy()
        # Give control back to the root program.
        self.__root.update_idletasks()
        self.__root.deiconify()


class StoryEditor:
    def __init__(self, root, file):
        self.__root = root
        self.__file = file


class InitSettings:
    def __init__(self, root):
        print('InitSettings class')

    def __enter__(self):
        print('enter...')
        #TODO construct init data gui
        # 1) checkout svn repo
        # 2) load requirements
        # 3) load usecases
        # 4) load story file location

    def __exit__(self):
        print('exiting initial setup...')
        self.update_stories()


class Icons:
    def __init__(self):
        # images
        self.add = tk.PhotoImage(data='R0lGODlhEAAQALMKAABy/5bG4ZDG5pLI247E9JXH2ZbF4ZDH5o7B/5LI3P///wAAAAAAAAAAAAAAAAAAACH5BAEAAAoALAAAAAAQABAAAAQ0UMlJq71Ygg3yBEHQeQookmWAjBa3EYTLpkJtH+FsDjyf5BRZoSDDAAwnkmlmBCo5qGg0AgA7')
        self.run = tk.PhotoImage(data='R0lGODlhEAAQAMZSADNIYzNIZDRJYzVKZTdMZjhNZzlNaDlOaDxQazxRaz5SbD5SbUJWb0RYcipbvUdadEpdd0teeExeeE5helBifFFkfVRmf1RngFlrhFtuhlxuh2BxiWFzi2R1jWV3jmZ4kGd5kEN+9Gt9k21/lm+Al1GD5XOEmneHnn+PpF6T/NTe9dXf9tbh9tji99rj9tzk99zl993m997n99/n+OHn+OLp+OPp+ePr+eXr+eXr+ubs+ebs+ubt+uju+eju+urv+uvv+uvw+uzx++3y++7y++7z++/z+/Dz/PD0/PH1/PL2/PP2/fT3/fX3/fX4/ff5/fn7/vv8/v///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH5BAEKAH8ALAAAAAAQABAAAAeXgH+Cg4SFhCWHiYaLi4iDjoKQkYqTkSkpIQ4ll5mbmA6RmaGgfyWig6SCqX+pJyYkIiAdGxoYFxUTEA8NfyNSv8DBv0wKfx5RKFAfTxRNCUoARwBDBX8ZTkxLSUhGREJAPz48OQF/FkUcQRE9BjoANgAzADAAfxI7ODc1NDIxLy4tWKxQUa8BgwUIDhAYIACAw4f1GC0KBAA7')
        self.open = tk.PhotoImage(data='R0lGODlhEAAQAOMJAICAAJ+fP///n19fP5+ff9+/P7+fP//fn19fX////////////////////////////yH5BAEKAA8ALAAAAAAQABAAAARE8MlJq70WaIAnOsJxIB0AnsemBRMQvudLSiZspy087Hw/1IdBYUgcGkiuYLF4pCmXxtkDMDBYr1fpg4Doer+dsHgsjgAAOw==')
        self.okay = tk.PhotoImage(data='R0lGODlhEAAQAIABAB4eHQAAACH5BAEAAAEALAAAAAAQABAAAAIjjI+pG8AK3DtRzmotwlk3TkUhtlUfWXJmoq6QeqGx99DTVAAAOw==')
        self.reset = tk.PhotoImage(data='R0lGODlhEAAQAOMJAAAAALAwF39ZBo1jBpVyHdGUDNusN+K7Uu7WgP///////////////////////////yH5BAEKAA8ALAAAAAAQABAAAARF8ElAq6XyAYK6/wIwIUZhnmYpakgRXEDQrsCcZXVB2zerj79ebhe8DSszDM5WaxWBxJWRp5FaZM+p55DFoQoDqRDWK5cjADs=')
        self.output = tk.PhotoImage(data='R0lGODlhEAAQAKUqAABCZQFGagBHbgBLcwBMcwFMdAFQeT9DRgBSewJSeAJXgQBZhANagklNTwJdiQBfiwNijwNmlAVsmwdwoV5hZAl0pmlsb25xc06LrVOOsGCdvKnV+KfY+rPa+Krf+b3f98Lh+crl+dHo+tfq+9zs++Hw/OXy/Ofz/e32/fD4/f///////////////////////////////////////////////////////////////////////////////////////yH5BAEKAD8ALAAAAAAQABAAAAaNwJ/wV6kMf5ekcjhJTY7QoQQlklivP4vW8oucQKCTWByBPkqdtDr9+FHelN9iQ6/TF9EfgsNB+P8/DYINQwQeBHl5AgJHB46PQhGSDJKVlJM/EBomJhoQJhCfn5wQPw4kDqcOI6msqw4JPwohCrO2t7RCARghIRgBGb0ZAQYfBkMAAwMAPwAFy83QiYlBADs=')
        self.delete = tk.PhotoImage(data='R0lGODlhEAAQAKU5ANshId0iItwkJN4lJd4mJuAnJ9UrK98qKuErK+QuLuEvL+kzM+c2Nt45OeQ6Ot4+PuY+Puo9Pe48POk+Pt9BQfA+PutAQOhBQeZCQudEROFGRu5DQ+9GRvRHR/JISPFKSutQUORTU/JSUvVTU+VYWPlTU/ZVVeVaWuZaWvlYWPpaWvpeXvVhYfxjY/BoaPFoaPxnZ/RubvtwcPxwcPZ7e/l7e/2EhP6MjP6Skv///////////////////////////yH5BAEKAD8ALAAAAAAQABAAAAarwJ9QaCgah8hfEYW73XCoYtJwss1grRZsZjsZhgaSLFVSrVaqUkpG+ipro1yuYzJ15KPa1xBieeQ5FRWAHiwhRTQiHxKAgBIfIjRFMRwcGwuNCxuVMUUvFhYRCY0JEaAvRS4TDAiNcggMEy5FGhetcgICgAgXGnsgB3IACAgAcgcgbgYUDgIAAwUFAwACDhRuSg8YCgQBAQQKGA/YRAYNGRAQGQ1SSeVG5D9BADs=')
        self.recover = tk.PhotoImage(data='R0lGODlhEAAQALMAAP9jAP8AAM4AAL0AAP///87OznNzcwAAAP///wAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAgALAAAAAAQABAAAARaEEl5qp0YVQI6IFV2EGRgBmRxTGMqDC9JGKuW0pas2kRBYy1fBRAQ1IBE44E4OLKYw6KTkow2Mxpoi+QM/ragXKp2KMg8n96PYigUTgH3mnUwwGA4LMUSwkQAADs=')
        self.delete_document = tk.PhotoImage(data='R0lGODlhEAAQAOcAAP///8opAJMAAPb4+v/M/4SQnfr7/Pj5+/z9/f7+/vT2+Ss2QvH1+P9MDP8zAP8pAOnu9O3y9uXs8u/z9+vw9f+DIJSfq/9sFHJ+ivr7/ff5+4+PyGBpc/n7/GNsd1dfaIGOmkpUX3aBjX6KlvP2+e7y9/n6+3B7h2Zveuzx9oSRnfH09v3+/2hyfVBZYW14hJKRy/7///j6/I6Ox//+/mBoc52evoSRnrjBx2t1gHuHk3mEkOXr8dPY3oiUn4mVoerv9Ss3QlRcZoCKlvD1+Kissejt84iUof///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH5BAEKAH8ALAAAAAAQABAAAAjRAH/cKECwoAofFv4oVAgCgMOHDmEASLhwBIAEGDMCmOGQ4h8dABCIHAlgw0OKOwAYWMkyhg0XQj4MUSgCwIGbOE2wWNEDxxGFGAAMGEp0qAYZADAoPAGAhIKnTzM4lApA4QsARBhoZdCBRoAADr/+yQGgxISzEwAEIEDgK9sALQCkiEA3AgABFSqwzSsABQAgFAJT0HD3guELAv54AGAEgmMIA9Q2mNwgwB8OAHhI2CxBLYEHDhw8aFsD4kMBoAUIEC0gRJAFsGEXuSvAoeo/AQEAOw==')
        self.information_blue = tk.PhotoImage(data='R0lGODlhEAAQAMZAABqQ1iSS3CuS1SCX2SGX2yaZ3i6Y5C6c4zSf5i2k3zCj5C2k4yul4Tuf7zmi6z6i8DKn5DOn5Tmn3jym7D6o3jmq6EGp3z2q6kap4UOp8EWp8T6t6UCt6z2x5UGw6FOt5Eaw70yv806w9UK25liw5T645lqw5Vqw5k2z8k+z81Oz+VK28lO29ES851i1+1C661m591679168+mG99WO9/GO++mjE8WjH8HDF/G7H9HTI+3vM+XvN9oTQ/YzT/pLW/v///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH5BAEKAH8ALAAAAAAQABAAAAe8gH+CggKFhoOIf4UnPz4+PyeFiQImPTg0Li40OD0mAoMCJDo1MipAQCoyNTokn4o7MTAwIqcisjE7nwIfMywsKRoNDyG+LDMfhTwrKCgZp0AZzCgrPIU5INgTzw7Y2DmFNhziFwanCOLiNoU3GxXuB6cH7hUbN4UYHhERCgGnAQr6PGDQ9QLCggLPgBRYAOGFKwEWOjAgkJAAgw4WXCmiMCLBAAAABiQYQUEjIQESWpQo0UKCpEQnDZn8EwgAOw==')

        self.settings = tk.PhotoImage(data='R0lGODlhEAAQAMQfAJyzyufy/qG1ysLa8qzF3llyitjr/pOsxcvk/aS807zV7UpierXO54ylvZywxPb5/r3S6L7X8H2WrrrS6ZCowPr8/6fA2WmCm5ixyrzU68fg+Mvg9fH3/sDY7////////yH5BAEAAB8ALAAAAAAQABAAAAV44CeOZGl+XuqdpOc4mLCeqfM8QWClpSckG45i4GEQdiPfDTKJeBCeHGXmejAVz6fCIJmhBIGMRyIJRLheFCDg0XQrDEQ3ufYQAxUChjIoUBM5TxEWex0ZC14eCQkEBhYAFA0FiD0eBwYIGgOIaS0XBaCdJiqiLCwhADs=')
        self.sflogo = tk.PhotoImage(data='R0lGODlhEAAQAMZGAO0bJewcJOwcJe0cJe0cJu4cJe4cJu0dJe4dJu43QO84P+84QPA5Qe9GTfBGTvFGTu9HTvBHTvFHT/BITvFUW/FUXPFVW/JVXPJVXfJWXPNWXfJiaPJiafNiafJjaPNjafRjavRkafNxdvNxd/RxdvRxd/RxePVxd/RyePR+g/V/hPWAhfaAhfaMkfaMkvaNkveboPacn/ecoPicofedoPidofeprfiqrfmqrfirrfmrrfm4u/m5u/vT1fzT1fzT1vzU1/3i5P3j5P3x8P3x8f/x8f///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH5BAEKAH8ALAAAAAAQABAAAAehgH+Cg4SFhoeIQysPFBcOK0SIFzQ2Hh06NReHQCQqAAEACCknPoZCIyoHBgcEKiM/hxcyOh8gmBaFLw4aFAwLFBgKCRcZDS1/IzQ3IR82NhARNjkdGzcwJhYsBgAGAyrfKgID4yoUFSoF3QMoLCwiquIqFR8zNx8fNDwSEzsxHB84YJz446LBhQoOShQhUmLBhQsPXhASIsRQjyCIMmpEFAgAOw==')
        self.folder = tk.PhotoImage(data='R0lGODlhEAAQAMQfAOvGUf7ztuvPMf/78/fkl/Pbg+u8Rvjqteu2Pf3zxPz36Pz0z+vTmPzurPvuw/npofbjquvNefHVduuyN+uuMu3Oafbgjfnqvf/3zv/3xevPi+vRjP/20/bmsP///////yH5BAEAAB8ALAAAAAAQABAAAAV24CeOZGmepqeqqOgxjBZFa+19r4ftWQUAgqDgltthMshMIJAZ4jYDHsBARSAmFOJvq+g6HIdEFgcYmBWNxoNAsDjGHgBnmV5bCoUDHLBIq9sFEhIdcAYJdYASFRUQhQkLCwkOFwcdEBAXhVabE52ecDahKy0oIQA7')
        self.help = tk.PhotoImage(data='R0lGODlhEAAQAMQfAGm6/idTd4yTmF+v8Xa37KvW+lyh3KHJ62aq41ee2bXZ98nm/2mt5W2Ck5XN/C1chEZieho8WXXA/2Gn4P39/W+y6V+l3qjP8Njt/lx2izxPYGyv51Oa1EJWZ////////yH5BAEAAB8ALAAAAAAQABAAAAWH4Cd+Xml6Y0pCQts0EKp6GbYshaM/skhjhCChUmFIeL4OsHIxXRAISQTl6SgIG8+FgfBMoh2qtbLZQr0TQJhk3TC4pYPBApiyFVDEwSOf18UFXxMWBoUJBn9sDgmDewcJCRyJJBoEkRyYmAABPZQEAAOhA5seFDMaDw8BAQ9TpiokJyWwtLUhADs=')

        # colors
        self.ncsRed = '#C40233'
        self.ncsBlue = '#0087BD'
        self.ncsGreen = '#009F6B'
        self.ncsYellow = '#FFD300'
        # styles
        style = ttk.Style()
        style.configure('bgRed.TLabel', background=self.ncsRed)
        style.configure('bgGreen.TLabel', background=self.ncsGreen)
        style.configure('bgYellow.TLabel', background=self.ncsYellow)

        # Public domain icons worth looking into using
        # http://www.famfamfam.com/lab/icons/mini/     # Free use
        # http://tango.freedesktop.org/Tango_Showroom  # Public domain


def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # TODO: This only sorts on the first character. Needs to convert to an int, sort, and the go back to a string.

    # reorder data
    data.sort(reverse=descending)
    for index, item in enumerate(data):
        tree.move(item[1], '', index)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, int(not descending)))

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    root = tk.Tk()
    BDDToolbox(root)
    root.mainloop()
