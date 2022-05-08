#!/bin/bash
set -e

# argument1 - directory name with goldstandard person annotation inside 'data/testing_sets' directory
# argument2 - name of experiment; subdirectory of 'experiments' directory
# argument3 - name of stats directory

for model in pl_core_news_sm pl_core_news_md pl_core_news_lg xx_ent_wiki_sm; do
  time python -m tool.scripts.compute_metrics data/novels_titles/polish_test_set.txt data/testing_sets/"$1"/ experiments/"$2"/spacy__${model}/ experiments/"$2"/spacy__${model}/"$3" --print_results
done

for model in ner-multi ner-multi-fast; do
  time python -m tool.scripts.compute_metrics data/novels_titles/polish_test_set.txt data/testing_sets/"$1"/ experiments/"$2"/flair__${model}/ experiments/"$2"/flair__${model}/"$3" --print_results
done

for model in jplu/tf-xlm-r-ner-40-lang Davlan/distilbert-base-multilingual-cased-ner-hrl Davlan/bert-base-multilingual-cased-ner-hrl; do
  time python -m tool.scripts.compute_metrics data/novels_titles/polish_test_set.txt data/testing_sets/"$1"/ experiments/"$2"/transformers__${model/*\//}/ experiments/"$2"/transformers__${model/*\//}/"$3" --print_results
done

for model in kpwr-n82-base cen-n82-base cen-n82-large nkjp-base nkjp-base-sq conll-english-large-sq; do
  time python -m tool.scripts.compute_metrics data/novels_titles/polish_test_set.txt data/testing_sets/"$1"/ experiments/"$2"/pdn2__${model/*\//}/ experiments/"$2"/pdn2__${model/*\//}/"$3" --print_results
done
