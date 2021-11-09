import argparse
import re
import os
import json
import spacy
from spacy.tokens import Span

from tool.file_and_directory_management import read_file_to_list, read_sentences_from_file
from tool.data_generator import json_to_spacy_train_data, spacy_format_to_json
from tool.file_and_directory_management import dir_path, file_path


def generalize_tags(data):
    return re.sub(r"([0-9]+,\s[0-9]+,\s')[a-zA-Z\s\.àâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ]+", r"\1PERSON", str(data))


# generalizing annotations - changing tags containing full names of literary characters to general tag PERSON
# titles - list of novels titles to be inlcluded in the generated data set (titles should not contain any special
#       characters and spaces should be replaced with "_", for example "Pride_andPrejudice")
# names_gold_standard_dir_path - path to directory with .txt files containing gold standard with annotations being full
#       names of literary characters (names of files should be the same as corresponding novels titles on the titles
#       list)
# generated_data_dir - directory where generated data should be stored
def generate_generalized_data(titles, names_gold_standard_dir_path, generated_data_dir):
    for title in titles:
        test_data = json_to_spacy_train_data(names_gold_standard_dir_path + title + ".json")
        generalized_test_data = generalize_tags(test_data)
        spacy_format_to_json(generated_data_dir + "generated_gold_standard\\", generalized_test_data, title)


def test_ner(data, model_dir=None):
    if model_dir is not None:
        nlp = spacy.load(model_dir)
    else:
        nlp = spacy.load("en_core_web_sm")
    result = []
    for sentence in data:
        doc = nlp(sentence)
        dict = {}
        entities = []
        for index, ent in enumerate(doc.ents):
            if ent.label_ == "PERSON":
                span = Span(doc, ent.start, ent.end, label="PERSON")
                doc.ents = [span if e == ent else e for e in doc.ents]
                entities.append([ent.start_char, ent.end_char, "PERSON"])

        dict["content"] = doc.text
        dict["entities"] = entities
        result.append(dict)

    return result


# titles_path - path to .txt file with titles of novels from which the sampled data are to be generated (titles should
#       not contain any special characters and spaces should be replaced with "_", for example "Pride_andPrejudice")
# names_gold_standard_dir_path - path to directory with .txt files containing gold standard with annotations being full
#       names of literary characters (names of files should be the same as corresponding novels titles on the titles
#       list)
# generated_data_dir - directory where generated data should be stored
# testing_data_dir_path - directory containing .txt files with sentences extrated from novels to be included in the
#       testing process
# ner_model_dir_path - path to directory containing fine-tune NER model to be tested; if None standard spacy NER
#       model is used
def main(titles_path, names_gold_standard_dir_path, testing_data_dir_path, generated_data_dir, ner_model_dir_path=None):
    titles = read_file_to_list(titles_path)
    generate_generalized_data(titles, names_gold_standard_dir_path, generated_data_dir)

    for title in titles:
        test_data = read_sentences_from_file(testing_data_dir_path + title)
        ner_result = test_ner(test_data, ner_model_dir_path)

        path = generated_data_dir + "ner_model_annotated\\" + title

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        with open(path, 'w+') as result:
            json.dump(ner_result, result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('titles_path', type=file_path)
    parser.add_argument('names_gold_standard_dir_path', type=dir_path)
    parser.add_argument('testing_data_dir_path', type=dir_path)
    parser.add_argument('generated_data_dir', type=str)
    parser.add_argument('ner_model_dir_path', type=str)
    opt = parser.parse_args()
    main(opt.titles_path, opt.names_gold_standard_dir_path, opt.generated_data_dir,
         opt.testing_data_dir_path, opt.ner_model_dir_path)
