from video_to_mp3 import name_list, format_converter
from chunking import WhisperTranscriber
from pathlib import Path
from vector_store import BGEVectorStore

VIDEO_DIR = Path("src/video")
AUDIO_DIR = Path("src/audio")

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
available_files = [f for f in VIDEO_DIR.iterdir() if f.is_file()]

db = BGEVectorStore(index_path="src/vector_db")

def video_to_mp3():
    file_map = name_list(available_files)
    format_converter(file_map, VIDEO_DIR, AUDIO_DIR, "mp3")

def text_chunking(path):
    transcriber = WhisperTranscriber()
    chunks = transcriber.ingest(path)
    print(chunks)
    return chunks

def text_to_Embeddings(chunks):
    vector_db = BGEVectorStore(model_name="bge-m3", dim=1024,index_path="src/vector_db")
    vector_db.add_documents(chunks, batch_size=32)
    vector_db.save()

    print("✅ Vector database saved")


    # db = BGEVectorStore(index_path="src/vector_db")
    # db.load()
    #
    # results = db.search("Explain transformer architecture", top_k=5)
    #
    # for r in results:
    #     print("\n---")
    #     print("Score:", r["score"])
    #     print("Text:", r["embedding_text"])
    #     print("Source:", r["source_name"])
    #
    # return results

#---------------- RUN ----------------
while "__main__" == "__main__":

    user_query = input("Enter query: ")

    matches = db.search_vector_db(
        query=user_query,
        top_k=5,
        score_threshold=0.35
    )

    # Remove useless short chunks
    matches = [
        r for r in matches
        if len(r["embedding_text"].split()) >= 6
    ]

    if not matches:
        print("❌ No relevant data found")
    else:
        for i, r in enumerate(matches, 1):
            print(f"\nResult #{i}")
            print("Score:", round(r["score"], 3))
            print("Text:", r.get("paragraph_text", r["embedding_text"]))
            print("Source:", r.get("source_name"))

def data_processing():
    split_data = text_chunking("src/pdf/Dsa.pdf")
    text_to_Embeddings(split_data)