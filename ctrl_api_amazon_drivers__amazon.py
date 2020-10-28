from controllers.base.default.drivers.web_driver import WebDriver


class AmazonDriver(WebDriver):

    def __init__(self):
        super().__init__()

    def login(self):
        return True

    def logout(self):
        return True

    def get_headers(self):
        return {
            'content-type': 'application/xml',
            'user-agent': 'AQNext/2.1 (Language=Python; Platform=Linux)'
        }
