import os
import whisper
import fitz
from docx import Document
import nltk
from nltk.tokenize import sent_tokenize

# Download once
nltk.download("punkt", quiet=True)
nltk.download('punkt_tab')

class WhisperTranscriber:
    def __init__(self, device="cuda"):
        # Use medium for speed + accuracy balance
        self.whisper_model = whisper.load_model("medium", device)

    # ---------------- COMMON ----------------
    def split_sentences(self, text):
        return [s.strip() for s in sent_tokenize(text) if s.strip()]

    # ---------------- AUDIO / VIDEO ----------------
    def extract_from_audio(self, file_path, window=1):
        result = self.whisper_model.transcribe(file_path)
        segments = result["segments"]

        records = []

        for idx, seg in enumerate(segments):
            start_idx = max(0, idx - window)
            end_idx = min(len(segments), idx + window + 1)

            context_text = " ".join(
                segments[i]["text"].strip() for i in range(start_idx, end_idx)
            )

            records.append({
                "embedding_text": seg["text"].strip(),
                "context_text": context_text,
                "start_time": round(segments[start_idx]["start"], 2),
                "end_time": round(segments[end_idx - 1]["end"], 2),
                "source_type": "audio",
                "source_name": os.path.basename(file_path),
                "segment_index": idx
            })

        return records

    # ---------------- PDF ----------------
    def extract_from_pdf(self, file_path):
        doc = fitz.open(file_path)
        records = []

        for page_no, page in enumerate(doc, start=1):
            blocks = page.get_text("blocks")

            for block_idx, block in enumerate(blocks):
                paragraph_text = block[4].strip()
                if not paragraph_text:
                    continue

                sentences = self.split_sentences(paragraph_text)
                paragraph_id = f"{os.path.basename(file_path)}_p{page_no}_{block_idx}"

                for sent_idx, sentence in enumerate(sentences):
                    records.append({
                        "embedding_text": sentence,
                        "paragraph_text": paragraph_text,
                        "source_type": "document",
                        "source_name": os.path.basename(file_path),
                        "page": page_no,
                        "paragraph_id": paragraph_id,
                        "sentence_index": sent_idx
                    })

        return records

    # ---------------- DOCX ----------------
    def extract_from_docx(self, file_path):
        doc = Document(file_path)
        records = []

        for para_idx, para in enumerate(doc.paragraphs):
            paragraph_text = para.text.strip()
            if not paragraph_text:
                continue

            sentences = self.split_sentences(paragraph_text)
            paragraph_id = f"{os.path.basename(file_path)}_para{para_idx}"

            for sent_idx, sentence in enumerate(sentences):
                records.append({
                    "embedding_text": sentence,
                    "paragraph_text": paragraph_text,
                    "source_type": "document",
                    "source_name": os.path.basename(file_path),
                    "paragraph_id": paragraph_id,
                    "sentence_index": sent_idx
                })

        return records

    # ---------------- TXT ----------------
    def extract_from_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            paragraphs = [p.strip() for p in f.read().split("\n\n") if p.strip()]

        records = []

        for para_idx, paragraph_text in enumerate(paragraphs):
            sentences = self.split_sentences(paragraph_text)
            paragraph_id = f"{os.path.basename(file_path)}_para{para_idx}"

            for sent_idx, sentence in enumerate(sentences):
                records.append({
                    "embedding_text": sentence,
                    "paragraph_text": paragraph_text,
                    "source_type": "text",
                    "source_name": os.path.basename(file_path),
                    "paragraph_id": paragraph_id,
                    "sentence_index": sent_idx
                })

        return records

    # ---------------- ROUTER ----------------
    def extract_text(self, file_path):
        ext = file_path.lower()

        if ext.endswith((".mp4", ".mkv", ".avi", ".mp3", ".wav")):
            return self.extract_from_audio(file_path)

        if ext.endswith(".pdf"):
            return self.extract_from_pdf(file_path)

        if ext.endswith(".docx"):
            return self.extract_from_docx(file_path)

        if ext.endswith(".txt"):
            return self.extract_from_txt(file_path)

        raise ValueError(f"Unsupported file type: {file_path}")

    # ---------------- INGEST ----------------
    def ingest(self, input_path):
        all_chunks = []

        if os.path.isfile(input_path):
            print(f"🔹 Processing file: {input_path}")
            all_chunks.extend(self.extract_text(input_path))

        elif os.path.isdir(input_path):
            print(f"📂 Processing folder: {input_path}")
            for root, _, files in os.walk(input_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        print(f"  ↳ {file}")
                        all_chunks.extend(self.extract_text(file_path))
                    except Exception as e:
                        print(f"❌ Skipped {file}: {e}")

        else:
            raise ValueError("Invalid file or directory path")

        return all_chunks


# ---------------- RUN ----------------
transcriber = WhisperTranscriber()
chunks = transcriber.ingest("src/pdf/")
print(len(chunks))
