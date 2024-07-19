# mysalon/templatetags/custom_filters.py
from django import template
from datetime import datetime
import locale

register = template.Library()

@register.filter
def format_tanggal(value):
    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')  # Set locale ke bahasa Indonesia
    return value.strftime('%d %B %Y')  # Format tanggal

@register.filter
def format_waktu(value):
    return value.strftime('%H:%M')  # Format waktu 24 jam
