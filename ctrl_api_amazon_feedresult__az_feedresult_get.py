from abc import ABC
from YBLEGACY import qsatype
from YBLEGACY.constantes import xml2dict

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload


class AzFeedResultGet(AzFeedsUpload, ABC):

    idamazon = None

    def __init__(self, params=None):
        super().__init__("azfeedresultget", params)

        self.small_sleep = 10
        self.large_sleep = 180
        self.no_sync_sleep = 300

    def get_data(self):
        body = []

        q = self.get_query()
        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)

        self.idamazon = body[0]['idamazon']

        return body[0]

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("idamazon")
        q.setFrom("az_logamazon")
        q.setWhere("NOT procesadoaz ORDER BY fecha, hora LIMIT 1")

        return q

    def get_feedtype(self):
        return None

    def get_child_serializer(self):
        pass

    def send_data(self, data):
        attr = self.get_attributes(data)
        signature = self.sign_request(attr)
        url = "https://{}/?{}&Signature={}".format(self.driver.azHost, attr, signature)

        return self.driver.send_request("post", url=url)

    def get_msgtype(self):
        return 'Result'

    def get_raw_attributes(self, data):
        attributes = super().get_raw_attributes(str(data))
        del attributes['ContentMD5Value']
        del attributes['PurgeAndReplace']
        del attributes['FeedType']
        attributes['FeedSubmissionId'] = data['idamazon']
        attributes['Action'] = 'GetFeedSubmissionResult'

        return attributes

    def after_sync(self, response_data=None):
        response = xml2dict(bytes(response_data, 'utf-8'))

        if response.Message[0].ProcessingReport.StatusCode == 'Complete':
            qsatype.FLSqlQuery().execSql("UPDATE az_logamazon SET procesadoaz = true, respuesta = '{}' WHERE idamazon = '{}'".format(response_data, self.idamazon))

            self.log("Exito", "Esquema '{}' sincronizado correctamente (idamazon: {})".format(self.get_msgtype(), self.idamazon))
            return self.small_sleep
        else:
            self.log("Error", "Esquema '{}' no se ha podido sincronizar correctamente o no se ha procesado todavía (idamazon: {})".format(self.get_msgtype(), self.idamazon))
            return self.large_sleep
