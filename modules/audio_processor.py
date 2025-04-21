import uuid
import asyncio
from typing import List, Dict, Optional
from .voicevox_client import VoiceVoxClient
from .anki_client import AnkiClient

class AudioProcessor:
    def __init__(self, logger, dry_run: bool = False, limit: Optional[int] = None, style_id: Optional[int] = None,
                 sentence_field: str = "Sentence", sentence_audio_field: str = "Sentence Audio",
                 term_field: str = "Term", term_audio_field: str = "Term Audio"):
        self.logger = logger
        self.voicevox = VoiceVoxClient(logger=logger, style_id=style_id)
        self.anki = AnkiClient(logger=logger)
        self.dry_run = dry_run
        self.limit = limit
        self.dry_run_updates = []
        self.sentence_field = sentence_field
        self.sentence_audio_field = sentence_audio_field
        self.term_field = term_field
        self.term_audio_field = term_audio_field

    async def initialize(self):
        await self.voicevox.initialize()

    def check_connections(self) -> bool:
        voicevox_ok = asyncio.run(self.voicevox.check_connection())
        anki_ok = self.anki.check_connection()
        if not voicevox_ok:
            self.logger.error("VOICEVOX server not running.")
        if not anki_ok:
            self.logger.error("AnkiConnect not running.")
        return voicevox_ok and anki_ok

    def clean_text(self, text: str) -> str:
        text = text.strip()
        if len(text) > 200:
            self.logger.warning(f"Text too long, truncating: {text[:50]}...")
            text = text[:200]
        return text

    async def process_note(self, note: Dict):
        note_id = note["noteId"]
        fields = note["fields"]
        sentence = fields.get(self.sentence_field, {}).get("value", "")
        sentence_audio = fields.get(self.sentence_audio_field, {}).get("value", "")
        term = fields.get(self.term_field, {}).get("value", "")
        term_audio = fields.get(self.term_audio_field, {}).get("value", "")

        updates = {}
        if sentence and not sentence_audio:
            sentence = self.clean_text(sentence)
            audio = await self.voicevox.generate_audio(sentence)
            if audio:
                filename = f"sentence_{note_id}_{uuid.uuid4()}"
                if not self.dry_run:
                    saved_filename = self.anki.store_audio(audio, filename)
                else:
                    saved_filename = f"{filename}.mp3 (dry-run)"
                if saved_filename:
                    updates[self.sentence_audio_field] = f"[sound:{saved_filename}]"

        if term and not term_audio:
            term = self.clean_text(term)
            audio = await self.voicevox.generate_audio(term)
            if audio:
                filename = f"term_{note_id}_{uuid.uuid4()}"
                if not self.dry_run:
                    saved_filename = self.anki.store_audio(audio, filename)
                else:
                    saved_filename = f"{filename}.mp3 (dry-run)"
                if saved_filename:
                    updates[self.term_audio_field] = f"[sound:{saved_filename}]"

        if updates:
            try:
                if not self.dry_run:
                    self.anki.invoke("updateNoteFields", note={"id": note_id, "fields": updates})
                self.logger.info(f"{'[DRY-RUN] ' if self.dry_run else ''}Updated note {note_id}: {updates}")
                self.dry_run_updates.append((note_id, updates))
            except Exception as e:
                self.logger.error(f"Failed to update note {note_id}: {e}")

    async def batch_process_deck(self, deck_name: str):
        notes = self.anki.get_deck_notes(deck_name)
        if self.limit:
            notes = notes[:self.limit]
        self.logger.info(f"Processing {len(notes)} notes in deck {deck_name}...")
        self.dry_run_updates = []
        for i, note in enumerate(notes, 1):
            await self.process_note(note)
            self.logger.debug(f"Processed note {i}/{len(notes)}")
        self.logger.info("Batch processing complete.")
        if self.dry_run and self.dry_run_updates:
            self.logger.info("Dry run summary:")
            for note_id, updates in self.dry_run_updates:
                self.logger.info(f"  Note {note_id}: {updates}")