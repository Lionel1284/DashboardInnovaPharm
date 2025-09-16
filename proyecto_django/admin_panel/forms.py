import re
import firebase_admin
from firebase_admin import auth
from django import forms
from django.core.exceptions import ValidationError
from .firebase_utils import clean_rut

ROLES = (
    ('medico', 'Médico'),
    ('farmaceutico', 'Farmacéutico'),
    ('admin', 'Administrador')
)

def validate_rut(value):
    """Valida que el RUT tenga formato correcto y dígito verificador válido"""
    rut_clean = clean_rut(value)
    
    # Validar longitud mínima
    if len(rut_clean) < 8:
        raise ValidationError('El RUT debe tener al menos 8 dígitos')
    
    # Separar cuerpo y dígito verificador
    cuerpo = rut_clean[:-1]
    dv = rut_clean[-1].upper()
    
    # Calcular dígito verificador esperado
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2
    
    resto = suma % 11
    dv_esperado = str(11 - resto) if resto != 0 else '0'
    if dv_esperado == '10':
        dv_esperado = 'K'
    elif dv_esperado == '11':
        dv_esperado = '0'
    
    if dv != dv_esperado:
        raise ValidationError('El RUT no es válido (dígito verificador incorrecto)')

def validate_email_unique(value):
    """Valida que el correo no esté registrado en Firebase Auth"""
    try:
        auth.get_user_by_email(value)
        raise ValidationError('Este correo electrónico ya está registrado')
    except auth.UserNotFoundError:
        pass  # El correo está disponible
    except Exception as e:
        raise ValidationError('Error al verificar el correo. Intente nuevamente.')

class RUTWidget(forms.TextInput):
    """Widget personalizado para formatear RUT mientras se escribe"""
    class Media:
        js = ('admin/js/rut_formatter.js',)

class UserCreationForm(forms.Form):
    rol = forms.ChoiceField(choices=ROLES)
    rut = forms.CharField(
        max_length=20, 
        label="RUT",
        validators=[validate_rut],
        widget=RUTWidget(attrs={
            'placeholder': '12.345.678-9',
            'class': 'rut-input'
        })
    )
    nombre = forms.CharField(max_length=100)
    apellido_paterno = forms.CharField(max_length=100)
    apellido_materno = forms.CharField(max_length=100, required=False)
    correo = forms.EmailField(
        validators=[
            validate_email_unique,
            # Validación básica de formato
            lambda value: None if '@' in value else ValidationError('El correo electrónico debe contener un @')
        ],
        widget=forms.EmailInput(attrs={
            'placeholder': 'usuario@ejemplo.com'
        })
    )
    especialidad = forms.CharField(max_length=100, required=False, label="Especialidad (solo médicos)")
    firma_base64 = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        required=False,
        label="Firma Base64 (solo médicos)"
    )

    def clean_rut(self):
        """Formatea el RUT correctamente antes de guardar"""
        rut = self.cleaned_data['rut']
        return self.format_rut(rut)
    
    def format_rut(self, rut):
        """Formatea el RUT como XX.XXX.XXX-X"""
        rut_clean = clean_rut(rut)
        if len(rut_clean) < 2:
            return rut
        
        # Formatear con puntos y guión
        cuerpo = rut_clean[:-1]
        dv = rut_clean[-1].upper()
        
        # Invertir el cuerpo para agregar puntos cada 3 dígitos
        cuerpo_invertido = cuerpo[::-1]
        cuerpo_formateado = '.'.join([cuerpo_invertido[i:i+3] for i in range(0, len(cuerpo_invertido), 3)])
        cuerpo_formateado = cuerpo_formateado[::-1]
        
        return f"{cuerpo_formateado}-{dv}"

class UserEditForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellido_paterno = forms.CharField(max_length=100)
    apellido_materno = forms.CharField(max_length=100, required=False)
    especialidad = forms.CharField(max_length=100, required=False, label="Especialidad (solo médicos)")
    firma_base64 = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        required=False,
        label="Firma Base64 (solo médicos)"
    )
    activo = forms.BooleanField(required=False, label="Usuario activo")