from controllers.base.default.serializers.default_serializer import DefaultSerializer


class FeedSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_value("Header//DocumentVersion", "1.01")
        self.set_string_value("Header//MerchantIdentifier", self.merchant_id)

        self.set_string_value("MessageType", self.msg_type)
        # self.set_string_value("PurgeAndReplace", "true")

        self.set_data_value("Message", self.get_children_data())

        del self.data['children']

        return True

    def get_children_data(self):
        message_id = 0
        children = []

        for data in self.init_data:
            message_id += 1
            data['messageId'] = message_id

            child_data = self.child_serializer.serialize(data)
            del child_data['children']
            children.append(child_data)

        return children
