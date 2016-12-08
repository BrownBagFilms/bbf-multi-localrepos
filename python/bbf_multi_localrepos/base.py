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

import bbf_sgtk_config.bbf_override_config as bbf_override_config

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


def _update(app, repo):
    project_id = app.context.project.get("id")
    # Get stored override config file name
    # config_file_name = app.settings_manager.retrieve("bbf_config_file_%s" % project_id, None,
    #                                                  app.settings_manager.SCOPE_PROJECT)
    config_file_name = bbf_override_config.get_config_file_name(project_id)

    # Use override data if found
    if config_file_name:
        config_data = bbf_override_config.get_available_override_config(config_file_name)

        if config_data:
            repo_config_data = config_data.get("bbf_localrepos_config")

            if repo_config_data:
                repo["name"] = repo_config_data.get("name") or repo["name"]
                repo["branch"] = repo_config_data.get("branch") or repo["branch"]
                repo["local_url"] = repo_config_data.get("local_url") or repo["local_url"]
                repo["remote_url"] = repo_config_data.get("remote_url") or repo["remote_url"]

    clone_success = app.execute_hook('hook_clone', msgBox=RepoUpdateUi, repo=repo)
    if not clone_success:
        app.log_info('Problem cloning {repo} repository'.format(repo=repo['name']))

    update_success = app.execute_hook('hook_update', msgBox=RepoUpdateUi, repo=repo)
    if not update_success:
        app.log_info('Problem updating {repo} repository'.format(repo=repo['name']))


def update_local_repos(app):

    threads = []
    for repo in app.settings['local_repos']:
        if repo['as_background_process']:
            t = threading.Thread(target=_update, args=(app, repo))
            threads.append(t)
            t.start()
        else:
            _update(app, repo)
        
        if repo['add_to_pythonpath']:
            os.environ[repo['name']] = repo['local_url']
            sys.path.append(repo['local_url'])
            pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
            pythonpath.append(repo['local_url'])
            pythonpath = os.pathsep.join(pythonpath)
            os.environ['PYTHONPATH'] = pythonpath
