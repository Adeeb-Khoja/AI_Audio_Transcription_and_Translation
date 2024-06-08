import whisper

class WhisperModel(object):

    def __init__(self,model_type):
        self.model = whisper.load_model("base")
    # Transcribe an audio file
    def transcribe_audio(self,file_path):
        try:
            result = self.model.transcribe(file_path)
            return result
        except Exception as e:
            print(f"Error {e}")
            raise Exception(f'Error trnascribe audio file {e}')

    def get_text(self,transcription):
        return transcription['text']
    
    def get_detected_language(self,transcription):
        return transcription['language']
    
    def get_segments(self,transcription):
        text_segments = []
        for segment in transcription['segments']:
            text_segments.append({
                "text": segment['text'],
                "start": segment['start'],
                "end": segment['end'],
                "id": segment['id'],
            })
        return text_segments

    def detect_language(self,file_path):
        try:
            audio = whisper.load_audio(file_path)
            audio = whisper.pad_or_trim(audio)
            # make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            # detect the spoken language
            _, probs = self.model.detect_language(mel)
            print(f"Detected language: {max(probs, key=probs.get)}")
            return max(probs, key=probs.get)
        except Exception as e:
            print(f"Error {e}")
            raise Exception(f'Error detecting language {e}')


