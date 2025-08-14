from rest_framework import serializers


class ImportLogSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])
    log_time = serializers.DateTimeField()
    file_name = serializers.CharField(max_length=255)
    content = serializers.CharField()


class LogSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)
    type = serializers.ChoiceField(choices=["post", "data"])
    log_time = serializers.DateTimeField()
    file_name = serializers.CharField(max_length=255)
    content = serializers.CharField()


class LogListItemSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64, help_text="Document ID")
    type = serializers.ChoiceField(choices=["post", "data"], help_text="Log type")
    log_time = serializers.DateTimeField(help_text="Log timestamp")
    file_name = serializers.CharField(max_length=255, help_text="Log file name")
    preview = serializers.CharField(
        allow_blank=True, 
        help_text="Preview: highlighted text with keyword, or first 100 chars without"
    )


class GetLogQuerySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])


class ListLogQuerySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["post", "data"])
    min_date = serializers.DateField(required=False, format="%Y-%m-%d")
    max_date = serializers.DateField(required=False, format="%Y-%m-%d")
    keyword = serializers.CharField(required=False, max_length=255)
    page = serializers.IntegerField(default=1, min_value=1, max_value=50)