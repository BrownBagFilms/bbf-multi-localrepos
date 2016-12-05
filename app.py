from sgtk.platform import Application

class LocalRepos(Application):
    def init_app(self):
        app_module = self.import_module('bbf_multi_localrepos')

        self.git = app_module.git

        def call_update_local_repos(app=self):
            app_module.update_local_repos(app)

        self.engine.register_command("update_code_repo", call_update_local_repos, {})
