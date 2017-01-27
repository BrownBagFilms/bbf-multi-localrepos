# -*- coding: utf-8 -*-
"""
.. module:: bbf-multi-localrepos.hooks.git_update
    :synopsis: hook to update git repos

copyright 2016 Brown Bag Films
"""
from __future__ import print_function

__all__ = ['GitUpdateHook']


import os
import re
import time

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class GitUpdateHook(HookBaseClass):
    def execute(self, repo, progress):

        progress.update_output.emit('Updating local {repo} repository'.format(repo=repo['name']))

        local_repo = repo.get("local_url")
        check_git_lock(local_repo)

        process = self.parent.update_subprocess(repo['local_url'], branch=repo['branch'])

        if process is None:
            error_msg = "An Error has occurred trying to update %s\n" % repo['name']
            # self.parent.log_info(error_msg)
            progress.update_output.emit(error_msg)
            return False

        percentage_re = re.compile('(?P<percentage>\d+)%')

        if process.waitForStarted(60000):
            while process.state() == process.Running:
                if process.waitForReadyRead(60000):
                    available_output = str(process.readAllStandardOutput()).replace("\r", "")
                    for line in available_output.split("\n"):
                        progress.update_output.emit(line)
                        m = percentage_re.search(line)
                        if m is not None:
                            progress.update_percentage.emit(float(m.group("percentage")))

        process.close()

        progress.update_output.emit('{repo} up to date'.format(repo=repo['name']))

        return True


def check_git_lock(local_repo_path):
    """
    Checks '.git' folder for 'index.lock' and delete it if exists and is longer than 24 hours old.

    :param local_repo_path: str
    """
    cut_off_time = 86400.0  # 24 hours in seconds

    if local_repo_path is not None:
        git_lock_file = os.path.join(local_repo_path, ".git", "index.lock")

        if os.path.exists(git_lock_file):
            time_modified = os.path.getmtime(git_lock_file)
            now = time.time()

            if (now - time_modified) > cut_off_time:
                try:
                    os.remove(git_lock_file)
                except IOError as e:
                    pass

