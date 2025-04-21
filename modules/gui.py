import tkinter as tk
from tkinter import messagebox, ttk
import asyncio
import threading
from typing import Optional
from .audio_processor import AudioProcessor
import logging
import queue
import sys
from io import StringIO

class TextHandler(logging.Handler):
    def __init__(self, text_widget, notebook):
        super().__init__()
        self.text_widget = text_widget
        self.notebook = notebook
        self.queue = queue.Queue()
        self.text_widget.after(100, self.poll_queue)
        
        # Configure text widget tags for different log levels
        self.text_widget.tag_configure('DEBUG', foreground='#666666')  # Màu xám nhạt
        self.text_widget.tag_configure('INFO', foreground='#2E7D32')   # Màu xanh lá đậm
        self.text_widget.tag_configure('WARNING', foreground='#F57C00') # Màu cam nhạt
        self.text_widget.tag_configure('ERROR', foreground='#C62828')   # Màu đỏ đậm
        self.text_widget.tag_configure('CRITICAL', foreground='#C62828', underline=1)  # Màu đỏ đậm + gạch chân

    def emit(self, record):
        msg = self.format(record)
        self.queue.put((msg, record.levelname))

    def poll_queue(self):
        try:
            while True:
                msg, level = self.queue.get_nowait()
                self.text_widget.insert(tk.END, msg + '\n', level)
                self.text_widget.see(tk.END)
        except queue.Empty:
            pass
        self.text_widget.after(100, self.poll_queue)

class VoiceVoxAnkiGUI:
    def __init__(self, processor: AudioProcessor):
        self.processor = processor
        self.root = tk.Tk()
        self.root.title("VoiceVox Anki")
        self.root.geometry("600x500")
    
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_gui()

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = ttk.Label(self.tooltip, text=text, justify=tk.LEFT,
                            background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack()

        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Main tab
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Main")

        # Create frames for better organization
        deck_frame = ttk.LabelFrame(main_tab, text="Deck Settings", padding="5")
        deck_frame.pack(fill=tk.X, pady=5)

        fields_frame = ttk.LabelFrame(main_tab, text="Field Names", padding="5")
        fields_frame.pack(fill=tk.X, pady=5)

        options_frame = ttk.LabelFrame(main_tab, text="Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)

        # Deck name
        ttk.Label(deck_frame, text="Deck Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.deck_entry = ttk.Entry(deck_frame, width=40)
        self.deck_entry.insert(0, "ラノベル")
        self.deck_entry.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.create_tooltip(self.deck_entry, "Name of the Anki deck to process")

        # Field names
        # Sentence field
        ttk.Label(fields_frame, text="Sentence Field:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sentence_field_entry = ttk.Entry(fields_frame, width=40)
        self.sentence_field_entry.insert(0, "Sentence")
        self.sentence_field_entry.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.create_tooltip(self.sentence_field_entry, "Name of the field containing the sentence text")

        # Sentence Audio field
        ttk.Label(fields_frame, text="Sentence Audio Field:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sentence_audio_field_entry = ttk.Entry(fields_frame, width=40)
        self.sentence_audio_field_entry.insert(0, "Sentence Audio")
        self.sentence_audio_field_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.create_tooltip(self.sentence_audio_field_entry, "Name of the field where sentence audio will be stored")

        # Term field
        ttk.Label(fields_frame, text="Term Field:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.term_field_entry = ttk.Entry(fields_frame, width=40)
        self.term_field_entry.insert(0, "Term")
        self.term_field_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.create_tooltip(self.term_field_entry, "Name of the field containing the term text")

        # Term Audio field
        ttk.Label(fields_frame, text="Term Audio Field:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.term_audio_field_entry = ttk.Entry(fields_frame, width=40)
        self.term_audio_field_entry.insert(0, "Term Audio")
        self.term_audio_field_entry.grid(row=3, column=1, sticky=tk.W, pady=2)
        self.create_tooltip(self.term_audio_field_entry, "Name of the field where term audio will be stored")

        # Options
        # Limit
        ttk.Label(options_frame, text="Limit:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.limit_entry = ttk.Entry(options_frame, width=10)
        self.limit_entry.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.create_tooltip(self.limit_entry, "Maximum number of notes to process (optional)")

        # Style ID
        ttk.Label(options_frame, text="Style ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.style_entry = ttk.Entry(options_frame, width=10)
        self.style_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.create_tooltip(self.style_entry, "VOICEVOX style ID (optional, default: 0 - あまあま)")

        # Dry run
        self.dry_run_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Dry Run (no changes)", variable=self.dry_run_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.create_tooltip(options_frame, "Simulate processing without making changes to Anki")

        # Process button
        self.process_button = ttk.Button(main_tab, text="Process Deck", command=self.start_processing)
        self.process_button.pack(pady=10)

        # Status
        self.status_label = ttk.Label(main_tab, text="Ready")
        self.status_label.pack(pady=5)

        # Log tab
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Log")

        # Log text with scrollbar
        log_frame = ttk.Frame(log_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(log_frame, height=20, width=70, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Configure logging
        text_handler = TextHandler(self.log_text, self.notebook)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.processor.logger.addHandler(text_handler)

    def start_processing(self):
        self.process_button.config(state="disabled")
        self.status_label.config(text="Processing...")
        self.processor.logger.info("Starting...")
        
        # Switch to Log tab
        self.notebook.select(1)  # Select the Log tab (index 1)

        deck_name = self.deck_entry.get()
        limit = self.limit_entry.get()
        style_id = self.style_entry.get()
        dry_run = self.dry_run_var.get()
        
        # Get field names
        sentence_field = self.sentence_field_entry.get()
        sentence_audio_field = self.sentence_audio_field_entry.get()
        term_field = self.term_field_entry.get()
        term_audio_field = self.term_audio_field_entry.get()

        try:
            limit = int(limit) if limit.strip() else None
            style_id = int(style_id) if style_id.strip() else None
        except ValueError:
            messagebox.showerror("Error", "Limit and Style ID must be numbers")
            self.reset_ui()
            return

        # Run in thread to avoid blocking GUI
        threading.Thread(
            target=self.run_processing,
            args=(deck_name, limit, style_id, dry_run, sentence_field, sentence_audio_field, term_field, term_audio_field),
            daemon=True
        ).start()

    def run_processing(self, deck_name: str, limit: Optional[int], style_id: Optional[int], dry_run: bool,
                      sentence_field: str, sentence_audio_field: str, term_field: str, term_audio_field: str):
        try:
            # Create new processor with GUI settings
            processor = AudioProcessor(
                logger=self.processor.logger,
                dry_run=dry_run,
                limit=limit,
                style_id=style_id,
                sentence_field=sentence_field,
                sentence_audio_field=sentence_audio_field,
                term_field=term_field,
                term_audio_field=term_audio_field
            )

            if not processor.check_connections():
                self.processor.logger.error("Error: VOICEVOX or AnkiConnect not running")
                self.reset_ui()
                return

            asyncio.run(processor.initialize())
            asyncio.run(processor.batch_process_deck(deck_name))
            self.processor.logger.info("Processing complete")
            messagebox.showinfo("Success", "Deck processing complete")
        except Exception as e:
            self.processor.logger.error(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed: {str(e)}")
        finally:
            self.reset_ui()

    def reset_ui(self):
        self.process_button.config(state="normal")
        self.status_label.config(text="Ready")
        self.root.update()

    def start(self):
        self.root.mainloop()