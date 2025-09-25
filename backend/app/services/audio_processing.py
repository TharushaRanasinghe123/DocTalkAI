# app/services/audio_processing.py
import json
import asyncio
from fastapi import WebSocket
from .transcript_buffer import TranscriptBuffer
from .websocket_utils import safe_send_json
from app.models.intent_model import IntentType
import difflib

try:
    from app.services.elevenlabs_service import elevenlabs_service
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    from app.services.openai_service import openai_service
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from app.services.mongodb_service import mongodb_service
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️ MongoDB service not available")

# Global variable to track speaking state
is_ai_speaking = False

def convert_spoken_numbers_to_digits(text):
    """Convert spoken numbers like 'one two three' to digits '123'"""
    number_words = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13', 
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
        'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
        'eighty': '80', 'ninety': '90'
    }
    
    # Split text into words
    words = text.split()
    result = []
    i = 0
    
    while i < len(words):
        word = words[i].lower()
        
        # Check if current word is a number word
        if word in number_words:
            # Check if next words are also number words (for multi-digit numbers)
            number_sequence = [number_words[word]]
            j = i + 1
            
            while j < len(words) and words[j].lower() in number_words:
                number_sequence.append(number_words[words[j].lower()])
                j += 1
            
            # If we have a sequence of single digits, combine them
            if all(len(num) == 1 for num in number_sequence):
                result.append(''.join(number_sequence))
            else:
                # For larger numbers, keep them separate
                result.extend(number_sequence)
            
            i = j  # Skip the processed words
        else:
            result.append(words[i])
            i += 1
    
    return ' '.join(result)

async def _verify_doctor_exists_enhanced(doctor_name: str) -> dict:
    """Enhanced doctor verification with fuzzy matching for speech recognition errors"""
    try:
        doctors = await mongodb_service.get_available_doctors()
        mentioned_lower = doctor_name.lower().replace('dr.', '').replace('doctor', '').strip()
        
        exact_matches = []
        fuzzy_matches = []
        
        for doctor in doctors:
            doc_name_lower = doctor["name"].lower()
            
            # 1. Exact match
            if mentioned_lower == doc_name_lower:
                return {
                    "status": "found",
                    "matched_name": doctor["name"],
                    "confidence": "exact"
                }
            
            # 2. Remove spaces and compare (handles "Johndoe" vs "John Doe")
            mentioned_no_spaces = mentioned_lower.replace(' ', '')
            doc_name_no_spaces = doc_name_lower.replace(' ', '')
            
            if mentioned_no_spaces == doc_name_no_spaces:
                return {
                    "status": "found", 
                    "matched_name": doctor["name"],
                    "confidence": "spacing_fixed"
                }
            
            # 3. Fuzzy matching for similar names
            similarity = difflib.SequenceMatcher(None, mentioned_lower, doc_name_lower).ratio()
            if similarity > 0.7:  # 70% similarity threshold
                fuzzy_matches.append((doctor["name"], similarity))
            
            # 4. Check if mentioned name is part of doctor name or vice versa
            if mentioned_lower in doc_name_lower or doc_name_lower in mentioned_lower:
                fuzzy_matches.append((doctor["name"], 0.8))  # High confidence for partial matches
        
        # Handle fuzzy matches
        if fuzzy_matches:
            # Sort by similarity score (highest first)
            fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
            best_match = fuzzy_matches[0]
            
            if best_match[1] > 0.8:  # High confidence
                return {
                    "status": "found",
                    "matched_name": best_match[0],
                    "confidence": "fuzzy_high"
                }
            else:  # Medium confidence - ask for confirmation
                return {
                    "status": "multiple_matches",
                    "matches": [match[0] for match in fuzzy_matches[:3]],
                    "matched_name": best_match[0],
                    "confidence": "fuzzy_medium"
                }
        
        return {"status": "not_found"}
            
    except Exception as e:
        print(f"❌ Doctor verification error: {e}")
        return {"status": "error"}

