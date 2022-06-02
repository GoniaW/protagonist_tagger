#!/bin/bash
set -e

# argument1 - name of experiment; subdirectory of 'experiments' directory

for model in pl_core_news_sm pl_core_news_md pl_core_news_lg xx_ent_wiki_sm; do
  python -m tool.scripts.annotate_ner docker_test/titles.txt docker_test/ docker_test/experiments/"$1"/spacy__${model}/ spacy ${model}
done

for model in ner-multi ner-fast; do
  python -m tool.scripts.annotate_ner docker_test/titles.txt docker_test docker_test/experiments/"$1"/flair__${model}/ flair ${model}
done

for model in jplu/tf-xlm-r-ner-40-lang Davlan/distilbert-base-multilingual-cased-ner-hrl Davlan/bert-base-multilingual-cased-ner-hrl; do
  python -m tool.scripts.annotate_ner docker_test/titles.txt docker_test docker_test/experiments/"$1"/transformers__${model/*\//}/ transformers ${model}
done

for model in kpwr-n82-base cen-n82-base cen-n82-large nkjp-base nkjp-base-sq conll-english-large-sq; do
  python -m tool.scripts.annotate_ner docker_test/titles.txt docker_test docker_test/experiments/"$1"/pdn2__${model/*\//}/ poldeepner ${model} "${@:2}"
done
