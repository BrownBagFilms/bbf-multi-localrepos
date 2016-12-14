# -*- coding: utf-8 -*-
"""
.. module:: bbf-multi-localrepos.hooks.git_clone
    :synopsis: hook to clone git repos

copyright 2016 Brown Bag Films
"""
from __future__ import print_function

__all__ = ['GitCloneHook']

import re
import os
import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class GitCloneHook(HookBaseClass):
    def execute(self, repo, progress):

        if os.path.exists(repo['local_url']):
            self.parent.log_info('Local repo already exists at {local_url} repository'.format(local_url=repo['local_url']))
            return True

        clone_message = 'Cloning {repo} repository into {local}- this might take a while.'.format(repo=repo['name'], local=repo['local_url'])
        clone_message += '\nBut it only needs to happen once. Shotgun Desktop may be "Not Responding" as it clones'

        progress.update_output.emit(clone_message)
        # self.parent.log_info(clone_message)

        process = self.parent.git.clone_subprocess(repo['remote_url'], repo['local_url'], repo['branch'])

        if process is None:
            error_msg = "An Error has occurred trying to clone %s\n" % repo['name']
            # self.parent.log_info(error_msg)
            progress.update_output.emit(error_msg)
            return False

        percentage_re = re.compile('(?P<percentage>\d+)%')

        if process.waitForStarted(60000):
            while process.state() == process.Running:
                if process.waitForReadyRead(60000):
                    available_output = str(process.readAllStandardOutput()).replace("\r", "")
                    for line in available_output.split("\n"):
                        self.parent.log_info(line)
                        progress.update_output.emit(line)
                        m = percentage_re.search(line)
                        if m is not None:
                            perc = m.group("percentage")
                            progress.update_percentage.emit(float(perc))

        process.close()

        progress.update_output.emit('{repo} up to date'.format(repo=repo['name']))

        return True
