from transformers import AutoTokenizer

def tokenize_and_encode(tokenizer, text):
    tokens = tokenizer.tokenize(text)
    input_ids = tokenizer.convert_tokens_to_ids(tokens)
    return tokens, input_ids
