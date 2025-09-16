import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2 import service_account
from django.conf import settings


# Usa las credenciales de tu settings.py
credentials = service_account.Credentials.from_service_account_info(settings.FIREBASE_CREDENTIALS)

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

# ID de propiedad GA4 (lo obtienes de https://analytics.google.com/ → Admin → ID de propiedad)
PROPERTY_ID = '494208471'  # <-- Reemplaza con tu ID real (ej: '402764566')

client = BetaAnalyticsDataClient(credentials=credentials)


def obtener_metrica(nombre_metrica, fecha_inicio="7daysAgo", fecha_fin="today"):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[],
        metrics=[Metric(name=nombre_metrica)],
        date_ranges=[DateRange(start_date=fecha_inicio, end_date=fecha_fin)],
    )
    response = client.run_report(request)
    return response.rows[0].metric_values[0].value if response.rows else "0"



def obtener_metricas_clave(fecha_inicio="7daysAgo", fecha_fin="today"):
    return {
        "active_users": obtener_metrica("activeUsers", fecha_inicio, fecha_fin),
        "new_users": obtener_metrica("newUsers", fecha_inicio, fecha_fin),
        "sessions": obtener_metrica("sessions", fecha_inicio, fecha_fin),
        "engagement_time": obtener_metrica("userEngagementDuration", fecha_inicio, fecha_fin),
    }
