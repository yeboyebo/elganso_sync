from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload


class EgProductsUpload(ProductsUpload):

    def __init__(self, params=None):
        super().__init__("mgb2bproducts", params)

        product_params = self.get_param_sincro('b2bProductsUpload')
        self.product_url = product_params['url']
        self.product_test_url = product_params['test_url']

        link_params = self.get_param_sincro('b2bProductsUploadLink')
        self.link_url = link_params['url']
        self.link_test_url = link_params['test_url']

        self.set_sync_params(self.get_param_sincro('b2b'))

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar productos' AND NOT sincronizado AND website = 'B2B' ORDER BY id LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, s.disponible, t.indice, a.mgdescripcion, a.mgdescripcioncorta")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN articulos a ON lsc.idobjeto = a.referencia INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia LEFT JOIN stocks s ON aa.barcode = s.barcode AND s.codalmacen = 'AMAY' INNER JOIN indicessincrocatalogo t ON aa.talla = t.valor")
        q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, s.disponible, t.indice, a.mgdescripcion, a.mgdescripcioncorta".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.referencia = body[0]["lsc.idobjeto"]

        for row in body:
            if not row["s.disponible"]:
                row["s.disponible"] = 0
            if row["s.disponible"] > 0:
                self.stock_disponible = True
            self.indice_tallas.append(row["t.indice"])

        return body
