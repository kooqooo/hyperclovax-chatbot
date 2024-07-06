from transformers import pipeline

class ReaderModel:
    def __init__(self, model_):
        self.reader = pipeline("question-answering", model=model_)

    def extract_answer(self, query, context):
        return self.reader(question=query, context=context)