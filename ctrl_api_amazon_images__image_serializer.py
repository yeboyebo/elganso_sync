from controllers.base.default.serializers.default_serializer import DefaultSerializer


class ImageSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")
        self.set_string_value("OperationType", "Update")

        self.set_string_relation("ProductImage//SKU", "az.referencia")
        self.set_string_relation("ProductImage//ImageType", "imgtype")

        self.set_string_relation(
            "ProductImage//ImageLocation",
            "url",
            max_characters=None,
            skip_replace=True
        )

        return True
