from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .firebase_utils import *
from .forms import UserCreationForm, UserEditForm
from .firebase_utils import send_credentials_email
from django.contrib import messages
from firebase_admin import auth as firebase_auth
from django.views.decorators.csrf import csrf_protect

from .analytics_utils import obtener_metricas_clave

from datetime import datetime

import logging

logger = logging.getLogger(__name__)  # Para registrar errores en logs


@login_required
def home(request):
    if not request.user.is_admin:
        return redirect('login')

    db = firestore.client()

    total_medicos = len(db.collection('usuarios_medicos').get())
    total_farmaceuticos = len(db.collection('usuarios_farmaceuticos').get())
    total_users = total_medicos + total_farmaceuticos

    # Leer parámetros GET
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    # Valores por defecto si no hay fechas
    fecha_inicio = start_date or "7daysAgo"
    fecha_fin = end_date or "today"

    # Validación de formato y orden
    try:
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if start_dt > end_dt:
                raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

            # (Opcional) Limitar a un máximo de 60 días, por ejemplo
            delta = (end_dt - start_dt).days
            if delta > 60:
                raise ValueError("El rango de fechas no debe exceder los 60 días.")
    except Exception as e:
        messages.warning(request, f"Fechas inválidas: {e}")
        fecha_inicio = "7daysAgo"
        fecha_fin = "today"
        start_date = ""
        end_date = ""

    # Obtener métricas con fechas validadas
    try:
        analytics_data = obtener_metricas_clave(fecha_inicio, fecha_fin)
    except Exception as e:
        analytics_data = {
            'active_users': "Error",
            'new_users': "Error",
            'sessions': "Error",
            'engagement_time': "Error"
        }

        mensaje_admin = "No se pudieron obtener las métricas del periodo seleccionado."
        if settings.DEBUG:
            messages.error(request, f"{mensaje_admin} Detalles: {e}")
        else:
            messages.error(request, f"{mensaje_admin} Intente con otro rango o contacte al soporte.")

        # Registrar en log si lo deseas
        logger.exception("Error al obtener métricas de Google Analytics")

    return render(request, 'admin/home.html', {
        'total_users': total_users,
        'total_medicos': total_medicos,
        'total_farmaceuticos': total_farmaceuticos,
        'analytics': analytics_data,
        'start_date': start_date,
        'end_date': end_date,
    })


@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                rut = data['rut']
                email = data['correo']
                role = data['rol']
                nombre = data['nombre']
                
                # Crear usuario en Firebase Auth
                rut_limpio = clean_rut(rut)
                uid = create_firebase_user(email, rut_limpio)
                
                # Preparar datos para Firestore
                user_data = {
                    'nombre': nombre,
                    'apellidoPaterno': data['apellido_paterno'],
                    'apellidoMaterno': data['apellido_materno'] or "",
                    'correo': email,
                    'rol': role,
                    'rut': rut,
                    'activo': True
                }
                
                # Campos específicos por rol
                if role == 'medico':
                    user_data['especialidad'] = data['especialidad'] or "General"
                    user_data['firmaBase64'] = data['firma_base64'] or ""
                
                # Guardar en Firestore
                db = firestore.client()
                collection = 'usuarios_medicos' if role == 'medico' else 'usuarios_farmaceuticos'
                db.collection(collection).document(uid).set(user_data)
                
                # Enviar credenciales por correo
                if send_credentials_email(email, rut, rut_limpio, nombre):
                    messages.success(request, 'Usuario creado y correo enviado exitosamente')
                else:
                    messages.warning(request, 'Usuario creado, pero falló el envío de correo')
                
                return redirect('list_users')
            
            except firebase_auth.EmailAlreadyExistsError:
                form.add_error('correo', 'Este correo ya está registrado')
            except Exception as e:
                messages.error(request, f'Error al crear usuario: {str(e)}')
        else:
            # Agregar mensajes de error específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'admin/create_user.html', {'form': form})

@login_required
def list_users(request):
    db = firestore.client()
    
    # Capturar filtro rol
    rol_filtro = request.GET.get('rol', '').lower()
    
    # Traer usuarios según filtro rol
    if rol_filtro == 'medico':
        users = [doc.to_dict() for doc in db.collection('usuarios_medicos').stream()]
    elif rol_filtro == 'farmaceutico':
        users = [doc.to_dict() for doc in db.collection('usuarios_farmaceuticos').stream()]
    else:
        medicos = [doc.to_dict() for doc in db.collection('usuarios_medicos').stream()]
        farmaceuticos = [doc.to_dict() for doc in db.collection('usuarios_farmaceuticos').stream()]
        users = medicos + farmaceuticos
    
    # Búsqueda por nombre, rut o correo
    search_query = request.GET.get('q', '')
    if search_query:
        users = [
            u for u in users
            if (search_query.lower() in u.get('nombre', '').lower() or
                search_query.lower() in u.get('rut', '').lower() or
                search_query.lower() in u.get('correo', '').lower())
        ]
    
    # Paginación
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/list_users.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'rol_filtro': rol_filtro
    })


@login_required
def edit_user(request, rut):
    user = get_firestore_user(rut)
    if not user:
        return redirect('list_users')
    
    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            update_data = {
                'nombre': data['nombre'],
                'apellidoPaterno': data['apellido_paterno'],
                'apellidoMaterno': data['apellido_materno'] or "",
                'activo': data['activo']
            }
            
            if user['rol'] == 'medico':
                update_data['especialidad'] = data['especialidad'] or "General"
                update_data['firmaBase64'] = data['firma_base64'] or ""
            
            # Actualizar Firestore
            update_firestore_user(rut, update_data, user['rol'])
            
            # Actualizar estado en Auth
            auth_user = get_user_by_email(user['correo'])
            if data['activo']:
                enable_user(auth_user.uid)
            else:
                disable_user(auth_user.uid)
                
            return redirect('list_users')
    else:
        initial_data = {
            'nombre': user.get('nombre', ''),
            'apellido_paterno': user.get('apellidoPaterno', ''),
            'apellido_materno': user.get('apellidoMaterno', ''),
            'activo': user.get('activo', True)
        }
        
        if user['rol'] == 'medico':
            initial_data['especialidad'] = user.get('especialidad', '')
            initial_data['firma_base64'] = user.get('firmaBase64', '')
        
        form = UserEditForm(initial=initial_data)
    
    return render(request, 'admin/edit_user.html', {'form': form, 'user': user})

@login_required
def toggle_user_status(request, rut, action):
    user = get_firestore_user(rut)
    if user:
        auth_user = get_user_by_email(user['correo'])
        if action == 'disable':
            disable_user(auth_user.uid)
            update_firestore_user(rut, {'activo': False}, user['rol'])
        elif action == 'enable':
            enable_user(auth_user.uid)
            update_firestore_user(rut, {'activo': True}, user['rol'])
    
    return redirect('list_users')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        # Verificar si el usuario existe y es administrador
        if user is not None:
            if user.is_admin:  # Verificar el campo is_admin
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'admin/login.html', {
                    'error': 'No tienes permisos de administrador'
                })
        else:
            return render(request, 'admin/login.html', {
                'error': 'Credenciales inválidas'
            })
    
    return render(request, 'admin/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')