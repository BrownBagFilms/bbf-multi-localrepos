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


def clean_repo_root_path(repo_root_path, progress):
    """
    Removes all .pyc files.
    
    :param repo_root_path: 
    :param progress: 
    :return: 
    """

    if repo_root_path and os.path.exists(repo_root_path):
        for root_path, dirs, files in os.walk(repo_root_path):
            for _f in files:
                if _f.endswith(".pyc"):
                    full_path = os.path.join(root_path, _f)
                    progress.update_output.emit("Removing file - '%s'" % full_path)
                    try:
                        os.remove(full_path)
                    except IOError as e:
                        progress.update_output.emit("Unable to remove file - '%s'" % full_path)
                        progress.update_output.emit(str(e))


def _update(app, repo, progress):
    project_id = app.context.project.get("id")
    # Get stored override config file name
    # config_file_name = app.settings_manager.retrieve("bbf_config_file_%s" % project_id, None,
    #                                                  app.settings_manager.SCOPE_PROJECT)
    config_file_name = bbf_override_config.get_config_file_name(project_id)

    run_update = False

    # Use override data if found
    if config_file_name:
        config_data = bbf_override_config.get_available_override_config(config_file_name)
        if config_data:
            config_mode = config_data.get("config_mode")

            # Make sure only primary config_mode will update code repo.
            if config_mode == "primary":
                run_update = True

            repo_config_data = config_data.get("bbf_localrepos_config")

            if repo_config_data:
                repo["name"] = repo_config_data.get("name") or repo["name"]
                repo["branch"] = repo_config_data.get("branch") or repo["branch"]
                repo["local_url"] = repo_config_data.get("local_url") or repo["local_url"]
                repo["remote_url"] = repo_config_data.get("remote_url") or repo["remote_url"]

    clean_repo_root_path(repo.get("local_url"), progress)

    clone_success = app.execute_hook('hook_clone', repo=repo, progress=progress)
    if not clone_success:
        progress.update_output.emit('Problem cloning {repo} repository'.format(repo=repo['name']))

    progress.reset.emit()

    if run_update:
        update_success = app.execute_hook('hook_update', repo=repo, progress=progress)
        if not update_success:
            progress.update_output.emit('Problem updating {repo} repository'.format(repo=repo['name']))
    else:
        progress.update_output.emit("Currently in 'dev' mode.  Skipping repo update!")

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
