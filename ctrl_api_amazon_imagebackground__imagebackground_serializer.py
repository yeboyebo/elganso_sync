from controllers.base.default.serializers.default_serializer import DefaultSerializer


class ImageBackgroundSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("referencia", "referencia")
        self.set_string_relation("name", "name")

        self.set_string_relation(
            "serialized//image_url",
            "url",
            max_characters=None,
            skip_replace=True
        )
        self.set_string_value("serialized//size", "full")
        self.set_string_value("serialized//format", "jpg")

        return True
