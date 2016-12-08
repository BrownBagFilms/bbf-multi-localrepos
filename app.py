from sgtk.platform import Application

class LocalRepos(Application):
    def init_app(self):

        app_module = self.import_module('bbf_multi_localrepos')
        framework_sgutils = self.frameworks.get("tk-framework-shotgunutils")
        settings_module = framework_sgutils.import_module("settings")
        self.settings_manager = settings_module.UserSettings(self.engine)

        self.git = app_module.git

        def call_update_local_repos(app=self):
            app_module.update_local_repos(app)

        self.engine.register_command("update_code_repo", call_update_local_repos, {})
