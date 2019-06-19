from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload


class EgProductsUpload(ProductsUpload):

    product_url = "http://b2b.elganso.com/index.php/rest/default/V1/products"
    product_test_url = "http://magento2.local/index.php/rest/default/V1/products"

    link_url = "http://b2b.elganso.com/index.php/rest/default/V1/configurable-products/{}/child"
    link_test_url = "http://magento2.local/index.php/rest/default/V1/configurable-products/{}/child"

    def __init__(self, params=None):
        super().__init__("mgb2bproducts", params)

        self.set_sync_params({
            "auth": "Bearer 7plp6sabntbe9liboanunxy8l9813f3p",
            "test_auth": "Bearer 2uvlxkuihd474nzj3dize4f5ezbl3lb6"
        })

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar productos' AND NOT sincronizado AND website = 'B2B' ORDER BY id LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, s.disponible, t.indice")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN articulos a ON lsc.idobjeto = a.referencia INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN stocks s ON aa.barcode = s.barcode  INNER JOIN indicessincrocatalogo t ON aa.talla = t.valor")
        q.setWhere("lsc.id = {} AND s.codalmacen = 'AMAY' GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, s.disponible, t.indice".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.referencia = body[0]["lsc.idobjeto"]

        for row in body:
            self.indice_tallas.append(row["t.indice"])

        return body
