# VoiceVox Anki

A Python tool to generate audio for Anki cards using [VOICEVOX](https://voicevox.hiroshiba.jp/). Perfect for language learning (e.g., Japanese), it adds `.mp3` audio to Anki decks with a user-friendly GUI or command-line interface.

<div align="center">
  <img src="https://github.com/user-attachments/assets/25f7b052-2dc0-4f4b-ab8f-df6211723fab" alt="四国めたん"/>
  <p><em>Image: 四国めたん © Hiroshiba/VOICEVOX</em></p>
</div>

## Features

- Generates `.mp3` audio for card fields (e.g., `Sentence`, `Term`) using VOICEVOX (default: 四国めたん あまあま, style ID `0`).
- GUI with deck selection, customizable field names, dry run, and color-coded logs (DEBUG, INFO, ERROR).
- CLI for advanced users with similar functionality.
- Stores temporary `.wav` files in the project directory, automatically cleaned up.
- Saves compact `.mp3` files to Anki's media folder for efficient storage.

## Requirements

- Python 3.8+
- [VOICEVOX](https://voicevox.hiroshiba.jp/) running locally (`http://127.0.0.1:50021`)
- [Anki](https://apps.ankiweb.net/) with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) enabled
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to PATH (for `.mp3` conversion)
- Dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tranhuy105/voicevox-anki.git
   cd voicevox-anki
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure VOICEVOX, Anki (with AnkiConnect), and FFmpeg are running/installed.

## Usage

### GUI (Recommended)

Launch the GUI:

```bash
python main.py --gui
```


<div align="center">
  <img src="https://github.com/user-attachments/assets/13b4b563-bbb6-44db-b9be-62c700a82a47" alt="VoiceVox Anki GUI" width="600" />
</div>



- Select deck (e.g., `ラノベル`).
- Customize field names (e.g., `Sentence`, `Sentence Audio`) if needed.
- Set limit or style ID (optional, default: あまあま ID `0`).
- Check "Dry Run" to simulate without changes.
- Click "Process Deck" and view logs in the "Log" tab.



### Command Line

Process a deck:

```bash
python main.py --deck "ラノベル" --limit 100 --dry-run
```

List VOICEVOX styles:

```bash
python main.py --list-speakers
```

## Notes

- Audio is saved as `.mp3` in Anki's media folder (e.g., `C:\Users\<User>\AppData\Roaming\Anki2\User 1\collection.media`).
- Temporary `.wav` files are deleted after conversion to `.mp3`.
- Backup your Anki deck before processing large batches.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [VOICEVOX](https://voicevox.hiroshiba.jp/) for text-to-speech.
- [Anki](https://apps.ankiweb.net/) and [AnkiConnect](https://ankiweb.net/shared/info/2055492159) for flashcard integration.
- [pydub](https://github.com/jiaaro/pydub) and [FFmpeg](https://ffmpeg.org/) for audio conversion.
