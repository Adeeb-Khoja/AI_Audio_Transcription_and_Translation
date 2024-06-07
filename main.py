
from transcript_detect import *
from translation import *


if __name__ == '__main__':
    audio_file_path = 'arabic.mp3'

    whisper_model = WhisperModel('base')

    print('Transcriping audio file....')
    transcription = whisper_model.transcribe_audio(audio_file_path)
    print('Detecting audio language....')
    detected_language = whisper_model.detect_language(audio_file_path)

    # Write the transcription to a text file
    print('Writing transcript into text file...')
    transcript_file_path = "transcript.txt"
    with open(transcript_file_path, "w",encoding="utf-8") as file:
        file.write(transcription)

    # Translate transcript
    translation_model = TranslationModel()
    target_language = 'en'
    print(f'Translating transcript from {detected_language} to {target_language}...')
    transalted_text = translation_model.translate_text(transcription,detected_language,target_language)

    # Write the translation to a text file
    print(f'Transcript translation {transalted_text}')
    print('Writing translation text file...')
    translation_file_path = "translation.txt"
    with open(translation_file_path, "w",encoding="utf-8") as file:
        file.write(transalted_text)