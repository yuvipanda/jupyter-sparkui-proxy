from tornado import web
from jupyter_server_proxy.handlers import LocalProxyHandler
from notebook.utils import url_path_join


class SparkUIHandler(LocalProxyHandler):
    def __init__(self, *args, **kwargs):
        self.port = 4040
        super().__init__(*args, **kwargs)

    @web.authenticated
    async def proxy(self, path):
        if not path.startswith('/'):
            path = '/' + path

        return await super().proxy(self.port, path)

    async def http_get(self, path):
        # SparkUI has a bug where / doesn't respect spark.ui.proxyBase
        # so we do the redirect for them
        if path == '' or path == '/':
            # The '/' at end of jobs is important, since otherwise
            # spark UI can't even and 
            self.redirect(url_path_join(self.base_url, 'sparkui', 'jobs/'))
        else:
            return await self.proxy(path)

    async def open(self, path):
        return await super().open(path)

    # We have to duplicate all these for now, I've no idea why!
    # Figure out a way to not do that?
    def post(self, path):
        return self.proxy(path)

    def put(self, path):
        return self.proxy(path)

    def delete(self, path):
        return self.proxy(path)

    def head(self, path):
        return self.proxy(path)

    def patch(self, path):
        return self.proxy(path)

    def options(self, path):
        return self.proxy(path)


def setup_handlers(web_app):
    base_url = web_app.settings['base_url']
    web_app.add_handlers('.*', [
        (url_path_join(base_url, r'/sparkui(.*)'), SparkUIHandler, {'absolute_url': False})
    ])


def load_jupyter_server_extension(nbapp):
    setup_handlers(nbapp.web_app)