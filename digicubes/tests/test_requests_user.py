from . import BasicServerTest

class TestRequest(BasicServerTest):

    async def test_users(self):

        api = self.api

        @api.route("/")
        def hello(req, resp):
            resp.text = "TEXT"

        print(api.requests.get(api.url_for(hello)).text)
