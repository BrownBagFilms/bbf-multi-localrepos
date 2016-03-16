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
    def execute(self, msgBox, repo):
        msgBox = msgBox()
        # msgBox.resize(512, 320)
        # msgBox.show()
        # msgBox.showMaximized()
        # msgBox.showNormal()
        # msgBox.raise_()

        if os.path.exists(repo['local_url']):
            self.parent.log_info('Local repo already exists at {local_url} repository'.format(local_url=repo['local_url']))
            return True
        self.parent.log_info('Cloning {repo} repository - this might take a while!'.format(repo=repo['name']))

        git_clone = self.parent.git.clone_subprocess(repo['remote_url'], repo['local_url'], repo['branch'])

        percentage_re = re.compile('(?P<percentage>\d+)%')
        for line in git_clone.stdout:
            msgBox.add_text(line)
            self.parent.log_info(line)
            m = percentage_re.search(line)
            if m is not None:
                msgBox.set_percentage(m.group('percentage'))

        self.parent.log_info('{repo} up to date'.format(repo=repo['name']))

        return True
