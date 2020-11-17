from controllers.base.default.drivers.web_driver import WebDriver


class ApiBgDriver(WebDriver):

    def __init__(self):
        super().__init__()

    def login(self):
        return True

    def logout(self):
        return True

    def get_headers(self):
        return {
            'X-Api-Key': self.apiBgImageKey
        }
