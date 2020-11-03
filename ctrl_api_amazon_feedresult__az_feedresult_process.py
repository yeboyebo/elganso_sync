from abc import ABC
from YBLEGACY import qsatype
from YBLEGACY.constantes import xml2dict

from controllers.api.amazon.drivers.amazon import AmazonDriver
from controllers.base.default.controllers.download_sync import DownloadSync


class AzFeedResultProcess(DownloadSync, ABC):

    procesamientos = {}

    def __init__(self, params=None):
        super().__init__("azfeedresultprocess", AmazonDriver(), params)

        self.set_sync_params(self.get_param_sincro('amazon'))

        self.origin_field = "idamazon"

    def get_data(self):
        self.procesamientos = {}

        body = []

        q = self.get_query()
        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)

        return body

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("id, idamazon, tipo, respuesta")
        q.setFrom("az_logamazon")
        q.setWhere("procesadoaz AND NOT procesadoaq ORDER BY fecha, hora LIMIT 1")

        return q

    def process_data(self, data):
        idlog = data['id']
        idamazon = data['idamazon']
        tipo = data['tipo']

        response = xml2dict(bytes(data['respuesta'], 'utf-8'))

        barcode_error = {}
        for result in response.Message.ProcessingReport.Result:
            error = result.ResultCode == 'Error'
            desc = result.ResultDescription
            sku = False

            if hasattr(result, 'AdditionalInfo'):
                sku = str(result.AdditionalInfo.SKU)

            if error and desc is not None and sku:
                if sku not in barcode_error:
                    barcode_error[sku] = []
                barcode_error[sku].append(desc)

        q = qsatype.FLSqlQuery()
        q.setSelect("referencia, barcode")
        q.setFrom("atributosarticulos")
        q.setWhere("barcode IN ('{}')".format("','".join([str(barcode) for barcode in barcode_error])))

        q.exec_()
        body = self.fetch_query(q)

        referencia_error = {}
        for row in body:
            referencia = row['referencia']
            barcode = row['barcode']

            if referencia not in referencia_error:
                referencia_error[referencia] = []

            if barcode in barcode_error:
                for error in barcode_error[barcode]:
                    referencia_error[referencia].append("{} -> {}".format(barcode, error))

        self.procesamientos[idlog] = {
            'idamazon': idamazon,
            'tipo': tipo,
            'errores': referencia_error
        }

    def after_sync(self, response_data=None):
        if not self.procesamientos:
            self.log("Error", "No se han podido procesar resultados")
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_logamazon SET procesadoaq = true WHERE id IN ({})".format(",".join([str(idlog) for idlog in self.procesamientos])))

        for idlog in self.procesamientos:
            referencias = []

            for referencia in self.procesamientos[idlog]['errores']:
                referencias.append(referencia)
                qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET id_error = {}, errorsincro = true, descerror = '{}' WHERE referencia = '{}'".format(idlog, self.format_error(self.procesamientos[idlog]['errores'][referencia]), referencia))

            bool_field = self.get_bool_field(self.procesamientos[idlog]['tipo'])
            nextbool_field = self.get_nextbool_field(self.procesamientos[idlog]['tipo'])
            idlog_field = self.get_idlog_field(self.procesamientos[idlog]['tipo'])

            if nextbool_field:
                qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET articulocreado = true, {} = true, {} = false, id_error = NULL, errorsincro = false, descerror = NULL WHERE {} = {} AND referencia NOT IN ('{}')".format(bool_field, nextbool_field, idlog_field, idlog, "','".join(referencias)))
            else:
                qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET articulocreado = true, {} = true, id_error = NULL, errorsincro = false, descerror = NULL WHERE {} = {} AND referencia NOT IN ('{}')".format(bool_field, idlog_field, idlog, "','".join(referencias)))

        self.log("Éxito", "Resultados procesados correctamente (ids_amazon: {})".format([str(self.procesamientos[idlog]['idamazon']) for idlog in self.procesamientos]))

        return self.small_sleep

    def get_bool_field(self, tipo):
        if tipo == 'Product':
            return 'sincroarticulo'
        if tipo == 'Relationship':
            return 'sincrorelacion'
        if tipo == 'Inventory':
            return 'sincrostock'
        if tipo == 'Price':
            return 'sincroprecio'
        if tipo == 'ProductImage':
            return 'sincroimagenes'
        return False

    def get_nextbool_field(self, tipo):
        if tipo == 'Product':
            return 'sincrorelacion'
        if tipo == 'Relationship':
            return 'sincroimagenes'
        if tipo == 'Price':
            return 'sincrostock'
        if tipo == 'ProductImage':
            return 'sincroprecio'
        return False

    def get_idlog_field(self, tipo):
        if tipo == 'Product':
            return 'idlog_articulo'
        if tipo == 'Relationship':
            return 'idlog_relacion'
        if tipo == 'Inventory':
            return 'idlog_stock'
        if tipo == 'Price':
            return 'idlog_precio'
        if tipo == 'ProductImage':
            return 'idlog_imagenes'
        return False

    def format_error(self, errors):
        errors = "\n".join(errors)
        errors = errors.replace("'", "\"")
        return errors

    def fetch_query(self, q):
        field_list = [field.strip() for field in q.select().split(",")]

        rows = []
        while q.next():
            row = {field: q.value(field) for (field) in field_list}
            rows.append(row)

        return rows
