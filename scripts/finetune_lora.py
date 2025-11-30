from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType
import torch

dataset = load_dataset("json", data_files="data/nl_sql_pairs.jsonl", split="train")
dataset = dataset.train_test_split(test_size=0.1)

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
def tokenize(batch):
    return tokenizer(batch["question"], text_target=batch["sql"], truncation=True, padding="max_length", max_length=128)
dataset = dataset.map(tokenize, batched=True)

model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
lora_config = LoraConfig(task_type=TaskType.SEQ_2_SEQ_LM, r=8, lora_alpha=16, lora_dropout=0.1)
model = get_peft_model(model, lora_config)

args = TrainingArguments(
    output_dir="model/fine_tuned_model",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    logging_dir="logs",
    evaluation_strategy="epoch",
    save_strategy="epoch"
)

trainer = Trainer(model=model, args=args, train_dataset=dataset["train"], eval_dataset=dataset["test"])
trainer.train()
model.save_pretrained("model/fine_tuned_model")
