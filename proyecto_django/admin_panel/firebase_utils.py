import firebase_admin
from firebase_admin import credentials, auth, firestore
import re
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


logger = logging.getLogger(__name__)

def initialize_firebase():
    cred = credentials.Certificate("path/to/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()

def clean_rut(rut):
    """Elimina puntos y guión del RUT y convierte a mayúsculas"""
    rut_clean = re.sub(r'[^0-9kK]', '', rut)
    return rut_clean.upper()

def create_firebase_user(email, rut):
    password = clean_rut(rut)
    
    # Validar longitud mínima de contraseña
    if len(password) < 8:
        raise ValueError('El RUT debe tener al menos 8 dígitos para generar una contraseña válida')
    
    user = auth.create_user(
        email=email,
        password=password,
        disabled=False
    )
    return user.uid

def disable_user(uid):
    auth.update_user(uid, disabled=True)

def enable_user(uid):
    auth.update_user(uid, disabled=False)

def get_user_by_email(email):
    return auth.get_user_by_email(email)

def get_firestore_user(rut):
    db = firestore.client()
    # Buscar en ambas colecciones
    medico_ref = db.collection('usuarios_medicos').where('rut', '==', rut).limit(1)
    farma_ref = db.collection('usuarios_farmaceuticos').where('rut', '==', rut).limit(1)
    
    medico = next(medico_ref.stream(), None)
    farma = next(farma_ref.stream(), None)
    
    return medico.to_dict() if medico else farma.to_dict() if farma else None

def update_firestore_user(rut, data, role):
    db = firestore.client()
    collection = 'usuarios_medicos' if role == 'medico' else 'usuarios_farmaceuticos'
    
    # Buscar documento por RUT
    user_ref = db.collection(collection).where('rut', '==', rut).limit(1)
    doc = next(user_ref.stream(), None)
    
    if doc:
        doc.reference.update(data)
        return True
    return False


def send_credentials_email(email, rut, password, nombre):
    """Envía las credenciales por correo electrónico"""
    try:
        subject = 'Bienvenido al Sistema de Recetas Médicas'
        
        context = {
            'nombre': nombre,
            'rut': rut,
            'password': password,
            'app_name': 'Sistema de Recetas Médicas'
        }
        
        html_message = render_to_string('admin/credentials_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando correo a {email}: {str(e)}")
        return False