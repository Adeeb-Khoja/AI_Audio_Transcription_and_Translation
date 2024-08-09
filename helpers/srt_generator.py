from datetime import timedelta
import json

# Sample list of subtitle objects
subtitles = [
    {
        "text": " The entire world has been suffering due to the climate change dilemma.",
        "start": 0.0,
        "end": 9.88,
        "id": 0
    },
    # Add more subtitle objects here
]

class SRTGenerator(object):

    @classmethod
    def format_time(cls,seconds):
        """Convert seconds to SRT time format (hh:mm:ss,ms)"""
        ms = int((seconds - int(seconds)) * 1000)
        td = str(timedelta(seconds=int(seconds)))
        return f"{td},{ms:03d}"
    @classmethod
    def generate_srt(cls,subtitles, output_file):
        with open(output_file, 'w',encoding='utf-8') as f:
            for sub in subtitles:
                start_time = cls.format_time(sub['start'])
                end_time = cls.format_time(sub['end'])
                text = sub['text'].strip()
                srt_entry = f"{sub['id'] + 1}\n{start_time} --> {end_time}\n{text}\n\n"
                f.write(srt_entry)



if __name__ == "__main__":
    segments_file = "segments.json"
    with open(segments_file, 'r') as f:
        segments = json.load(f)
    output_srt_file = "subtitles.srt"
    SRTGenerator.generate_srt(segments, output_srt_file)