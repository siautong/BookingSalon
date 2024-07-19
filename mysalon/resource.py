from import_export import resources
from mysalon.models import tbBooking
from import_export.fields import Field

class BookingResource(resources.ModelResource):
    kode = Field(attribute='kode', column_name='Nomor Serial Buku')
    class Meta:
        model = tbBooking
        fields = ['kode','nama','desk']
        export_order = ['nama','kode','desk']
        
       