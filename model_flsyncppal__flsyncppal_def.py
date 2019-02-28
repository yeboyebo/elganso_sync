
# @class_declaration elganso_sync #
class elganso_sync(flsyncppal):

    def elganso_sync_get_customer(self):
        return "elganso"

    def __init__(self, context=None):
        super().__init__(context)

    def get_customer(self):
        return self.ctx.elganso_sync_get_customer()

