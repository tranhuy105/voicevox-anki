import requests
import os
import uuid
from pydub import AudioSegment

class AnkiClient:
    def __init__(self, logger, url: str = "http://127.0.0.1:8765"):
        self.url = url
        self.logger = logger
        self.project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    def invoke(self, action: str, **params):
        request = {"action": action, "version": 6, "params": params}
        try:
            response = requests.post(self.url, json=request).json()
            if response.get("error"):
                self.logger.error(f"AnkiConnect error: {response['error']}")
                raise Exception(response["error"])
            return response.get("result")
        except Exception as e:
            self.logger.error(f"AnkiConnect request failed: {e}")
            raise

    def check_connection(self) -> bool:
        try:
            self.invoke("version")
            self.logger.debug("AnkiConnect connection successful")
            return True
        except Exception:
            self.logger.error("AnkiConnect not running")
            return False

    def get_deck_notes(self, deck_name: str) -> list:
        try:
            # First get all notes in the deck
            query = f'deck:"{deck_name}"'
            note_ids = self.invoke("findNotes", query=query)
            if not note_ids:
                self.logger.warning(f"No notes found in deck {deck_name}")
                return []
            
            # Get detailed info for all notes
            notes = self.invoke("notesInfo", notes=note_ids)
            
            # Filter notes that have empty audio fields
            filtered_notes = []
            for note in notes:
                fields = note["fields"]
                sentence_audio = fields.get("Sentence Audio", {}).get("value", "")
                term_audio = fields.get("Term Audio", {}).get("value", "")
                
                # Only include notes that have either sentence or term field but missing corresponding audio
                sentence = fields.get("Sentence", {}).get("value", "")
                term = fields.get("Term", {}).get("value", "")
                
                if (sentence and not sentence_audio) or (term and not term_audio):
                    filtered_notes.append(note)
            
            self.logger.debug(f"Found {len(filtered_notes)} notes with missing audio in deck {deck_name}")
            return filtered_notes
        except Exception as e:
            self.logger.error(f"Failed to retrieve notes from deck {deck_name}: {e}")
            return []

    def store_audio(self, audio_data: bytes, filename: str) -> str:
        try:
            # Save temp WAV file in project directory
            temp_wav_filename = f"temp_{uuid.uuid4()}.wav"
            temp_wav_path = os.path.join(self.project_dir, temp_wav_filename)
            self.logger.debug(f"Writing audio to temp WAV file: {temp_wav_path}")

            # Write audio data to temp WAV file
            with open(temp_wav_path, "wb") as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()

            # Verify temp WAV file exists
            if not os.path.exists(temp_wav_path):
                self.logger.error(f"Temp WAV file not created: {temp_wav_path}")
                raise FileNotFoundError(f"Temp WAV file not created: {temp_wav_path}")

            # Convert WAV to MP3
            temp_mp3_filename = f"temp_{uuid.uuid4()}.mp3"
            temp_mp3_path = os.path.join(self.project_dir, temp_mp3_filename)
            self.logger.debug(f"Converting WAV to MP3: {temp_mp3_path}")
            
            audio = AudioSegment.from_wav(temp_wav_path)
            audio.export(temp_mp3_path, format="mp3", bitrate="64k")

            # Store in Anki media
            final_filename = f"{filename}.mp3"
            self.logger.debug(f"Storing audio in Anki: {final_filename}")
            self.invoke("storeMediaFile", filename=final_filename, path=temp_mp3_path)

            # Clean up temp files
            try:
                os.remove(temp_wav_path)
                os.remove(temp_mp3_path)
                self.logger.debug(f"Deleted temp files: {temp_wav_path}, {temp_mp3_path}")
            except Exception as e:
                self.logger.warning(f"Failed to delete temp files: {e}")

            self.logger.info(f"Stored audio: {final_filename}")
            return final_filename
        except Exception as e:
            self.logger.error(f"Failed to store audio {filename}: {e}")
            raise