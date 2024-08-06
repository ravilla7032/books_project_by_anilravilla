from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mobile_number = serializers.IntegerField()
    is_staff = serializers.BooleanField()
    age = serializers.IntegerField()
    address = serializers.CharField()
    gender = serializers.CharField()