def proper_capitalization(text):
    """Convert text to proper capitalization with name and proper noun support"""
    if not text:
        return text
    
    # First, capitalize the first letter of the entire text
    text = text[0].upper() + text[1:]
    
    # Capitalize names and proper nouns (words after specific patterns)
    words = text.split()
    
    # Patterns that typically precede names/proper nouns
    name_indicators = ['my name is', 'i am', 'call me', 'this is', 'it is', 'name is', 
                      'doctor', 'dr.', 'mr.', 'mrs.', 'ms.', 'miss', 'professor', 'prof.']
    
    for i in range(len(words) - 1):
        current_phrase = ' '.join(words[i:i+2]).lower()
        current_word = words[i].lower()
        
        # If we detect a name indicator, capitalize the next word
        if current_phrase in name_indicators or current_word in name_indicators:
            if i + 2 < len(words):
                words[i + 2] = words[i + 2].capitalize()
            elif i + 1 < len(words):
                words[i + 1] = words[i + 1].capitalize()
        
        # Capitalize words after apostrophes (like O'Brian)
        if "'" in words[i] and i + 1 < len(words):
            words[i + 1] = words[i + 1].capitalize()
    
    # Capitalize after periods, question marks, and exclamation points
    for punctuation in ['.', '?', '!']:
        parts = ' '.join(words).split(punctuation + ' ')
        text = (punctuation + ' ').join([part.capitalize() for part in parts])
        words = text.split()  # Update words after punctuation processing
    
    # Capitalize 'I' and common proper nouns
    text = ' '.join(words)
    text = text.replace(' i ', ' I ')
    text = text.replace(" i'", " I'")
    
    # Capitalize common titles and names
    text = text.replace('dr. ', 'Dr. ')
    text = text.replace('mr. ', 'Mr. ')
    text = text.replace('mrs. ', 'Mrs. ')
    text = text.replace('ms. ', 'Ms. ')
    
    return text

async def delayed_processing(client_ws, sentence):
    """Wait before processing to ensure user finished speaking"""
    # Wait 1.5 seconds before processing
    await asyncio.sleep(2)
    
    # Check if client is still connected
    if client_ws.client_state.name == 'CONNECTED':
        await process_complete_sentence(client_ws, sentence)
    else:
        print("⚠️ Client disconnected during delay, skipping processing")


def process_transcript_text(text):
    """Apply all text processing: capitalization + number conversion"""
    if not text:
        return text
    
    # First convert spoken numbers to digits
    text_with_numbers = convert_spoken_numbers_to_digits(text)
    
    # Then apply proper capitalization
    return proper_capitalization(text_with_numbers)


async def receive_audio(client_ws: WebSocket, deepgram_ws):
    """Receive audio from client and forward to Deepgram"""
    try:
        print("🎤 Waiting for audio data from client...")
        async for message in client_ws.iter_bytes():
            try:
                print(f"📦 Received {len(message)} bytes from client")
                # Forward audio data to Deepgram
                await deepgram_ws.send(message)
                print(f"📤 Forwarded {len(message)} bytes to Deepgram")
            except Exception as e:
                print(f"Error forwarding audio: {e}")
                break
    except Exception as e:
        print(f"Error receiving audio: {e}")


