"""salon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mysalon import views
from mysalon.views import *
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from mysalon.viewset_api import *
from rest_framework import routers
from django.urls import include, re_path 
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


router = routers.DefaultRouter()
router.register('Buku', BukuViewset)

urlpatterns = [
    path('api/',include(router.urls)),
    path("admin/", admin.site.urls),
    re_path(r'^booking$', booking, name='booking'),
    re_path(r'^layanan$', layanan, name='layanan'),
    re_path(r'^about$', about, name='about'),
    path('bookingadmin/',bookingadmin),
    path('layananadmin/',layananadmin),
    path('layanan/',layanan),
    path('daftarstaff/',daftarstaff, name="daftarstaff"),
    path('daftarbookinganstaff/',daftarbookinganstaff, name="daftarbookinganstaff"),
    path('daftaruser/',daftaruser, name="daftaruser"),
    path('index_book',index_book),
    path('tambahbooking/',tambahbooking, name="tambahbooking"),
    path('tambahlayanan/',tambahlayanan, name="tambahlayanan"),
    path('tambahstaff/',tambahstaff, name="tambahstaff"),
    path('booking/ubah/<str:kode_id>',ubahbooking, name = "ubahbooking"),
    path('layanan/ubah/<str:namalayanan_id>',ubahlayanan, name = "ubahlayanan"),
    path('daftarstaff/ubah/<str:nama_id>',ubahstaff, name = "ubahstaff"),
    path('daftaruser/ubah/<str:nama_id>',ubahuser, name = "ubahuser"),
    path('booking/hapus/<str:kode_id>',hapusbooking, name = "hapusbooking"),
    path('api/get_bookings', views.get_bookings, name='get_bookings'),
    path('layanan/hapus/<str:namalayanan_id>',hapuslayanan, name = "hapuslayanan"),
    path('daftarstaff/hapus/<str:nama_id>',hapusstaff, name = "hapusstaff"),
    path('daftaruser/hapus/<str:nama_id>',hapususer, name = "hapususer"),
    path('login/', views.login_view, name='login'),
    path('logout/',LogoutView.as_view(next_page='home'), name='logout'),
    path('register/',register, name='register'),
    path('registeradmin/',registeradmin, name='registeradmin'),
    path('registerowner/',registerowner, name='registerowner'),
    path('export/xls/', export_xls, name='export_xls'),
    path('send_otp/', send_otp, name='send_otp'),
    re_path(r'^$', index, name='index'),
    re_path(r'^home$', index, name='home'),
    re_path(r'^bookingadmin$', bookingadmin, name='bookingadmin'),
    re_path(r'^layananadmin$', layananadmin, name='layananadmin'),
    re_path(r'^index_book$', index_book, name='index_book'),
    path('dashboarduser/', views.dashboard_user, name='dashboard_user'),
    path('dashboardstaff/', views.dashboard_staff, name='dashboard_staff'),
    path('dashboardowner/', views.dashboard_owner, name='dashboard_owner'),
    path('change_pass/', change_user_password, name='change_pass'),
    path('pass_change_success/', views.CustomPasswordChangeDoneView.as_view(), name='pass_change_success'),
    path('ubahstatus/<str:username>/', views.ubah_status, name='ubahstatus'),
    path('ubah_status_booking/<str:kode>/', views.ubah_status_booking, name='ubah_status_booking'),
    path('ubah_status_selesai/', ubah_status_selesai, name='ubah_status_selesai'),
    path('ubah_status_batal/', ubah_status_batal, name='ubah_status_batal'),
    path('viewbooking/<str:kode_id>/', viewbooking, name='viewbooking'),
    path('save_fcm_token/', save_fcm_token, name='save_fcm_token'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




