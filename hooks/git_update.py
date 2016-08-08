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
    def execute(self, msgBox, repo):
        msgBox = msgBox()
        # msgBox.resize(640, 480)
        # msgBox.show()
        # msgBox.showMaximized()
        # msgBox.showNormal()
        # msgBox.raise_()

        self.parent.log_info('Updating local {repo} repository'.format(repo=repo['name']))

        git_pull = self.parent.git.update_subprocess(repo['local_url'], branch=repo['branch'])

        percentage_re = re.compile('(?P<percentage>\d+)%')
        for line in git_pull.stdout:
            msgBox.add_text(line)
            self.parent.log_info(line)
            m = percentage_re.search(line)
            if m is not None:
                msgBox.set_percentage(m.group('percentage'))


        self.parent.log_info('{repo} up to date'.format(repo=repo['name']))

        return True