async def process_complete_sentence(client_ws, transcript):
    """Process a complete sentence with OpenAI and convert response to speech"""
    global is_ai_speaking
    
    try:
        # Check if WebSocket is still connected before processing
        if client_ws.client_state.name != 'CONNECTED':
            print(f"⚠️ WebSocket not connected, skipping processing for: {transcript}")
            return
            
        print(f"🔄 Processing complete sentence: {transcript}")
        
        # Get session ID for conversation tracking
        session_id = str(id(client_ws))
        
        # 🎯 SIMPLIFIED: Just call OpenAI - it handles conversation logic now!
        intent_response = await openai_service.analyze_intent(transcript, session_id)
        
        print(f"✅ Intent: {intent_response.intent}")
        print(f"📋 Entities: {intent_response.entities}")
        print(f"🎯 Confidence: {intent_response.confidence}")
        print(f"💬 Response: {intent_response.processed_response}")

        # 🗄️ DATABASE OPERATIONS - Save to MongoDB when appropriate
        if MONGODB_AVAILABLE and intent_response.entities:
            try:
                # Handle different intents with database operations
                # In process_complete_sentence function, replace the BOOK_APPOINTMENT section:

                if intent_response.intent == IntentType.BOOK_APPOINTMENT:
                    # === ENHANCED DOCTOR VALIDATION ===
                    doctor_name = intent_response.entities.get("doctor_name")
                    
                    if doctor_name:
                        # Verify doctor exists with fuzzy matching
                        verification_result = await _verify_doctor_exists_enhanced(doctor_name)
                        
                        if verification_result["status"] == "not_found":
                            # Doctor not found
                            available_doctors = await mongodb_service.get_available_doctors()
                            alternatives = ", ".join([f"Dr. {doc['name']}" for doc in available_doctors[:3]])
                            intent_response.processed_response = f"I don't see Dr. {doctor_name} in our system. We have {alternatives}. Who would you prefer?"
                            
                        elif verification_result["status"] == "multiple_matches":
                            # Multiple fuzzy matches found
                            matches = ", ".join([f"Dr. {match}" for match in verification_result["matches"][:2]])
                            intent_response.processed_response = f"Did you mean {matches}? Please confirm which doctor you'd like to see."
                            
                        elif verification_result["status"] == "found":
                            # Doctor found - use corrected name and proceed with booking
                            corrected_name = verification_result["matched_name"]
                            intent_response.entities["doctor_name"] = corrected_name
                            
                            # Check if we have all required data
                            required_fields = ["patient_name", "doctor_name", "date", "time"]
                            if all(intent_response.entities.get(field) for field in required_fields):
                                appointment_data = {
                                    # Use the correct field names that match Postman bookings
                                    "patientName": intent_response.entities["patient_name"],
                                    "doctorName": intent_response.entities["doctor_name"],  # ← FIXED: doctorName instead of doctor_name
                                    "date": intent_response.entities["date"],
                                    "time": intent_response.entities["time"],
                                    "reason": intent_response.entities.get("reason", ""),
                                    # Include both for compatibility if needed
                                    "patient_name": intent_response.entities["patient_name"],
                                    "doctor_name": intent_response.entities["doctor_name"]
                                }
    
                                
                                # BOOK THE APPOINTMENT
                                appointment_id = await mongodb_service.insert_appointment(appointment_data)
                                
                                if appointment_id:
                                    print(f"✅ Appointment booked in database! ID: {appointment_id}")
                                    intent_response.processed_response = f"Thank you, {appointment_data['patientName']}! I have booked your appointment with Dr. {appointment_data['doctorName']} on {appointment_data['date']} at {appointment_data['time']}. Your appointment ID is {appointment_id}."
                                else:
                                    print("❌ Failed to save appointment to database")
                                    intent_response.processed_response = "Sorry, I encountered an error while booking your appointment."
                            else:
                                # Missing required fields - let OpenAI handle asking for missing info
                                print("⚠️ Missing required fields for booking")
                                # The processed_response from OpenAI will naturally ask for missing information
                                
                    else:
                        # No doctor specified
                        available_doctors = await mongodb_service.get_available_doctors()
                        doctors_list = ", ".join([f"Dr. {doc['name']}" for doc in available_doctors[:3]])
                        intent_response.processed_response = f"I'd be happy to book your appointment! We have {doctors_list}. Which doctor would you like to see?"
                elif intent_response.intent == IntentType.CANCEL_APPOINTMENT:
                    # Cancel appointment by ID or patient info
                    if intent_response.entities.get("appointment_id"):
                        success = await mongodb_service.cancel_appointment(
                            intent_response.entities["appointment_id"]
                        )
                        if success:
                            print(f"✅ Appointment {intent_response.entities['appointment_id']} cancelled in database!")
                            intent_response.processed_response = f"✅ I've successfully cancelled your appointment {intent_response.entities['appointment_id']}."
                        else:
                            print("❌ Failed to cancel appointment")
                            intent_response.processed_response = "❌ Sorry, I couldn't find that appointment ID. Please check and try again."
                    # METHOD 2: Cancel by patient details
                    elif intent_response.entities.get("patient_name") and intent_response.entities.get("date"):
                        success = await mongodb_service.cancel_appointment_by_details(
                            intent_response.entities["patient_name"],
                            intent_response.entities["date"],
                            intent_response.entities.get("time")
                        )
                        if success:
                            print(f"✅ Appointment for {intent_response.entities['patient_name']} on {intent_response.entities['date']} cancelled!")
                            # Update AI response to confirm cancellation
                            intent_response.processed_response = f"✅ I've successfully cancelled your appointment on {intent_response.entities['date']}."
                        else:
                            print("❌ Failed to cancel appointment by details")
                            intent_response.processed_response = "❌ Sorry, I couldn't find a matching appointment. Please check the details and try again."
                    
                    else:
                        print("⚠️ Insufficient information for cancellation")
                    
                elif intent_response.intent == IntentType.RESCHEDULE_APPOINTMENT:
                    # Reschedule appointment with status validation
                    if intent_response.entities.get("appointment_id") and intent_response.entities.get("date"):

                        appointment_id = intent_response.entities["appointment_id"]
                        new_date = intent_response.entities["date"]
                        new_time = intent_response.entities.get("time")

                        print(f"🔄 Attempting to reschedule appointment {appointment_id} to {new_date} {new_time or ''}")

                        # FIRST CHECK APPOINTMENT STATUS
                        status = await mongodb_service.get_appointment_status(appointment_id)
                        
                        if status is None:
                            print(f"❌ Appointment not found: {appointment_id}")
                            intent_response.processed_response = f"❌ I couldn't find appointment {appointment_id}. Please check your appointment ID and try again."
                            
                        elif status == "cancelled":
                            print(f"❌ Cannot reschedule cancelled appointment: {appointment_id}")
                            intent_response.processed_response = f"❌ Appointment {appointment_id} has been cancelled. You cannot reschedule a cancelled appointment. Please book a new appointment instead."
                            
                        elif status == "booked":
                            # Proceed with rescheduling since appointment is booked
                            success = await mongodb_service.reschedule_appointment(
                                appointment_id, new_date, new_time
                            )
                            
                            if success:
                                print(f"✅ Appointment {appointment_id} rescheduled in database!")
                                time_info = f" at {new_time}" if new_time else ""
                                intent_response.processed_response = f"✅ I've successfully rescheduled your appointment to {new_date}{time_info}. Your appointment ID remains {appointment_id}."
                            else:
                                print("❌ Failed to reschedule appointment in database")
                                intent_response.processed_response = "❌ Sorry, I couldn't reschedule that appointment. Please try again."
                                
                        else:
                            print(f"❌ Unknown appointment status: {status}")
                            intent_response.processed_response = "❌ Sorry, I encountered an issue with your appointment status. Please contact support."
                            
                    else:
                        print("⚠️ Insufficient information for rescheduling")
        
                elif intent_response.intent == IntentType.QUERY_APPOINTMENT:
                    # Handle appointment queries
                    try:
                        appointment_id = intent_response.entities.get("appointment_id")
                        patient_name = intent_response.entities.get("patient_name")
                        
                        if appointment_id:
                            # Query by appointment ID
                            appointment = await mongodb_service.get_appointment_by_id(appointment_id)
                            
                            if appointment:
                                print(f"✅ Found appointment: {appointment_id}")
                                # Format a nice response with appointment details
                                intent_response.processed_response = (
                                    f"Your appointment with Dr. {appointment['doctor_name']} is scheduled for "
                                    f"{appointment['date']} at {appointment['time']}. "
                                    f"Reason: {appointment.get('reason', 'Not specified')}. "
                                    f"Status: {appointment['status']}."
                                )
                            else:
                                print(f"❌ Appointment not found: {appointment_id}")
                                intent_response.processed_response = f"❌ I couldn't find appointment {appointment_id}. Please check your appointment ID and try again."
                                
                        elif patient_name:
                            # Query by patient name (you can implement this later)
                            intent_response.processed_response = f"I found your name, but I need your appointment ID to look up your appointment details. Could you please provide your appointment ID?"
                            
                        else:
                            # No appointment ID or patient name provided
                            intent_response.processed_response = "I'd be happy to help you with your appointment details! Could you please provide your appointment ID?"
                            
                    except Exception as db_error:
                        print(f"❌ Database query failed: {db_error}")
                        intent_response.processed_response = "Sorry, I encountered an error while looking up your appointment details."
        # Keep the original OpenAI response which should ask for missing info                        
            except Exception as db_error:
                print(f"❌ Database operation failed: {db_error}")
        
        # Send intent response to frontend
        success = await safe_send_json(client_ws, {
            "type": "intent",
            "transcript": process_transcript_text(transcript),
            "intent": intent_response.intent.value,  # Use .value for string representation
            "entities": intent_response.entities,
            "confidence": intent_response.confidence,
            "processed_response": intent_response.processed_response,
            "is_final": True
        })
        
        if not success:
            print("❌ Failed to send intent response - client disconnected")
            return

        # Try speech generation
        if (ELEVENLABS_AVAILABLE and 
            intent_response.processed_response and 
            not is_ai_speaking and
            client_ws.client_state.name == 'CONNECTED'):
            
            try:
                is_ai_speaking = True
                print(f"🎵 Generating speech: {intent_response.processed_response}")
                
                # Send speech start signal
                await safe_send_json(client_ws, {
                    "type": "speech_start",
                    "message": "AI is responding..."
                })

                audio = await elevenlabs_service.generate_speech(intent_response.processed_response)
                
                # Check connection before sending audio
                if client_ws.client_state.name == 'CONNECTED' and audio:
                    audio_bytes = b''.join([chunk for chunk in audio])
                    await client_ws.send_bytes(audio_bytes)
                    print(f"✅ Sent audio: {len(audio_bytes)} bytes")
                    
                    # Send speech end signal
                    await safe_send_json(client_ws, {
                        "type": "speech_end", 
                        "message": "AI finished speaking"
                    })
                else:
                    print("❌ Connection closed during audio generation")
                
            except Exception as speech_error:
                print(f"🔊 Speech generation failed: {speech_error}")
                await safe_send_json(client_ws, {
                    "type": "speech_error",
                    "message": "Text-to-speech unavailable, continuing with text only",
                    "error": str(speech_error)
                })
            finally:
                is_ai_speaking = False
        else:
            print("🔇 Speech generation skipped")
        
    except Exception as e:
        print(f"❌ Error in intent processing: {e}")
        # Fallback response
        await safe_send_json(client_ws, {
            "type": "transcript",
            "transcript": process_transcript_text(transcript),
            "is_final": True,
            "error": "Processing failed"
        })


