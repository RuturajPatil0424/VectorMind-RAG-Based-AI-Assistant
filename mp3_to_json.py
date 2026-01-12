import whisper
import json
import os

model = whisper.load_model("large-v2")

audios = os.listdir("src/audio")

for audio in audios:
        title = audio
        result = model.transcribe(audio = f"src/audio/{audio}",
                              language="hi",
                              task="translate",
                              word_timestamps=False)
        
        chunks = []
        for segment in result["segments"]:
            chunks.append({"title":title, "start": segment["start"], "end": segment["end"], "text": segment["text"]})
        
        chunks_with_metadata = {"chunks": chunks, "text": result["text"]}

        with open(f"src/jsons/{audio}.json", "w") as f:
            json.dump(chunks_with_metadata,f)