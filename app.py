from sgtk.platform import Application

from PySide import QtCore


class LocalRepos(Application):
    def init_app(self):

        app_module = self.import_module('bbf_multi_localrepos')
        try:
            self.psutil = self.import_module('psutil')
        except:
            self.psutil = None
        framework_sgutils = self.frameworks.get("tk-framework-shotgunutils")
        settings_module = framework_sgutils.import_module("settings")
        self.settings_manager = settings_module.UserSettings(self.engine)

        self.git = app_module.git
        self.git_cmds = app_module.git.base.git_cmds

        def call_update_local_repos(app=self):
            app_module.update_local_repos(app)

        self.engine.register_command("update_code_repo", call_update_local_repos, {})

    def clone_subprocess(self, remote_url, local_url, branch):
        # When cloning using --depth, make sure file:// in front of a local path (URLs are fine)
        args = ["clone", "-b", branch, "--depth", "1", remote_url, local_url]
        process = QtCore.QProcess()
        process.setProcessChannelMode(process.MergedChannels)
        process.start(self.git_cmds.git, args)
        return process

    def update_subprocess(self, local_url, remote='origin', branch=None):
        def call_git(args):
            process = QtCore.QProcess()
            process.setProcessChannelMode(process.MergedChannels)
            process.setWorkingDirectory(local_url)
            process.start(self.git_cmds.git, args)
            return process

        process_args = ['pull', remote]

        if branch is not None:
            p = call_git(['checkout', branch])  # Checkout [branch]
            if not p.waitForFinished(60000):  # Need to wait for process to finish
                self.clean_process(p)
                return None

            p = call_git(['reset', "--hard", "origin/%s" % branch])  # Hard reset to origin/[branch]
            if not p.waitForFinished(60000):  # Ensure process is finished
                self.clean_process(p)
                return None

            process_args.append(branch)

        return call_git(process_args)

    def clean_process(self, process):
        if self.psutil:
            pid = process.pid()
            p = self.psutil.Process(pid)
            for child_proc in p.children(recursive=True):
                if child_proc.is_running():
                    child_proc.kill()
            if p.is_running():
                p.kill()

            process.close()

