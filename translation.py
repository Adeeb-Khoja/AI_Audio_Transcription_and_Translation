from transformers import MarianMTModel, MarianTokenizer

class TranslationModel(object):
    def __init__(self):
        pass

    def translate_chunk(self,chunk, src_lang, tgt_lang):
        try:

            model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'
            model = MarianMTModel.from_pretrained(model_name)
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            
            inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=512)
            translated_tokens = model.generate(**inputs)
            translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            
            return translated_text

        except Exception as e:
            print(e)
            raise Exception(f"Error translating text {e}")

    def translate_text(self,text, src_lang, tgt_lang):
        max_length = 512
        chunks = self.split_text(text, max_length)
        translated_chunks = [self.translate_chunk(chunk, src_lang, tgt_lang) for chunk in chunks]
        return ' '.join(translated_chunks)



    def split_text(self,text, max_length):
        # Split text into sentences
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                current_chunk += sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks