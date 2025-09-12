# # backend/app/config/intent_requirements.py
# from app.models.intent_model import IntentType

# # Define required entities for each intent
# INTENT_REQUIREMENTS = {
#     IntentType.BOOK_APPOINTMENT: ["patient_name", "doctor_name", "date", "time"],
#     IntentType.RESCHEDULE_APPOINTMENT: ["patient_name", "date", "new_date", "new_time"],
#     IntentType.CANCEL_APPOINTMENT: ["patient_name", "date"],  # OR appointment_id
#     IntentType.QUERY_AVAILABILITY: ["doctor_name", "date"],
# }

# # Alternative entities that can satisfy requirements
# ENTITY_ALTERNATIVES = {
#     "date": ["appointment_id"],  # For cancellation, either date or appointment_id works
#     "appointment_id": ["date"],
# }