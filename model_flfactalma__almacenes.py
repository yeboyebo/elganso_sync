
# @class_declaration elganso_sync_almacenes #
class elganso_sync_almacenes(interna_almacenes, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def damelistaalmacenessincro(params):
        return form.iface.damelistaalmacenessincro(params)

    @helpers.decoradores.csr()
    def damealmacenesconstock(params):
        return form.iface.damealmacenesconstock(params)

