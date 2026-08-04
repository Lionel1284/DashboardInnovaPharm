# ⚙️ InnovaPharm - Dashboard Administrativo

> **Panel de administración centralizado y API backend desarrollado en Django para la gestión de usuarios, roles, métricas y seguridad de la plataforma InnovaPharm (Consultorio Raúl Brañes Farmer).**

---

## 📌 Tabla de Contenidos
- [Acerca del Componente](#-acerca-del-componente)
- [Funcionalidades del Dashboard](#-funcionalidades-del-dashboard)
- [Stack Tecnológico](#-stack-tecnológico)
- [Requisitos de Seguridad](#-requisitos-de-seguridad)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Relación con el Ecosistema InnovaPharm](#-relación-con-el-ecosistema-innovapharm)

---

## 📖 Acerca del Componente

Este módulo constituye la columna vertebral administrativa del ecosistema **InnovaPharm**. Proporciona a los administradores del Consultorio Raúl Brañes Farmer un panel web intuitivo y seguro para controlar el acceso a la plataforma, gestionar las cuentas de los distintos perfiles de usuario (médicos, farmacéuticos y pacientes) y monitorear el desempeño global del sistema.

---

## ✨ Funcionalidades del Dashboard

* **👤 Gestión de Usuarios y Perfiles (RBAC):**
  * Creación, edición y administración de roles.
  * Listado global de usuarios registrados en el sistema.
  * Generación automática de contraseñas y credenciales seguras.

* **📊 Métricas y Rendimiento:**
  * Visualización de indicadores clave (recetas emitidas, validadas, activas).
  * Panel con métricas de rendimiento y uso de la plataforma.

* **🔐 Seguridad y Control de Acceso:**
  * Cierre automático de sesión por inactividad.
  * Sistema de bloqueo tras múltiples intentos fallidos de autenticación.
  * Gestión de permisos granulares por perfil para garantizar la confidencialidad médica.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python (v3.10+)
* **Framework Backend:** Django
* **Base de Datos:** SQLite (Entorno de desarrollo) / PostgreSQL (Producción)
* **Entorno Virtual:** Virtualenv (`env`)
* **Integración:** Firebase Authentication / RUT-RUN Validation

---

## 🛡️ Requisitos de Seguridad e ISO/IEC 25010

Este dashboard implementa directrices de la norma **ISO/IEC 25010**, destacando:

* **Seguridad (RNF.2 / RNF.7):** Manejo seguro de credenciales, cifrado de datos sensibles y mecanismos contra accesos no autorizados.
* **Escalabilidad y Tolerancia a Errores (RNF.2 / RNF.3 / RNF.4):** Diseño modular en Django capaz de soportar el incremento de usuarios sin degradar la respuesta.
* **Consistencia e Interfaz (RNF.1 / RNF.4):** Mensajes claros de bienvenida, validación visual en formularios e interfaz uniforme.

---

## 📁 Estructura del Repositorio

```text
DashboardInnovaPharm/
├── env/                    # Entorno virtual de Python
├── proyecto_django/        # Proyecto principal de Django
│   ├── manage.py           # Script de gestión de Django
│   ├── proyecto_django/    # Configuración principal (settings, urls, wsgi)
│   └── ...                 # Aplicaciones y módulos del panel
└── README.md
