# -*- coding: utf-8 -*-
"""
.. module:: bbf_multi_localrepos.base
   :synopsis: actual implementation of the localrepos app

copyright 2016 Brown Bag Films
"""
from __future__ import print_function

__all__ = ['update_local_repos']

import os
import sys
import threading
from PySide import QtGui

import repoupdateui_ui

class RepoUpdateUi(QtGui.QMainWindow):
    def __init__(self):
        super(RepoUpdateUi, self).__init__()

        self._ui = repoupdateui_ui.Ui_RepoUpdateUi()
        self._ui.setupUi(self)

    def add_text(self, msg):
        self._ui.textEdit.insertHtml('{msg}<br />\n'.format(msg=msg))
        self._ui.textEdit.ensureCursorVisible()
        QtGui.QApplication.processEvents()

    def set_percentage(self, percentage):
        percentage = float(percentage)

        self._ui.progressBar.setValue(percentage)
        QtGui.QApplication.processEvents()

def update_local_repos(app):
    def doit(app, repo):
        clone_success = app.execute_hook('hook_clone', msgBox=RepoUpdateUi, repo=repo)
        update_success = app.execute_hook('hook_update', msgBox=RepoUpdateUi, repo=repo)

        if False in [clone_success, update_success]:
            app.log_info('Problem cloning/updating {repo} repository'.format(repo=repo['name']))


    threads = []
    for repo in app.settings['local_repos']:
        if repo['as_background_process']:
            t = threading.Thread(target=doit, args=(app, repo))
            threads.append(t)
            t.start()
        else:
            doit(app, repo)
        if repo['add_to_pythonpath']:
            os.environ[repo['name']] = repo['local_url']
            sys.path.append(repo['local_url'])
            pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
            pythonpath.append(repo['local_url'])
            pythonpath = os.pathsep.join(pythonpath)
            os.environ['PYTHONPATH'] = pythonpath
