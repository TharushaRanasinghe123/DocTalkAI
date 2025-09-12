try:
    from app.services.conversation_service import conversation_service
    print("✅ conversation_service imported successfully!")
    print("✅ Available methods:", [method for method in dir(conversation_service) if not method.startswith('_')])
except Exception as e:
    print(f"❌ Import failed: {e}")