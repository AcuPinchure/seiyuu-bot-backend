from rest_framework import serializers


class ImportLogSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])
    log_time = serializers.DateTimeField()
    file_name = serializers.CharField(max_length=255)
    content = serializers.CharField()


class LogSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])
    log_time = serializers.DateTimeField()
    file_name = serializers.CharField(max_length=255)
    content = serializers.CharField()


class LogListItemSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])
    log_time = serializers.DateTimeField()
    file_name = serializers.CharField(max_length=255)


class GetLogQuerySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])


class ListLogQuerySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])
    min_date = serializers.DateField(required=False, format="%Y-%m-%d")
    max_date = serializers.DateField(required=False, format="%Y-%m-%d")
    keyword = serializers.CharField(required=False, max_length=255)
    page = serializers.IntegerField(default=1, min_value=1, max_value=50)