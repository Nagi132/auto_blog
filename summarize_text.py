from transformers import pipeline
import logging
import torch


def summarize_text(text, summarizer):
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
    return summary[0]['summary_text']


if __name__ == '__main__':
    model_name = 'tsmatz/mt5_summarize_japanese'
    logging.info('Loading tokenizer and model...')
    device = 0 if torch.cuda.is_available() else -1  # Use GPU if available

    summarizer = pipeline('summarization', model=model_name, device=device)

    logging.info('Loading conversations...')
    with open('data/cleaned_conversations.txt', 'r', encoding='utf-8') as f:
        conversations = f.readlines()

    logging.info('Generating summaries...')
    summaries = [summarize_text(conv, summarizer) for conv in conversations]

    logging.info('Saving summaries...')
    with open('data/summaries.txt', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(summaries))
    logging.info('Summaries saved.')
