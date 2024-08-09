from transformers import MarianMTModel, MarianTokenizer
import torch

class TranslationModel(object):
    def __init__(self, src_lang, tgt_lang, use_gpu=True):
        model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'
        self.model = MarianMTModel.from_pretrained(model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def translate_chunks(self, chunks):
        # Tokenize all chunks together
        inputs = self.tokenizer(chunks, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
        
        # Generate translations for all chunks in one call
        translated_tokens = self.model.generate(**inputs)
        
        # Decode translated tokens
        translated_texts = [self.tokenizer.decode(tokens, skip_special_tokens=True) for tokens in translated_tokens]
        
        return translated_texts

    def translate_text(self, text):
        max_length = 512
        chunks = self.split_text(text, max_length)
        
        # Translate chunks in batches
        translated_chunks = self.translate_chunks(chunks)
        
        return ' '.join(translated_chunks)

    def split_text(self, text, max_length):
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