from controllers.base.default.serializers.default_serializer import DefaultSerializer


class PriceSerializer(DefaultSerializer):

    def get_data(self):

        self.set_string_relation("price", "a.pvp")

        return True
