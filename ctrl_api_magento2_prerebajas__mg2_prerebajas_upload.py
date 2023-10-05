import json

from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload
from controllers.api.magento2.prerebajas.serializers.simple_prerebajas_serializer import SimplePrerebajasSerializer


class Mg2PrerebajasUpload(ProductsUpload):

    def __init__(self, params=None):
        super().__init__("mg2Prerebajas", params)

        product_params = self.get_param_sincro('mg2ProductsUpload')
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
        s.setSelect("mg.codstoreview")
        s.setFrom("mg_storeviews mg INNER JOIN eg_tiendasplanprecios t ON mg.egcodtiendarebajas = t.codtienda INNER JOIN eg_planprecios p ON t.codplan = p.codplan")
        s.setWhere("p.codplan = '{}' GROUP BY mg.codstoreview".format(self.cod_plan))
        s.exec_()
        bodyStores = self.fetch_query(s)
        for i in bodyStores:
            print(i["mg.codstoreview"])
            self.stores_id.append(i["mg.codstoreview"])

        q = qsatype.FLSqlQuery()
        q.setSelect("sku, pvp, desde")
        q.setFrom("lineassincro_planpreciosprerebajas")
        q.setWhere("codplan = '{}'".format(self.cod_plan))
        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False

        return body

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        for row in data:
            product = self.get_simple_prerebajas_serializer().serialize(row)
            self.send_data(product)

        return True

    def get_simple_prerebajas_serializer(self):
        return SimplePrerebajasSerializer()

    def send_data(self, data):
        product_url = self.product_url if self.driver.in_production else self.product_test_url
        for i in range(len(self.stores_id)):
            self.send_request("post", url=product_url.format(self.stores_id[i]), data=json.dumps({"product": data["product"]}))
        return True

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosprerebajas SET sincronizado = TRUE WHERE codplan = '{}'".format(self.cod_plan))

        self.log("Exito", "Plan Precios PreRebajas {} sincronizados correctamente.".format(self.cod_plan))

        return self.small_sleep

    def sync(self):
        data = self.get_data()
        return self.after_sync(True)