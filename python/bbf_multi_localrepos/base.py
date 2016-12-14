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
from PySide import QtGui, QtCore

import bbf_sgtk_config.bbf_override_config as bbf_override_config

import repoupdateui_ui


class Progress(QtCore.QObject):

    update_output = QtCore.Signal(str)
    update_percentage = QtCore.Signal(float)
    finished = QtCore.Signal()
    reset = QtCore.Signal()

    def __init__(self, parent=None):
        super(Progress, self).__init__(parent)


class RepoUpdateUi(QtGui.QMainWindow):
    def __init__(self):
        super(RepoUpdateUi, self).__init__()

        self._ui = repoupdateui_ui.Ui_RepoUpdateUi()
        self._ui.setupUi(self)
        self._ui.textEdit.setReadOnly(True)

    def reset(self):
        self._ui.textEdit.clear()
        self._ui.progressBar.setValue(0.0)

    def add_text(self, msg):
        self._ui.textEdit.insertHtml('{msg}<br />\n'.format(msg=msg))
        self._ui.textEdit.ensureCursorVisible()
        # QtGui.QApplication.processEvents()

    def set_percentage(self, percentage):
        percentage = float(percentage)

        self._ui.progressBar.setValue(percentage)
        # QtGui.QApplication.processEvents()


def _update(app, repo, progress):
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

    clone_success = app.execute_hook('hook_clone', repo=repo, progress=progress)
    if not clone_success:
        progress.update_output.emit('Problem cloning {repo} repository'.format(repo=repo['name']))

    progress.reset.emit()

    update_success = app.execute_hook('hook_update', repo=repo, progress=progress)
    if not update_success:
        progress.update_output.emit('Problem updating {repo} repository'.format(repo=repo['name']))

    progress.finished.emit()


def update_local_repos(app):

    progress = Progress()
    if app.engine.instance_name == "tk-desktop":
        widget = app.engine.show_dialog(app.instance_name, app, RepoUpdateUi)
        progress.update_output.connect(widget.add_text)
        progress.update_percentage.connect(widget.set_percentage)
        progress.reset.connect(widget.reset)
        progress.finished.connect(widget.close)

    progress.update_output.connect(app.log_info)

    threads = []
    for repo in app.settings['local_repos']:
        if repo['as_background_process']:
            t = threading.Thread(target=_update, args=(app, repo, progress))
            threads.append(t)
            t.start()
        else:
            _update(app, repo, progress)

        if repo['add_to_pythonpath']:
            os.environ[repo['name']] = repo['local_url']
            sys.path.append(repo['local_url'])
            pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
            pythonpath.append(repo['local_url'])
            pythonpath = os.pathsep.join(pythonpath)
            os.environ['PYTHONPATH'] = pythonpath
