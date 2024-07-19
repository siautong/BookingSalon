from mysalon.models import tbBooking
from rest_framework import serializers

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbBooking
        fields = ['kode','nama','desk']