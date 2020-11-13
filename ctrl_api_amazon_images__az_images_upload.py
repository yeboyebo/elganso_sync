from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.images.serializers.image_serializer import ImageSerializer


class AzImagesUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azimagesupload", params)

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("az.referencia, aa.barcode, urls.urls_sinfondo")
        q.setFrom("az_articulosamazon az INNER JOIN atributosarticulos aa ON az.referencia = aa.referencia LEFT JOIN eg_urlsimagenesarticulosmgt urls ON az.referencia = urls.referencia")
        q.setWhere("az.referencia IN (SELECT referencia FROM az_articulosamazon WHERE sincroarticulo AND articulocreado AND sincrorelacion AND NOT sincroimagenes AND NOT errorsincro LIMIT 15) AND urls.urls_sinfondo IS NOT NULL AND urls.urls_sinfondo <> ''")

        return q

    def get_db_data(self):
        body = []

        q = self.get_query()
        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)

        url_body = []
        for row in body:
            new_ref = False
            if row['az.referencia'] not in self.referencias:
                new_ref = True
                self.referencias.append(row['az.referencia'])

            imgtype = None

            urls = row['urls.urls_sinfondo'].split(',')

            if not urls or urls == '':
                continue

            for idx, url in enumerate(urls):
                if idx == 0:
                    imgtype = 'Main'
                elif 0 < idx <= 8:
                    imgtype = 'PT{}'.format(idx)
                else:
                    imgtype = None

                if imgtype is not None:
                    if new_ref:
                        url_body.append({'idobjeto': row['az.referencia'], 'url': url, 'imgtype': imgtype})
                    url_body.append({'idobjeto': row['aa.barcode'], 'url': url, 'imgtype': imgtype})

        return url_body

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET sincroimagenes = true, idlog_imagenes = (SELECT id FROM az_logamazon WHERE idamazon = '{}') WHERE referencia IN ('{}')".format(amazon_id, "','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        return ImageSerializer()

    def get_msgtype(self):
        return 'ProductImage'

    def get_feedtype(self):
        return '_POST_PRODUCT_IMAGE_DATA_'
