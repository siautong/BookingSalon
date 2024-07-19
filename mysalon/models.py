from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group
from django.db import models
from django.conf import settings
from django.core.exceptions import PermissionDenied
import uuid
import random
from django.db import models
from django.conf import settings
import uuid
import random
from django.contrib.auth import get_user_model

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email=email, username=username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    nama = models.CharField(max_length=50)
    alamat = models.TextField()
    nohp = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_users')
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nama', 'email', 'nohp', 'alamat']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class StaffManager(BaseUserManager):
    def create_staff(self, email, username, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        staff = self.model(email=email, username=username)
        staff.set_password(password)
        staff.save(using=self._db)
        return staff

class Staff(AbstractBaseUser):
    STATUS_CHOICES = [
        ('Tersedia', 'Tersedia'),
        ('Sedang Bekerja', 'Sedang Bekerja'),
        ('Tidak Tersedia', 'Tidak Tersedia'),
    ]

    nama = models.CharField(max_length=50)
    alamat = models.TextField()
    nohp = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True, related_name='staff_users')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Tersedia')
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nama', 'email', 'nohp', 'alamat']

    objects = StaffManager()

    def __str__(self):
        return self.username

class tbLayanan(models.Model):
    namalayanan = models.CharField(max_length=50)
    harga = models.IntegerField()
    foto = models.ImageField(upload_to='media/foto', default='logo.png')
    pengerjaan = models.IntegerField()

    def __str__(self):
        return self.namalayanan

class tbProgress(models.Model):
    kodestaff = models.CharField(max_length=10, unique=True, blank=True)
    kode = models.CharField(max_length=10, unique=True, blank=True)
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='progress', null=True, blank=True)
    namalayanan = models.ForeignKey('tbLayanan', on_delete=models.CASCADE, related_name='namalayanan_progress')
    tanggal = models.DateTimeField(null=True)
    waktu = models.TimeField()
    harga = models.IntegerField(null=True, blank=True)
    namauser = models.TextField(blank=False, null=False)
    alamat = models.TextField(blank=False, null=False)
    nomoruser = models.TextField(blank=False, null=False)
    namastatus = models.CharField(max_length=15, choices=[('Sudah di ACC', 'Sudah di ACC'), ('Belum di ACC', 'Belum di ACC'), ('Terselesaikan', 'Terselesaikan'), ('Dibatalkan', 'Dibatalkan')], default='Belum di ACC')

    def save(self, *args, **kwargs):
        from .models import tbBooking, Staff  # Impor lokal di sini untuk menghindari circular import
        
        if self.kode:
            booking = tbBooking.objects.get(kode=self.kode)
            self.namalayanan = booking.namalayanan
            self.tanggal = booking.tanggal
            self.waktu = booking.waktu
            self.harga = booking.harga
            self.namauser = booking.namauser
            self.nomoruser = booking.nomoruser
            self.alamat = booking.alamat
            self.namastatus = booking.namastatus  # Assigning tbBooking status to namastatus field

            if not self.kodestaff:
                self.kodestaff = self.generate_unique_kodestaff()

            super().save(*args, **kwargs)

            # Check if status is changed to 'Sudah di ACC'
            if booking.namastatus == 'Sudah di ACC' and not self.staff:
                # Select a random available staff
                available_staff = Staff.objects.filter(status='Tersedia').order_by('?').first()
                if available_staff:
                    self.staff = available_staff
                    self.save()  # Save again to update `staff` field

                    # Update staff status
                    available_staff.status = 'Sedang Bekerja'
                    available_staff.save()

    def generate_unique_kodestaff(self):
        return str(uuid.uuid4()).split('-')[0]

    def __str__(self):
        return self.kodestaff

class tbStatus(models.Model):
    STATUS_ACC_CHOICES = [
        ('Sudah di ACC', 'Sudah di ACC'),
        ('Belum di ACC', 'Belum di ACC'),
        ('Terselesaikan', 'Terselesaikan'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    namastatus = models.CharField(max_length=15, choices=STATUS_ACC_CHOICES, default='Belum Di Acc')

    def __str__(self):
        return self.namastatus

CustomUser = get_user_model()

class tbBooking(models.Model):
    STATUS_ACC_CHOICES = [
        ('Sudah di ACC', 'Sudah di ACC'),
        ('Belum di ACC', 'Belum di ACC'),
        ('Terselesaikan', 'Terselesaikan'),
        ('Dibatalkan', 'Dibatalkan'),
    ]

    kode = models.CharField(max_length=10, unique=True, blank=True)
    namalayanan = models.ForeignKey('tbLayanan', on_delete=models.CASCADE, related_name='namalayanan_bookings')
    desk = models.TextField(blank=True, null=True)
    namauser = models.TextField(blank=False, null=False)
    alamat = models.TextField(blank=False, null=False)
    nomoruser = models.TextField(null=False, blank=False)
    tanggal = models.DateTimeField(null=True)
    waktu = models.TimeField()
    harga = models.IntegerField(null=True, blank=True)  # Harga diambil dari tbLayanan
    namastatus = models.CharField(max_length=15, choices=STATUS_ACC_CHOICES, default='Belum di ACC')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)  # Tambahkan field user

    def save(self, *args, **kwargs):
        # Set harga berdasarkan namalayanan yang dipilih
        if self.namalayanan:
            self.harga = self.namalayanan.harga
        
        # Generate kode jika belum ada
        if not self.kode:
            self.kode = self.generate_unique_kode()
        
        super().save(*args, **kwargs)

    def generate_unique_kode(self):
        return str(uuid.uuid4()).split('-')[0]  # menghasilkan kode unik 8 karakter

    def __str__(self):
        return self.kode