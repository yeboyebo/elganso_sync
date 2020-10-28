from abc import ABC
from YBLEGACY import qsatype
from YBLEGACY.constantes import xml2dict

from controllers.api.amazon.drivers.amazon import AmazonDriver
from controllers.base.default.controllers.download_sync import DownloadSync


class AzFeedResultProcess(DownloadSync, ABC):

    procesamientos = {}

    def __init__(self, params=None):
        super().__init__("azfeedresultprocess", AmazonDriver(), params)

    def get_data(self):
        body = []

        q = self.get_query()
        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)

        return body

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("id, idamazon, respuesta")
        q.setFrom("az_logamazon")
        q.setWhere("procesadoaz AND NOT procesadoaq ORDER BY fecha, hora")

        return q

    def process_data(self, data):
        for d in data:
            idlog = d['id']
            idamazon = d['idamazon']
            response = xml2dict(d['respuesta'])

            print(response)

            for message in response.Message:
                for result in message.ProcessingReport.Result:
                    error = result.ResultCode == 'Error'
                    desc = result.ResultDescription
                    sku = False
                    if 'AdditionalInfo' in result:
                        sku = result.AdditionalInfo.SKU

                    barcode_error = {}
                    if error and desc and sku:
                        if sku not in barcode_error:
                            barcode_error[sku] = []
                        barcode_error[sku].append(error)

            q = qsatype.FLSqlQuery()
            q.setSelect("referencia, barcode")
            q.setFrom("atributosarticulos")
            q.setWhere("barcode IN ('{}')".format("','".join([barcode for barcode in barcode_error])))

            body = self.fetch_query(q)

            referencia_error = {}
            for row in body:
                referencia = row['referencia']
                barcode = row['barcode']

                if referencia not in referencia_error:
                    referencia_error[referencia] = []

                if barcode in barcode_error:
                    referencia_error[referencia].append("{} -> {}".format(barcode, barcode_error[barcode]))

            self.procesamientos[idlog] = {
                'idamazon': idamazon,
                'errores': referencia_error
            }

            # Procesar messages (Message[])
            # Comprobar ProcessingReport.StatusCode Complete?
            # Procesar results (Result[])
            # ResultCode Error o Warning?
            # ResultDescription
            # Comprobar si hay AdditionalInfo.SKU, si no, es general

            # * Guardar errores por barcode en un dict barcode - array_errores
            # * Agrupar por referencia en un dict referencia - array_barcode_+_error
            # * Guardar log_amazon como procesado
            # * Marcar referencia como errorsincro = true
            # * Guardar errores en descerror
            # Guardar un registro de az_error? No parece tener mucho sentido

    def after_sync(self, response_data=None):
        if not self.procesamientos:
            self.log("Error", "No se han podido procesar resultados")
            return

        qsatype.FLSqlQuery().execSql("UPDATE az_logamazon SET procesadoaq = true WHERE id IN ({})".format(",".join([idlog for idlog in self.procesamientos])))

        for idlog in self.procesamientos:
            for referencia in self.procesamientos[idlog]['errores']:
                qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET id_error = {}, errorsincro = true, descerror = '{}' WHERE referencia = '{}'".format(idlog, "\n".join(self.procesamientos[idlog]['errores'][referencia]), referencia))

        self.log("Éxito", "Resultados procesados correctamente (ids_amazon: {})".format([self.procesamientos[idlog]['idamazon'] for idlog in self.procesamientos]))

    def fetch_query(self, q):
        field_list = [field.strip() for field in q.select().split(",")]

        rows = []
        while q.next():
            row = {field: q.value(field) for (field) in field_list}
            rows.append(row)

        return rows
