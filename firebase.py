# firebase.py
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate('E:\BookingSalon\serviceAccountKey.json')
firebase_admin.initialize_app(cred)
