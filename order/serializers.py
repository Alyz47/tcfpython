from rest_framework import serializers
from .models import Order
from listing.serializers import ReadListingSerializer

class OrderSerializer(serializers.ModelSerializer):
    listing = ReadListingSerializer()
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')