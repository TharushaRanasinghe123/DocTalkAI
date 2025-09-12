# app/services/transcript_buffer.py
import time


class TranscriptBuffer:
    def __init__(self):
        self.buffer = ""
        self.last_activity_time = time.time()
        self.silence_threshold = 3.0  # seconds of silence before processing
        self.processed_sentences = set()  # Track processed sentences to avoid duplicates
    
    def add_transcript(self, transcript, is_final=False):
        """Add transcript to buffer and return complete sentence if ready"""
        if not transcript.strip():
            return None
            
        # Update activity time
        self.last_activity_time = time.time()
        
        # Add to buffer
        if self.buffer:
            self.buffer += " " + transcript.strip()
        else:
            self.buffer = transcript.strip()
        
        print(f"📝 Buffer updated: '{self.buffer}' (is_final: {is_final})")
        
        # Check if we should process this sentence
        if self._should_process_sentence(is_final):
            sentence = self.buffer.strip()
            # Avoid processing the same sentence multiple times
            if sentence not in self.processed_sentences and len(sentence) > 10:
                self.processed_sentences.add(sentence)
                self.buffer = ""  # Clear buffer after processing
                return sentence
        
        return None
    
    def _should_process_sentence(self, is_final):
        """Improved logic to determine when to process a sentence"""
        if not self.buffer:
            return False
            
        buffer_words = self.buffer.split()
        buffer_length = len(self.buffer)
        
        # Strong indicators of a complete sentence
        if self.buffer.strip().endswith(('.', '?', '!', '。', '？', '！')):
            return is_final and len(buffer_words) >= 2
        
        # For sentences without punctuation, be more conservative
        if is_final:
            # Check for incomplete patterns
            incomplete_endings = ['my', 'the', 'a', 'an', 'to', 'for', 'with', 'and', 'or', 'i', 'want', 'need','is','id is','because']
            last_word = self.buffer.strip().lower().split()[-1] if buffer_words else ""
            
            # More conservative: require longer sentences and avoid obvious incomplete endings
            if (len(buffer_words) >= 3 and 
                buffer_length >= 15 and 
                last_word not in incomplete_endings):
                return True
        
        return False
    
    def get_final_buffer(self):
        """Get any remaining content when connection closes"""
        if self.buffer and len(self.buffer.split()) >= 3:
            sentence = self.buffer.strip()
            if sentence not in self.processed_sentences:
                self.processed_sentences.add(sentence)
                self.buffer = ""
                return sentence
        return None