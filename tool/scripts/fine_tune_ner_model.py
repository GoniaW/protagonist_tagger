from __future__ import unicode_literals, print_function
import random
import warnings
import spacy
from spacy.util import minibatch, compounding
from tool.data_generator import json_to_spacy_train_data
from tool.file_and_directory_management import read_file_to_list
import sys


# titles_path - path to .txt file with titles of novels from which the sampled data are to be generated (titles should
#       not contain any special characters and spaces should be replaced with "_", for example "Pride_andPrejudice")
# training_set_1_dir_path - path to directory with .txt files containing training sets corresponding to each novel
#       (names of files should be the same as titles on the list from titles_path); this training set was created by
#       including named entities not recognized by standard NER model
# training_set_2_path - path to file containing raining set generated by injecting commmon English names into sentences
#       extracted form novels
def prepare_training_data(titles_path, training_set_1_dir_path, training_set_2_path):
    titles = read_file_to_list(titles_path)
    train_data = []

    for title in titles:
        data_slice = json_to_spacy_train_data(training_set_1_dir_path + title)
        train_data.extend(data_slice)

    data_second_set = json_to_spacy_train_data(training_set_2_path)
    train_data.extend(data_second_set)

    return train_data


# model_output_dir - path to directory where fine-tuned NER model should be stored
def fine_tune_ner(model_output_dir):
    train_data = prepare_training_data()
    n_iter = 100
    nlp = spacy.load("en_core_web_sm")

    # if "ner" not in nlp.pipe_names:
    #     ner = nlp.create_pipe("ner")
    #     nlp.add_pipe(ner, last=True)
    # else:
    #     ner = nlp.get_pipe("ner")
    # for _, annotations in train_data:
    #     for ent in annotations.get("entities"):
    #         ner.add_label(ent[2])

    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        warnings.filterwarnings("once", category=UserWarning, module='spacy')
        for itn in range(n_iter):
            random.shuffle(train_data)

            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            print("Losses", losses)

    for text, _ in train_data:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    if model_output_dir is not None:
        nlp.to_disk(model_output_dir)
        nlp2 = spacy.load(model_output_dir)
        for text, _ in train_data:
            doc = nlp2(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])


# model_output_dir - path to directory where fine-tuned NER model should be stored
# titles_path - path to .txt file with titles of novels from which the sampled data are to be generated (titles should
#       not contain any special characters and spaces should be replaced with "_", for example "Pride_andPrejudice")
# training_set_1_dir_path - path to directory with .txt files containing training sets corresponding to each novel
#       (names of files should be the same as titles on the list from titles_path); this training set was created by
#       including named entities not recognized by standard NER model
# training_set_2_path - path to file containing raining set generated by injecting commmon English names into sentences
#       extracted form novels
def main(model_output_dir, titles_path, training_set_1_dir_path, training_set_2_path):
    # prepare_training_data(titles_path, training_set_1_dir_path, training_set_2_path)
    fine_tune_ner(model_output_dir)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
