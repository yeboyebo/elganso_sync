
# @class_declaration elganso_sync_tpv_comandas #
from models.flsyncppal import eg_diagnosis_def as diagnosis


class elganso_sync_tpv_comandas(flfact_tpv_tpv_comandas, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def diagnosis(params):
        return diagnosis.iface.diagnosis(params)

