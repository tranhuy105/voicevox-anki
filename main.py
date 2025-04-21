import asyncio
import argparse
from modules.logger import setup_logger
from modules.audio_processor import AudioProcessor
from modules.gui import VoiceVoxAnkiGUI

def main():
    parser = argparse.ArgumentParser(description="Generate audio for Anki cards using VOICEVOX.")
    parser.add_argument("--deck", help="Name of the Anki deck to process")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")
    parser.add_argument("--dry-run", action="store_true", help="Simulate processing without updating notes")
    parser.add_argument("--limit", type=int, help="Limit number of notes to process")
    parser.add_argument("--list-speakers", action="store_true", help="List available VOICEVOX speakers and styles")
    parser.add_argument("--style-id", type=int, help="Override default style ID for VOICEVOX")
    args = parser.parse_args()

    logger = setup_logger()
    processor = AudioProcessor(logger, dry_run=args.dry_run, limit=args.limit, style_id=args.style_id)

    if args.list_speakers:
        speakers = asyncio.run(processor.voicevox.list_speakers())
        for speaker_name, styles in speakers:
            print(f"Speaker: {speaker_name}")
            for style_name, style_id in styles:
                print(f"  Style: {style_name} (ID: {style_id})")
        return

    if not args.deck and not args.gui:
        logger.error("Must specify --deck or --gui")
        return

    if not processor.check_connections():
        logger.error("Cannot start: VOICEVOX or AnkiConnect not running.")
        return

    asyncio.run(processor.initialize())

    if args.gui:
        gui = VoiceVoxAnkiGUI(processor)
        gui.start()
    else:
        asyncio.run(processor.batch_process_deck(args.deck))

if __name__ == "__main__":
    main()