from transformers import MarianMTModel, MarianTokenizer

class TranslationModel(object):
    def __init__(self):
        pass

    def translate_text(self,text, src_lang, tgt_lang):
        try:
            # Load the MarianMT model and tokenizer for the specific language pair
            model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'
            model = MarianMTModel.from_pretrained(model_name)
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            
            # Tokenize the text
            translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
            
            # Decode the tokens to get the translated text
            translated_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
            return translated_text[0]
        except Exception as e:
            print(e)
            raise Exception(f"Error translating text {e}")


