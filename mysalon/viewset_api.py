from mysalon.models import tbBooking
from .serializers import BookingSerializer
from rest_framework import viewsets
from rest_framework import permissions

class BukuViewset(viewsets.ModelViewSet):
    queryset = tbBooking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]