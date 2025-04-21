import aiohttp
import asyncio
from voicevox import Client
from typing import Optional, List, Tuple

class VoiceVoxClient:
    def __init__(self, url: str = "http://127.0.0.1:50021", logger=None, style_id: Optional[int] = None):
        self.url = url
        self.style_id = style_id
        self.speaker_name = "四国めたん"
        self.style_name = "あまあま"
        self.logger = logger

    async def initialize(self):
        async with Client(self.url) as client:
            try:
                speakers = await client.fetch_speakers()
                speaker_info = [(s.name, [(st.name, st.id) for st in s.styles]) for s in speakers]

                found = False
                if self.style_id is not None:
                    # Check if provided style_id exists
                    for speaker in speakers:
                        for style in speaker.styles:
                            if style.id == self.style_id:
                                self.speaker_name = speaker.name
                                self.style_name = style.name
                                self.logger.info(f"Using style_id {self.style_id}: {self.speaker_name} ({self.style_name})")
                                found = True
                                break
                        if found:
                            break
                else:
                    # Find style by name
                    for speaker in speakers:
                        if speaker.name == self.speaker_name:
                            for style in speaker.styles:
                                if style.name == self.style_name:
                                    self.style_id = style.id
                                    self.logger.info(f"Found {self.speaker_name} ({self.style_name}) with style_id {self.style_id}")
                                    found = True
                                    break
                        if found:
                            break

                if not found:
                    raise ValueError(f"Style '{self.style_name}' (ID {self.style_id}) for {self.speaker_name} not found.")
            except Exception as e:
                self.logger.error(f"VOICEVOX initialization failed: {e}")
                raise

    async def generate_audio(self, text: str) -> Optional[bytes]:
        for attempt in range(3):
            async with Client(self.url) as client:
                try:
                    audio_query = await client.create_audio_query(text, speaker=self.style_id)
                    audio = await audio_query.synthesis(speaker=self.style_id)
                    if len(audio) > 0:
                        self.logger.debug(f"Generated audio for text: {text[:50]}...")
                        return audio
                    self.logger.warning(f"Empty audio for text: {text}")
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} failed for text '{text}': {e}")
                    await asyncio.sleep(1)
        self.logger.error(f"Failed to generate audio for text: {text}")
        return None

    async def check_connection(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url) as response:
                    self.logger.debug(f"VOICEVOX connection check: status {response.status}")
                    return response.status == 200
            except Exception as e:
                self.logger.error(f"VOICEVOX connection check failed: {e}")
                return False

    async def list_speakers(self) -> List[Tuple[str, List[Tuple[str, int]]]]:
        async with Client(self.url) as client:
            try:
                speakers = await client.fetch_speakers()
                return [(s.name, [(st.name, st.id) for st in s.styles]) for s in speakers]
            except Exception as e:
                self.logger.error(f"Failed to list speakers: {e}")
                return []