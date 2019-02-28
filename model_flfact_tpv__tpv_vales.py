
# @class_declaration elganso_sync_tpv_vales #
class elganso_sync_tpv_vales(flfact_tpv_tpv_vales, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def consultavale(params):
        return form.iface.consultavale(params)

    @helpers.decoradores.csr()
    def actualizavale(params):
        return form.iface.actualizavale(params)

