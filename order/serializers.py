from rest_framework import serializers
from .models import Order
from listing.models import Listing
from listing.serializers import ReadListingSerializer


class ReadOrderSerializer(serializers.ModelSerializer):
    listing = ReadListingSerializer()

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'status', 'listing', 'address', 'is_delivered']
        read_only_fields = ('created', 'modified')


class WriteOrderSerializer(serializers.ModelSerializer):
    buyer = serializers.CharField(source="buyer.get_username", read_only=True)
    # listing = ReadListingSerializer()
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'status', 'listing', 'address', 'is_delivered']
        read_only_fields = ('created', 'modified')

    def create(self, validated_data):
        listing_data = validated_data.pop('listing')
        listing = Listing.objects.get(id=listing_data.id)
        order = Order.objects.create(listing=listing, **validated_data)
        return order

    def update(self, instance, validated_data):
        listing_data = validated_data.pop('listing', None)
        delivered_data = validated_data.pop('is_delivered', None)
        order_listing = instance.listing

        # If there are changes to listing (is_sold changing to True)
        if listing_data:
            order_listing.is_sold = listing_data.get('is_sold', order_listing.is_sold)
            order_listing.save()
        # If there are changes to order (is_delivered changing to True)
        if delivered_data:
            instance.is_delivered = delivered_data
            instance.save()

        return instance
