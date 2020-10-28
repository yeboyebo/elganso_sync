from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.images.serializers.image_serializer import ImageSerializer


class AzImagesUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azimagesupload", params)

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("az.referencia, urls.text")
        q.setFrom("az_articulosamazon az LEFT JOIN eg_urlsimagenesarticulosmgt urls ON az.referencia = urls.referencia")
        q.setWhere("az.sincroarticulo AND az.articulocreado AND az.sincrorelacion AND NOT az.sincroimagenes AND NOT az.errorsincro")

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
            self.referencias.append(row['az.referencia'])

            imgtype = None

            urls = row['urls.text'].split(',')
            for idx, url in enumerate(urls):
                if idx == 0:
                    imgtype = 'Main'
                elif 0 < idx <= 8:
                    imgtype = 'PT{}'.format(idx)
                else:
                    imgtype = None

                if imgtype is not None:
                    url_body.append({'az.referencia': row['az.referencia'], 'url': url, 'imgtype': imgtype})

        return url_body

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET sincroimagenes = true, idlog_imagenes = {} WHERE referencia IN ('{}')".format(amazon_id, "','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        return ImageSerializer()

    def get_msgtype(self):
        return 'ProductImage'

    def get_feedtype(self):
        return '_POST_PRODUCT_IMAGE_DATA_'