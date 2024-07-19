from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from mysalon.models import tbBooking
from mysalon.models import tbLayanan
from mysalon.forms import FormBooking, FormLayanan
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from mysalon.resource import BookingResource
from datetime import date, datetime
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from mysalon.forms import CustomUserCreationForm
from mysalon.forms import CustomStaffCreationForm
from django.contrib.auth.models import Group
from django.http import JsonResponse
import random
import string
import twilio
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from mysalon.models import CustomUser
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from mysalon.models import CustomUser
from mysalon.models import Staff
from mysalon.models import tbProgress
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .forms import CustomPasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import time
from datetime import datetime, timedelta, time
import logging
import random
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
import uuid
from datetime import datetime, timedelta
from .models import tbProgress, Staff
from .forms import FormBooking
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.db.models import Sum
from django.core.paginator import Paginator
import os
from django.utils.dateparse import parse_datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FormBooking
from .models import Staff, tbProgress, CustomUser
from .utils import send_fcm_notification
import random
import uuid
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from pusher_config import pusher_client

@csrf_exempt
@login_required
def save_fcm_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fcm_token = data.get('fcm_token')
        print(f'Received FCM token: {fcm_token}')  # Tambahkan log untuk debug
        if fcm_token:
            request.user.fcm_token = fcm_token
            request.user.save()
            return JsonResponse({'status': 'success', 'message': 'Token saved successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Token not provided.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def check_operational_hours(booking_time):
    opening_time = time(10, 0)
    closing_time = time(17, 0)
    return opening_time <= booking_time <= closing_time

def check_booking_conflict(booking_date, booking_time, duration):
    end_time = (datetime.combine(datetime.today(), booking_time) + timedelta(minutes=duration)).time()
    overlapping_bookings = tbBooking.objects.filter(
        tanggal=booking_date,
        waktu__lt=end_time,
        waktu__gte=booking_time
    ).count()
    return overlapping_bookings < 5

def is_valid_slot(booking_date, booking_time, duration):
    if not check_operational_hours(booking_time):
        return False
    if not check_booking_conflict(booking_date, booking_time, duration):
        return False
    return True

def find_next_available_slot(booking_date, booking_time, duration):
    opening_time = time(10, 0)
    closing_time = time(17, 0)
    current_time = booking_time

    while current_time <= closing_time:
        if is_valid_slot(booking_date, current_time, duration):
            return current_time
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()

    return None


def index(request):
    now = datetime.now()

    # Check if the user has already granted notification permission
    notification_permission = request.session.get('notification_permission', None)

    if notification_permission is None:
        # If permission is not granted, ask for permission
        request.session['notification_permission'] = False  # Set default to False
        # You can render a popup or use JavaScript to request permission here

    return render(
        request, "index.html",
        {
            'title': "Glory Salon Booking Online",
            'message1': "Glory Salon Booking Online",
            'message2': "Selamat Datang",
            'content': " pada " + now.strftime("%A, %d %B, %Y at %X"),
            'notification_permission': notification_permission  # Pass permission status to template
        }
    )
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect user to the appropriate dashboard based on role
            if hasattr(user, 'is_superuser') and user.is_superuser and user.is_staff:
                return redirect('dashboard_owner')
            elif hasattr(user, 'is_staff') and user.is_staff:
                return redirect('dashboard_staff')
            else:
                return redirect('dashboard_user')
        else:
            if CustomUser.objects.filter(username=username).exists() or Staff.objects.filter(username=username).exists():
                messages.error(request, "Password yang Anda masukkan salah.")
            else:
                messages.error(request, "Username tidak ada.")
            return redirect('login')  # Redirect to login page after unsuccessful login

    return render(request, 'registration/login.html')

def get_bookings(request):
    bookings = tbBooking.objects.filter(namastatus__in=['Dikonfirmasi', 'Sudah di ACC']).values('waktu', 'namastatus')
    bookings_list = [
        {
            'waktu': booking['waktu'].isoformat() if isinstance(booking['waktu'], (datetime, date)) else booking['waktu'],
            'namastatus': booking['namastatus']
        }
        for booking in bookings
    ]
    return JsonResponse(bookings_list, safe=False)

def update_expired_bookings():
    one_day_ago = datetime.now() - timedelta(days=1)
    expired_bookings = tbBooking.objects.filter(waktu__lt=one_day_ago, namastatus__in=['Belum di ACC'])

    for booking in expired_bookings:
        booking.namastatus = 'Dibatalkan'
        booking.save()

@login_required(login_url=settings.LOGIN_URL)
def booking(request):
    user = request.user
    update_expired_bookings()  # Call the function to update expired bookings

    if request.method == 'POST':
        kata_kunci = request.POST.get('cari')
        if isinstance(user, Staff):
            if kata_kunci:
                bk = tbBooking.objects.filter(
                    Q(kode__icontains=kata_kunci) &
                    ~Q(namastatus__in=['Terselesaikan', 'Dibatalkan'])
                )
            else:
                bk = tbBooking.objects.exclude(
                    Q(namastatus='Terselesaikan') |
                    Q(namastatus='Dibatalkan')
                )
        else:
            if kata_kunci:
                bk = tbBooking.objects.filter(
                    Q(kode__icontains=kata_kunci) &
                    Q(user=user) &
                    ~Q(namastatus__in=['Terselesaikan', 'Dibatalkan'])
                )
            else:
                bk = tbBooking.objects.filter(
                    user=user
                ).exclude(
                    Q(namastatus='Terselesaikan') |
                    Q(namastatus='Dibatalkan')
                )
    else:
        if isinstance(user, Staff):
            bk = tbBooking.objects.exclude(
                Q(namastatus='Terselesaikan') |
                Q(namastatus='Dibatalkan')
            )
        else:
            bk = tbBooking.objects.filter(
                user=user
            ).exclude(
                Q(namastatus='Terselesaikan') |
                Q(namastatus='Dibatalkan')
            )

    paginator = Paginator(bk, 10)  # 10 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    isi = {
        'page_obj': page_obj
    }
    return render(request, 'booking.html', isi)

@login_required(login_url=settings.LOGIN_URL)
def bookingadmin(request):
    if request.POST:
        kata_kunci = request.POST['cari']
        bk = tbBooking.objects.filter(nama__icontains=kata_kunci)
        isi = {
        'bk' : bk,
}
    else:
        bk = tbBooking.objects.all()
        isi = {
        'bk' : bk
        }
    return render(request,'bookingadmin.html', isi)

def about(request):

    return render(request,"about.html")

   
def layanan(request):
    if request.method == 'POST':
        kata_kunci = request.POST.get('cari', '')
        ly = tbLayanan.objects.filter(namalayanan__icontains=kata_kunci)
    else:
        ly = tbLayanan.objects.all()
    
    paginator = Paginator(ly, 10)  # 10 layanan per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'layanan.html', context)

@user_passes_test(lambda u: u.is_superuser)
def daftarstaff(request):
    if request.POST:
        kata_kunci = request.POST['cari']
        staf = Staff.objects.filter(
            nama__icontains=kata_kunci,
            is_staff=True
        ) | Staff.objects.filter(
            nama__icontains=kata_kunci,
            is_superuser=True
        )
    else:
        staf = Staff.objects.filter(
            is_staff=True
        ) | Staff.objects.filter(
            is_superuser=True
        )

    isi = {
        'staf': staf
    }
    return render(request, 'daftarstaff.html', isi)

@user_passes_test(lambda u: u.is_staff)
def daftarbookinganstaff(request):
    try:
        # Mengambil username dari user yang sedang login
        username = request.user.username
        # Mengambil instance Staff yang terkait dengan username
        current_staff = Staff.objects.get(username=username)
    except Staff.DoesNotExist:
        # Jika user yang login bukan staff, kembalikan ke halaman login atau halaman lain
        return redirect('login')

    # Ambil semua booking progress yang berkaitan dengan staff yang sedang login
    progress_list = tbProgress.objects.filter(staff=current_staff, namastatus='Sudah di ACC')

    isi = {
        'progress_list': progress_list
    }
    return render(request, 'daftarbookinganstaff.html', isi)

logger = logging.getLogger(__name__)

@csrf_exempt
def ubah_status_selesai(request):
    if request.method == 'POST':
        progress_id = request.POST.get('id') or request.GET.get('id')  # Ambil id dari POST atau GET parameter
        logger.debug(f'Received request to change status for progress ID: {progress_id}')
        
        try:
            progress = get_object_or_404(tbProgress, id=progress_id)
            booking = get_object_or_404(tbBooking, kode=progress.kode)
            
            progress.namastatus = 'Terselesaikan'
            booking.namastatus = 'Terselesaikan'
            
            logger.debug(f'Changing status for progress ID {progress.id} to {progress.namastatus}')
            logger.debug(f'Changing status for booking ID {booking.id} to {booking.namastatus}')
            
            progress.save()
            booking.save()
            
            # Update staff status to 'Tersedia'
            staff = progress.staff
            if staff:
                staff.status = 'Tersedia'
                staff.save()
                logger.debug(f'Changing status for staff ID {staff.id} to {staff.status}')
            
            # Redirect back to the booking list page
            return redirect('daftarbookinganstaff')
        
        except tbProgress.DoesNotExist:
            logger.error(f'Progress with ID {progress_id} not found.')
            return JsonResponse({'success': False, 'error': 'Progress not found.'})
        except tbBooking.DoesNotExist:
            logger.error(f'Booking with kode {progress.kode} not found.')
            return JsonResponse({'success': False, 'error': 'Booking not found.'})
    else:
        logger.error('Invalid request method. Only POST is allowed.')
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

logger = logging.getLogger(__name__)

@csrf_exempt
def ubah_status_batal(request):
    if request.method == 'POST':
        progress_id = request.POST.get('id') or request.GET.get('id')
        if not progress_id:
            return JsonResponse({'success': False, 'error': 'Progress ID not provided.'})
        
        try:
            progress = get_object_or_404(tbProgress, id=progress_id)
            booking = get_object_or_404(tbBooking, kode=progress.kode)
            
            # Ubah status pada kedua objek
            progress.namastatus = 'Dibatalkan'
            booking.namastatus = 'Dibatalkan'
            
            # Simpan perubahan status
            progress.save()
            booking.save()
            
            # Update staff status to 'Tersedia'
            staff = progress.staff
            if staff:
                staff.status = 'Tersedia'
                staff.save()
                logger.debug(f'Changing status for staff ID {staff.id} to {staff.status}')
            
            logger.debug(f'Changing status for progress ID {progress.id} to {progress.namastatus}')
            logger.debug(f'Changing status for booking ID {booking.id} to {booking.namastatus}')
            
            # Redirect back to the booking list page
            return redirect('daftarbookinganstaff')
        
        except tbProgress.DoesNotExist:
            logger.error(f'Progress with ID {progress_id} not found.')
            return JsonResponse({'success': False, 'error': 'Progress not found.'})
        except tbBooking.DoesNotExist:
            logger.error(f'Booking with kode {progress.kode} not found.')
            return JsonResponse({'success': False, 'error': 'Booking not found.'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@user_passes_test(lambda u: u.is_staff)
def daftaruser(request):
    if request.POST:
        kata_kunci = request.POST['cari']
        user = CustomUser.objects.filter(
            nama__icontains=kata_kunci,
            is_staff=False,
            is_superuser=False
        )
    else:
        user = CustomUser.objects.filter(
            is_staff=False,
            is_superuser=False
        )

    isi = {
        'user': user
    }
    return render(request, 'daftaruser.html', isi)

CustomUser = get_user_model()

@user_passes_test(lambda u: u.is_superuser)
def tambahstaff(request):
    if request.method == 'POST':
        form = CustomStaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if 'is_staff' in request.POST:
                user.is_staff = True
            else:
                user.is_staff = False
            user.save()
            messages.success(request, 'Staff berhasil ditambahkan!')
            return redirect('daftarstaff')
    else:
        form = CustomStaffCreationForm()

    return render(request, 'tambahstaff.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)    
def layananadmin(request):
    if request.POST:
        kata_kunci = request.POST['cari']
        ly = tbLayanan.objects.filter(namalayanan__icontains=kata_kunci)
        isi = {
        'ly' : ly,
}
    else:
        ly = tbLayanan.objects.all()
        isi = {
        'ly' : ly
        }
    return render(request,'layananadmin.html', isi)

def index_book(request):
    return render(request,'index_book.html')

@login_required(login_url=settings.LOGIN_URL)
def tambahbooking(request):
    if request.method == 'POST':
        form = FormBooking(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            service_duration = booking.namalayanan.pengerjaan  # Assuming `pengerjaan` is the duration of the service in minutes

            # Assign user-related fields from request
            booking.namauser = request.POST.get('namauser')
            booking.alamat = request.POST.get('alamat')
            booking.nomoruser = request.POST.get('nomoruser')
            booking.user = request.user  # Set the user who is currently logged in
            
            # Check if the booking time is within operational hours and not conflicting
            if not is_valid_slot(booking.tanggal, booking.waktu, service_duration):
                new_time = find_next_available_slot(booking.tanggal, booking.waktu, service_duration)
                if new_time:
                    booking.waktu = new_time
                    booking.save()
                    messages.success(request, f"Booking berhasil dilakukan pada {new_time}.")
                else:
                    messages.error(request, "Tidak ada slot yang tersedia dalam jam operasional. Silakan pilih hari lain.")
                    return redirect('tambahbooking')
            else:
                booking.save()
                messages.success(request, 'Booking berhasil dilakukan.')

                # Debugging: Print to check if this block is executed
                print("Booking created, triggering Pusher event...")

                # Kirim notifikasi ke Pusher
                pusher_client.trigger('booking-channel', 'booking-created', {
                    'message': 'Bookingan berhasil dibuat.'
                })
                
                # Check if the booking status is 'Sudah di ACC'
                if booking.namastatus == 'Sudah di ACC':
                    # Get all available staff
                    available_staff = Staff.objects.filter(status='Tersedia')
                    if available_staff.exists():
                        # Select a random available staff
                        random_staff = random.choice(available_staff)

                        # Generate a unique kodestaff using UUID
                        kodestaff = str(uuid.uuid4())[:10]  # Mengambil 10 karakter pertama dari UUID

                        # Create tbProgress based on tbBooking data
                        progress = tbProgress(
                            kodestaff=kodestaff,
                            kode=booking.kode,
                            namauser=booking.namauser,
                            alamat=booking.alamat,
                            nomoruser=booking.nomoruser,
                            tanggal=booking.tanggal,
                            waktu=booking.waktu,
                            harga=booking.harga,
                            namalayanan=booking.namalayanan,
                            staff=random_staff  # Set the randomly selected available staff
                        )
                        progress.save()

                        # Update the selected staff status to 'Sedang Bekerja'
                        random_staff.status = 'Sedang Bekerja'
                        random_staff.save()

                        # Kirim notifikasi ke staff
                        if random_staff.fcm_token:
                            send_fcm_notification(random_staff.fcm_token, 'Tugas Baru', f'Anda memiliki tugas baru dengan kode {booking.kode}.')

                        messages.success(request, 'Booking berhasil dipindahkan ke Progress.')
                    else:
                        # Calculate new time 30 minutes later
                        new_time = booking.waktu + timedelta(minutes=30)
                        booking.waktu = new_time
                        booking.save()

                        # Format new_time for display
                        formatted_new_time = new_time.strftime('%H:%M')

                        # Update booking status to 'Belum di ACC' if it's not already 'Sudah di ACC'
                        if booking.namastatus != 'Sudah di ACC':
                            booking.namastatus = 'Belum di ACC'
                            booking.save()

                        messages.error(request, f"Tidak ada staff yang tersedia. Mohon Maaf saat ini tidak ada Staff yang tersedia sehingga jadwal Anda kami undur hingga {formatted_new_time}.")

                return redirect('booking')  # Change 'booking' to the target URL after successful booking
        
        else:
            messages.error(request, "Terjadi kesalahan dalam form booking.")
    else:
        form = FormBooking()
    
    return render(request, 'tambahbooking.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def tambahlayanan(request):
    if request.method == 'POST':
        form = FormLayanan(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            pesan = "Layanan sudah tersimpan"
            # Optionally, redirect to a success page or clear form data after saving
            form = FormLayanan()  # Reset form after successful submission
        else:
            pesan = "Ada kesalahan dalam menyimpan layanan"
    else:
        form = FormLayanan()
        pesan = None  # No message initially

    isi = {
        'form': form,
        'pesan': pesan,
    }
    return render(request, 'tambahlayanan.html', isi)

def viewbooking(request, kode_id):
    # Ambil objek booking berdasarkan kode
    booking = get_object_or_404(tbBooking, kode=kode_id)
    
    # Kirimkan data booking ke template
    context = {
        'booking': booking
    }
    return render(request, 'viewbooking.html', context)

logger = logging.getLogger(__name__)

@login_required(login_url=settings.LOGIN_URL)
def ubahbooking(request, kode_id):
    try:
        bk = tbBooking.objects.get(kode=kode_id)
    except tbBooking.DoesNotExist:
        messages.error(request, "Booking tidak ditemukan.")
        return redirect('booking')  # Ganti dengan URL redirect yang benar

    if request.method == 'POST':
        form = FormBooking(request.POST, instance=bk)
        if form.is_valid():
            # Simpan instance dengan nilai dari form
            booking = form.save(commit=False)
            
            # Assign nilai dari request.POST ke instance tbBooking
            booking.namauser = request.POST.get('namauser')
            booking.alamat = request.POST.get('alamat')
            booking.nomoruser = request.POST.get('nomoruser')

            booking.save()
            messages.success(request, "Data berhasil di-update")
            return redirect('booking')  # Ganti dengan URL redirect yang benar
        else:
            messages.error(request, "Terjadi kesalahan dalam pengisian form.")
    else:
        form = FormBooking(instance=bk)
    
    isi = {
        'form': form,
        'bk': bk,
    }
    
    return render(request, 'ubahbooking.html', isi)


@user_passes_test(lambda u: u.is_staff)
def ubahlayanan(request, namalayanan_id):
    ly = tbLayanan.objects.get(namalayanan = namalayanan_id)
    template = "ubahlayanan.html"
    if request.POST:
        form = FormLayanan(request.POST, request.FILES, instance=ly)
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil di-update")
            return redirect('layanan')
    else:
        form = FormLayanan(instance=ly)
        isi = {
        'form':form,
        'ly':ly,
        }
        return render(request,template,isi)
    
@user_passes_test(lambda u: u.is_superuser)
def ubahstaff(request, nama_id):
    staf = Staff.objects.get(nama = nama_id)
    template = "ubahstaff.html"
    if request.POST:
        form = CustomStaffCreationForm(request.POST, request.FILES, instance=staf)
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil di-update")
            return redirect('daftarstaff')
    else:
        form = CustomStaffCreationForm(instance=staf)
        isi = {
        'form':form,
        'staf':staf,
        }
        return render(request,template,isi)

def ubah_status_booking(request, kode):
    booking = get_object_or_404(tbBooking, kode=kode)

    if request.method == 'POST':
        # Ubah status booking menjadi Sudah di ACC
        booking.namastatus = 'Sudah di ACC'
        booking.save()

        # Cari staff yang tersedia secara acak
        available_staff = Staff.objects.filter(status='Tersedia')
        if available_staff.exists():
            random_staff = random.choice(available_staff)

            # Ubah status staff menjadi Sedang Bekerja
            random_staff.status = 'Sedang Bekerja'
            random_staff.save()

            # Generate kode staff menggunakan UUID
            kodestaff = str(uuid.uuid4())[:10]

            # Simpan data ke tbProgress
            progress = tbProgress.objects.create(
                kodestaff=kodestaff,
                kode=booking.kode,
                tanggal=booking.tanggal,
                waktu=booking.waktu,
                harga=booking.harga,
                namalayanan=booking.namalayanan,
                staff=random_staff
            )

            messages.success(request, 'Booking telah berhasil di ACC.')
        else:
            messages.error(request, 'Tidak ada staff yang tersedia untuk menangani booking ini.')

    return redirect('booking')  
    
@login_required(login_url=settings.LOGIN_URL)
def ubahuser(request, nama_id):
    user = CustomUser.objects.get(nama = nama_id)
    template = "ubahuser.html"
    if request.POST:
        form = CustomUserCreationForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil di-update")
            return redirect('daftaruser')
    else:
        form = CustomUserCreationForm(instance=user)
        isi = {
        'form':form,
        'user':user,
        }
        return render(request,template,isi)

@login_required(login_url=settings.LOGIN_URL)
def hapusbooking(request, kode_id):
    if request.method == 'POST':
        booking = get_object_or_404(tbBooking, kode=kode_id)
        booking.delete()
        messages.success(request, "Data Berhasil dihapus!")
        return redirect('booking')
    else:
        return redirect('booking')


@user_passes_test(lambda u: u.is_superuser)
def hapuslayanan(request, namalayanan_id):
    try:
        ly = tbLayanan.objects.get(namalayanan=namalayanan_id)
        
        # Get the path of the foto
        foto_path = ly.foto.path
        
        # Delete the object from the database
        ly.delete()
        
        # Delete the foto file from the filesystem
        if os.path.exists(foto_path):
            os.remove(foto_path)
        
        messages.success(request, "Data Berhasil dihapus!") 
    except tbLayanan.DoesNotExist:
        messages.error(request, "Data tidak ditemukan!")
    
    return redirect('layanan')
@user_passes_test(lambda u: u.is_superuser)
def hapususer(request, nama_id):
    user = get_object_or_404(CustomUser, nama=nama_id)
    user.delete()
    messages.success(request, "User berhasil dihapus!")
    return redirect('daftaruser')

@user_passes_test(lambda u: u.is_superuser)
def hapusstaff(request, nama_id):
    staf = get_object_or_404(Staff, nama=nama_id)
    staf.delete()
    messages.success(request, "Staff berhasil dihapus dari database!")
    return redirect('daftarstaff')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def registeradmin(request):
    if request.method == 'POST':
        form = CustomStaffCreationForm(request.POST)
        if form.is_valid():
            otp_entered = request.POST.get('otp', '')  # Ambil OTP yang diinputkan oleh pengguna
            otp_sent = request.session.get('otp_sent', '')  # Ambil OTP yang dikirimkan sebelumnya

            if otp_entered == otp_sent:  # Periksa apakah OTP yang diinputkan sesuai dengan OTP yang dikirimkan
                user = form.save(commit=False)
                user.is_staff = True  # Menjadikan user sebagai staff
                user.save()

                # Menambahkan user ke grup 'Admin' jika grup tersebut sudah ada
                admin_group, created = Group.objects.get_or_create(name='Admin')
                user.groups.add(admin_group)

                messages.success(request, 'Registrasi berhasil.')
                return redirect('login')  # Redirect to login page after successful registration
            else:
                messages.error(request, 'OTP yang Anda masukkan salah.')
        else:
            messages.error(request, 'Registrasi gagal. Silakan periksa kembali input Anda.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registeradmin.html', {'form': form})

def registerowner(request):
    if request.method == 'POST':
        form = CustomStaffCreationForm(request.POST)
        if form.is_valid():
            otp_entered = request.POST.get('otp')
            otp_sent = request.session.get('otp_sent')
            
            if otp_entered == otp_sent:
                user = form.save(commit=False)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                
                try:
                    admin_group = Group.objects.get(name='Owner')
                except Group.DoesNotExist:
                    admin_group = Group.objects.create(name='Owner')
                
                if admin_group:
                    user.groups.add(admin_group)
                    
                return redirect('login')  # Redirect to login page after successful registration
            else:
                return JsonResponse({'error': 'Invalid OTP'})  # Return error response if OTP is invalid
    else:
        form = CustomUserCreationForm()
    return render(request, 'registerowner.html', {'form': form})

def export_xls(request):
    booking = BookingResource()
    dataset = booking.export()
    response = HttpResponse(dataset.xls, content_type = "application/vnd.ms-excel")

    response['content-disposition'] = 'attachment; filename=Laporan Booking Anda.xls'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    if not request.user.has_perm('auth.delete_user'):
        return Response({'error': 'You do not have permission to delete users.'}, status=status.HTTP_403_FORBIDDEN)

    # Delete user logic
    return Response({'success': 'User deleted successfully.'}, status=status.HTTP_200_OK)

def send_otp(request):
    # Logic untuk mengirim OTP
    # Contoh: Generate OTP secara acak dan kirim ke nomor telepon
    otp = generate_random_otp()
    request.session['otp_sent'] = otp  # Simpan OTP yang dikirimkan di session
    send_otp_to_phone_number(otp, '+62859196196283')  # Ganti nomor telepon dengan nomor tujuan

    # Response JSON
    return JsonResponse({'success': True})

def generate_random_otp(length=6):
    """Generate random OTP (One Time Password)"""
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def send_otp_to_phone_number(otp, phone_number):
    """Send OTP to a phone number"""
    # Implement logic to send OTP to the provided phone number
    # You can use Twilio or any other SMS gateway for this purpose
    # For example:
    # Send SMS using Twilio
    account_sid = 'AC1ea71c4caa8d4a475f7d0aa263795480'
    auth_token = 'a9a4814ef063e9f78ce8d03b5f3399c3'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
         body=f'Your OTP is: {otp}',
         from_='+13396661811',
         to='+62859196196283'
     )
    print(message.sid)
    

@login_required
def dashboard_user(request):
    # Menghitung jumlah layanan yang tersedia dan Bookingan user
    layanan_count = tbLayanan.objects.all()
    total_layanan = layanan_count.count()

    # Jika tidak ada user sebelumnya, hasil rendernya adalah 0 (handled by default with count())

    context = {
        'total_layanan': total_layanan,
    }

    return render(request, 'dashboarduser/index.html', context)

@user_passes_test(lambda u: u.is_staff)
def dashboard_staff(request):
    # logic for staff dashboard
    return render(request, 'dashboardstaff/index.html')

@user_passes_test(lambda u: u.is_superuser)
def dashboard_owner(request):
    user_count = CustomUser.objects.filter(is_staff=False, is_superuser=False)
    staff_count = Staff.objects.filter(is_staff=True)
    total_user = user_count.count()
    total_staff = staff_count.count()

    total_belum_di_acc = tbBooking.objects.filter(namastatus='Belum di ACC').count()
    total_sudah_di_acc = tbBooking.objects.filter(namastatus='Sudah di ACC').count()
    total_booking = total_belum_di_acc + total_sudah_di_acc

    total_sum_harga = tbBooking.objects.filter(namastatus__in=['Belum di ACC', 'Sudah di ACC']).aggregate(total=Sum('harga'))['total']

    booking_list = tbBooking.objects.filter(namastatus='Belum di ACC').order_by('-id')[:5]

    bookings = tbBooking.objects.filter(namastatus__in=['Belum di ACC', 'Sudah di ACC']).values('waktu', 'namastatus')
    bookings_list = [
        {
            'title': 'Sudah di ACC' if booking['namastatus'] == 'Sudah di ACC' else 'Belum di ACC',
            'start': booking['waktu'].isoformat() if isinstance(booking['waktu'], (datetime, date)) else booking['waktu'],
            'color': 'green' if booking['namastatus'] == 'Sudah di ACC' else 'red'
        }
        for booking in bookings
    ]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'bookings': bookings_list}, safe=False)

    context = {
        'total_user': total_user,
        'total_staff': total_staff,
        'total_booking': total_booking,
        'total_sum_harga': total_sum_harga,
        'booking_list': booking_list,
    }

    return render(request, 'dashboardowner/index.html', context)



class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_pass.html'
    success_url = reverse_lazy('pass_change_success')

    def form_valid(self, form):
        user = self.request.user
        old_password = form.cleaned_data['old_password']
        new_password = form.cleaned_data['password1']
        
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(self.request, user)
            return HttpResponseRedirect(self.get_success_url())
        else:
            form.add_error('old_password', 'Password lama tidak benar.')
            return self.form_invalid(form)

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'pass_change_success.html'

def change_user_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')  # Ambil password lama dari form
        new_password = request.POST.get('password1')  # Ambil password baru dari form
        username = request.user.username  # Dapatkan username dari user yang sedang login
        
        # Authenticate user
        user = authenticate(username=username, password=old_password)
        
        if user is not None:
            # Jika password lama sesuai, ubah password baru
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Update session authentication hash untuk menghindari logout
            messages.success(request, 'Password berhasil diubah.')
            return redirect('pass_change_success')  # Redirect ke halaman sukses
        else:
            messages.error(request, 'Password lama tidak sesuai.')
    
    return render(request, 'change_pass.html')  # Render halaman ganti password

@user_passes_test(lambda u: u.is_superuser)
def ubah_status(request, username):
    staff = get_object_or_404(Staff, username=username)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Staff.STATUS_CHOICES).keys():
            staff.status = status
            staff.save()
            messages.success(request, 'Status staff berhasil diubah.')
        else:
            messages.error(request, 'Status tidak valid.')
    
    return redirect('daftarstaff')  # Ganti dengan nama view yang menampilkan daftar staff
