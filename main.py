
import json
from transcript_detect import *
from translation import *


def translate_segments(segments,translator: TranslationModel,from_lang,to_lang):
    transalted_segments = []
    for segment in segments:
        translated_segment_text = translator.translate_text(segment['text'],from_lang,to_lang)
        transalted_segments.append({'text':translated_segment_text,'start':segment['start'],'end':segment['end'],'id':segment['id']})
    
    return transalted_segments

if __name__ == '__main__':
    audio_file_path = 'english.mp3'

    whisper_model = WhisperModel('base')

    print('Transcriping audio file....')
    transcription = whisper_model.transcribe_audio(audio_file_path)

    print('Generating transctipt text...')
    transcript_text = whisper_model.get_text(transcription)

    print('Detecting audio language....')
    detected_language = whisper_model.get_detected_language(transcription)

    print('Generating transcript segments...')
    transcript_segments = whisper_model.get_segments(transcription)
    

    # Write the transcription to a text file
    print('Writing transcript into text file...')
    transcript_file_path = "transcript_segments.txt"
    with open(transcript_file_path, "w",encoding="utf-8") as file:
        file.write(transcript_text)

    # Translate transcript
    translation_model = TranslationModel()
    target_language = 'ar'

    print(f'Translating transcript text from {detected_language} to {target_language}...')
    transalted_text = translation_model.translate_text(transcript_text,detected_language,target_language)

    print(f'Translating transcript segments from {detected_language} to {target_language}...')
    transalted_segments = translate_segments(transcript_segments,translation_model,detected_language,target_language)

    # Write the translation to a text file
    print('Writing translation text file...')
    translation_file_path = "translation.txt"
    with open(translation_file_path, "w",encoding="utf-8") as file:
        file.write(transalted_text)

    print('Writing transcsript segments and translated segments to json file...')
    segments_file_path = "segments.json"
    both_segments = transcript_segments + transalted_segments
    with open(segments_file_path, "w",encoding="utf-8") as file:
        json.dump(both_segments, file,ensure_ascii=False)