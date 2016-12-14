# -*- coding: utf-8 -*-
"""
.. module:: bbf-multi-localrepos.hooks.git_update
    :synopsis: hook to update git repos

copyright 2016 Brown Bag Films
"""
from __future__ import print_function

__all__ = ['GitUpdateHook']

import re

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class GitUpdateHook(HookBaseClass):
    def execute(self, repo, progress):

        progress.update_output.emit('Updating local {repo} repository'.format(repo=repo['name']))

        process = self.parent.git.update_subprocess(repo['local_url'], branch=repo['branch'])

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
