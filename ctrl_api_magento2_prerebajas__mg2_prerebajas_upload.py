import json

from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload
from controllers.api.magento2.prerebajas.serializers.simple_prerebajas_serializer import SimplePrerebajasSerializer
from controllers.api.magento2.prerebajas.serializers.configurable_prerebajas_serializer import ConfigurablePrerebajasSerializer


class Mg2PrerebajasUpload(ProductsUpload):

    error = False

    def __init__(self, params=None):
        super().__init__("mg2Prerebajas", params)

        product_params = self.get_param_sincro('mg2PreRebajas')
        self.product_url = product_params['url']
        self.product_test_url = product_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 2
        self.cod_plan = ""
        self.stores_id = []

    def get_db_data(self):
        body = []
        self.stores_id = []
        self.cod_plan = qsatype.FLUtil.sqlSelect("lineassincro_planpreciosprerebajas", "codplan", "sincronizado = false")
        if not self.cod_plan:
            return body

        s = qsatype.FLSqlQuery()
        s.setSelect("at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento")
        s.setFrom("lineassincro_planpreciosprerebajas pr INNER JOIN atributosarticulos at ON pr.sku = at.referencia INNER JOIN eg_tiendasplanprecios t ON pr.codplan = t.codplan INNER JOIN mg_storeviews mg ON mg.egcodtiendarebajas = t.codtienda")
        s.setWhere("pr.codplan = '{}' GROUP BY at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento ORDER BY at.referencia, mg.idmagento".format(self.cod_plan))
        s.exec_()

        body = self.fetch_query(s)
        self.error = False

        return body

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        new_rebaja = []
        referencia = ""
        store_id = ""
        for row in data:
            if referencia == "":
                referencia = row["at.referencia"]
                store_id = row["mg.idmagento"]
                new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))

            if referencia != row["at.referencia"]:
                referencia = row["at.referencia"]
                new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))
            else:
                if store_id != row["mg.idmagento"]:
                    new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))
                    store_id = row["mg.idmagento"]

            new_rebaja.append(self.get_simple_prerebajas_serializer().serialize(row))

        return {
            "promoPrices": new_rebaja
        }

    def get_simple_prerebajas_serializer(self):
        return SimplePrerebajasSerializer()

    def get_configurable_prerebajas_serializer(self):
        return ConfigurablePrerebajasSerializer()

    def send_data(self, data):
        product_url = self.product_url if self.driver.in_production else self.product_test_url
        
        for idx in range(len(data["promoPrices"])):
            del data["promoPrices"][idx]["children"]

        try:
            self.send_request("post", url=product_url, data=json.dumps(data))
        except Exception as e:
            print("exception")
            self.error = True

        return True

    def after_sync(self, response_data=None):
        
        if self.error:
            self.log("Error", "No se pudo sincronizar las Pre-rebajas del planificador: {})".format(self.cod_plan))
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosprerebajas SET sincronizado = TRUE WHERE codplan = '{}'".format(self.cod_plan))

        self.log("Exito", "Plan Precios PreRebajas {} sincronizados correctamente.".format(self.cod_plan))

        return self.small_sleep
