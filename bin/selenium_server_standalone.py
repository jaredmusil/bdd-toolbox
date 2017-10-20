# -*- coding: utf-8 -*-

"""
This Program launches a selenium server standalone as another user using RunAs

Author:   Jared Musil
Function: Customer Collaborations
Email:    jared.musil.kbw5@statefarm.com
"""

import os
import subprocess
import tkinter as tk
import tkinter.ttk as ttk

__author__ = "Jared Musil"
__email__ = "jared.musil.kbw5@statefarm.com"

class Server:
    def __init__(self, root):
        self.root = root
        self.root.title('Selenium Server Standalone')
        self.root.iconbitmap(os.path.dirname(os.path.abspath('__file__')) + '\\img\\toolbox-icon.ico')

        self.__init_variables()
        self.__init_widgets(root)

    def __init_variables(self):
        self.app_root = os.path.dirname(os.path.abspath('__file__'))
        self.data_root = self.app_root + '\\data'
        self.results_root = self.data_root + '\\results'
        #TODO implement save method using results directory


    def __init_widgets(self, parent):
        # root geometry
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # variables
        self.browser = tk.StringVar()
        self.domain = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        browsers = ['Chrome', 'Firefox', 'IE', 'PhantomJS']
        domains = ['UNTOPR', 'OPRSYS', 'OPR']

        # widgets
        frame = ttk.Frame(root)
        browser_option = ttk.OptionMenu(frame, self.browser, browsers[0], *browsers)
        domain_option = ttk.OptionMenu(frame, self.domain, domains[0], *domains)
        browser_label = ttk.Label(frame, text='Browser')
        domain_label = ttk.Label(frame, text='Username')
        username_label = ttk.Label(frame, text='Username')
        password_label = ttk.Label(frame, text='Password')
        username_entry = ttk.Entry(frame, textvariable=self.username)
        password_entry = ttk.Entry(frame, textvariable=self.password)
        button = ttk.Button(frame, command=lambda: self.on_selenium_server_start(), text='Start Selenium Server')
        frame.grid()

        browser_label.grid(row=0, column=0, sticky=tk.NSEW)
        browser_option.grid(row=0, column=1, sticky=tk.NSEW)
        domain_label.grid(row=1, column=0, sticky=tk.NSEW)
        domain_option.grid(row=1, column=1, sticky=tk.NSEW)
        username_label.grid(row=2, column=0, sticky=tk.NSEW, pady=2)
        username_entry.grid(row=2, column=1, sticky=tk.NSEW, pady=2)
        password_label.grid(row=3, column=0, sticky=tk.NSEW, pady=(0,2))
        password_entry.grid(row=3, column=1, sticky=tk.NSEW, pady=(0,2))
        button.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW)
        frame.update()

    def on_selenium_server_start(self):
        _port = 5555
        _driver = 'ie'
        _domain = self.domain.get()
        _browser = self.browser.get()
        _username = 'AAAA'
        _password = 'qwerty'
        _ie_driver_path = self.app_root + '-Dwebdriver.ie.driver=' + self.app_root + '\extra\IEDriverServer.exe -jar'
        _selenium_server_path = self.app_root + '\extra\IEDriverServer.exe'

        _java = 'java.exe -jar "C:\path-to-selenium-rc-server\selenium-server.jar" -interactive'
        _runas = 'runas.exe /netonly /user:' + _domain + '\\' + _password + ' "C:\path-to-other-batch-file\start-selenium-server.bat"'

        cmd = 'java.exe ' + _ie_driver_path + ' ' + _selenium_server_path + ' ' + _port
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
        output, error = process.communicate()
        print(cmd)
        process.terminate()

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    root = tk.Tk()
    Server(root)
    root.mainloop()