async def send_transcripts(deepgram_ws, client_ws: WebSocket):
    """Receive transcripts from Deepgram, buffer sentences, and send complete ones to OpenAI"""
    transcript_buffer = TranscriptBuffer()
    
    try:
        print("🎧 Starting to listen for Deepgram responses...")
        async for message in deepgram_ws:
            try:
                # Check if client is still connected
                if client_ws.client_state.name != 'CONNECTED':
                    print("Client disconnected, stopping transcript processing")
                    break

                data = json.loads(message)
                
                # Extract transcript
                transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                is_final = data.get("is_final", False)
                
                if transcript:
                    # Check for complete sentence
                    complete_sentence = transcript_buffer.add_transcript(transcript, is_final)
                    
                    if complete_sentence:
                        print(f"🎯 Complete sentence detected: {complete_sentence}")
                        # Process in background
                        asyncio.create_task(delayed_processing(client_ws, complete_sentence))
                                            
                    # Send interim transcripts for real-time display
                    await safe_send_json(client_ws, {
                        "type": "transcript",
                        "transcript": process_transcript_text(transcript),
                        "is_final": is_final,
                        "is_interim": not is_final
                    })
                        
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {message}")
            except Exception as e:
                print(f"Error processing message: {e}")
                
        # Process any remaining text when connection closes
        final_sentence = transcript_buffer.get_final_buffer()
        if final_sentence and client_ws.client_state.name == 'CONNECTED':
            print(f"📚 Processing final buffer: {final_sentence}")
            processed_sentence = process_transcript_text(final_sentence)
            await process_complete_sentence(client_ws, processed_sentence)

    except Exception as e:
        print(f"Error in send_transcripts: {e}")