# RESEARCH — Faz 9: Yayın

## HuggingFace Dataset API

```python
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi

api = HfApi(token=os.environ['HF_TOKEN'])

# Create dataset card
# Push with configs for each task
dataset_dict = DatasetDict({
    'train': Dataset.from_parquet('data/processed/.../train.parquet'),
    'val': Dataset.from_parquet('data/processed/.../val.parquet'),
    'test': Dataset.from_parquet('data/processed/.../test.parquet'),
})
dataset_dict.push_to_hub('enesdemir/f1-analytics-dataset', config_name='tyre_degradation')
```

## Kaggle API

```python
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# Dataset create + upload
api.dataset_create_new(...)
```

## Riskler
- HF rate limit: 30GB free storage, proje ~500MB → sorun değil
- Kaggle dataset size limit: 20GB → Parquet sıkıştırmayla ~200MB
- Token: HF_TOKEN ve KAGGLE_KEY .env'de olmalı, asla commit edilmemeli
