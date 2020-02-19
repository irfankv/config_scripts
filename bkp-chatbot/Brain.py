import nltk
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()
import sys
import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import API
import re
import multiprocessing, threading
from time import sleep

TERMINATE_THRESHOLD = 1
temp_t = False


def match(q, pat):
    return pat.match(q.lower())


def log(msg, value=""):
    print("\n*****************")
    print("\t" + str(msg) + " = " + str(value))
    print("*****************\n")


def get_options(data):
    options = []
    for intent in data["intents"]:
        item = {"tag": intent["tag"], "response": random.choice(intent["responses"])}
        options.append(item)
    return options


def train_model():
    with open("intents.json") as file:
        data = json.load(file)
    training, output = [], []

    try:
        with open("data.pickle", "rb") as f:
            words, labels, training, output = pickle.load(f)
    except:
        words = []
        labels = []
        docs_x = []
        docs_y = []

        for intent in data["intents"]:
            for pattern in intent["patterns"]:
                wrds = nltk.word_tokenize(pattern)
                words.extend(wrds)
                docs_x.append(wrds)
                docs_y.append(intent["tag"])

            if intent["tag"] not in labels:
                labels.append(intent["tag"])

        words = [stemmer.stem(w.lower()) for w in words if w != "?"]
        words = sorted(list(set(words)))

        labels = sorted(labels)

        # training = []
        # output = []

        out_empty = [0 for _ in range(len(labels))]

        for x, doc in enumerate(docs_x):
            bag = []

            wrds = [stemmer.stem(w) for w in doc]

            for w in words:
                if w in wrds:
                    bag.append(1)
                else:
                    bag.append(0)

            output_row = out_empty[:]
            output_row[labels.index(docs_y[x])] = 1

            training.append(bag)
            output.append(output_row)

        training = numpy.array(training)
        output = numpy.array(output)

        with open("data.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)

    tensorflow.reset_default_graph()
    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)

    # try:
    #    model.load("model.ganesha")
    # except:
    model.fit(training, output, n_epoch=800, batch_size=8, show_metric=True)
    model.save("model.ganesha")

    return model, words, labels, data


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


def fetch_answer(question, model, words, labels, data, user="", type="web"):
    # model, words, labels, data = train_model()
    global temp_t
    temp_t = False
    inp = question.lower()

    tag = ""
    # val_list = []
    # proc_list = []
    ri = re.compile("((ri[-_\s]score)|(riscore)|((ri\s)|(ri$)))")
    bit = re.compile("((bit[-_\s]score)|(bitscore)|((ri\s)|(ri$)))")
    cdets = re.compile("(csc[a-z]{2}[0-9]{5})")
    # ri = re.compile("(\w*\s*)*((ri[-_\s]score)|(riscore)|((ri\s)|(ri$)))")
    # cdets = re.compile("(\w*|\d*|\s*|.*)+(csc[a-z]{2}[0-9]{5})+(\w*|\d*|\s*|.*)")
    # p = threading.Thread(target=match, args=(question, ri))
    # p.start()
    # p.join(1)
    # if p.is_alive():
    #     print("running... let's kill it...")
    #     p.terminate()
    #     p.join()
    # if not p.is_alive():
    #     if temp_t:
    #         tag = "RI_score"
    #         responses = ['']
    #     else:
    #         cdets = re.compile("(\w*|\d*|\s*|.*)*(csc[a-z]{2}[0-9]{5})+(\w*|\d*|\s*|.*)*")
    #         p = threading.Thread(target=match, args=(question, cdets))
    #         p.start()
    #         p.join(1)
    #         if p.is_alive():
    #             print("running... let's kill it...")
    #             p.terminate()
    #             p.join()
    #         if not p.is_alive():
    #             if temp_t:
    #                 tag = "cdets"
    #                 responses = ['']
    # with multiprocessing.Manager() as manager:
    #     #print('ri matching')
    #     val = manager.dict()
    #     val_list.append(val)
    #     proc = multiprocessing.Process(target = match, name = 'ri', args = ("update severity 3 s1s2withoutworkaround ~random data~ CSCum72637", ri))
    #     proc_list.append(proc)
    #     proc.start()
    #     #print('cdets matching')
    #     val1 = manager.dict()
    #     val_list.append(val1)
    #     proc1 = multiprocessing.Process(target = match, name = 'cdets', args = ("update severity 3 s1s2withoutworkaround ~random data~ CSCum72637", cdets))
    #     proc_list.append(proc1)
    #     proc1.start()

    #     join_count = 0
    #     finished_list = []
    #     while len(finished_list) != len(proc_list):
    #         for proc in proc_list:
    #             if proc.name not in finished_list:
    #                 proc.join(0.001)
    #                 if proc.is_alive() and join_count >= TERMINATE_THRESHOLD:
    #                     proc.terminate()
    #                     print('terminated {}'.format(proc.name))

    #                     finished_list.append(proc.name)

    #                 if not proc.is_alive():
    #                     print('joined {}'.format(proc.name))
    #                     print('tag : ', proc.name)
    #                     tag = proc.name
    #                     finished_list.append(proc.name)
    #         sleep(0.5)
    #         join_count += 1
    if "schedule" in question.lower():
        tag = "schedule"
    elif ri.search(question.lower()):
        tag = "RI_score"
    elif "smu" in question.lower():
        tag = "smu"
    elif bit.search(question.lower()):
        tag = "Bit_score"
    elif cdets.search(question.lower()):
        tag = "cdets"
    elif "rally" in question.lower():
        tag = "rally"
    elif "pims" in question.lower():
        tag = "pims"
    elif "dir" in question.lower():
        tag = "directory"

    if "help" in question.lower():
        tag = "help"

    # if results[results_index] > 0.5:
    if tag == "":
        bag = bag_of_words(inp, words)
        results = model.predict([bag])
        results_index = numpy.argmax(results)
        tag = labels[results_index]

    log("TAG", tag)

    # if results[results_index] > 0.5:

    for tg in data["intents"]:
        if tg["tag"] == tag:
            responses = tg["responses"]
            api_call = tg["api_call"]

    results = []
    title = ""
    try:
        content = getattr(API, api_call)(question, user, type)
        log("content", content)
        results = content["results"]
        title = content["title"]
    except Exception as e:
        log("ERROR", e)
    log("results", results)
    answer = random.choice(responses)
    link = None
    if answer.startswith("http"):
        link = answer
        answer = "You'll find more data in this link"
    # else:
    #     answer =  "I don't understand, please try asking me something else"

    options = get_options(data)
    return tag, answer, results, link, title, options


def improve_learning(tag, question):
    with open("intents.json") as file:
        data = json.load(file)

    for intent in data["intents"]:
        if intent["tag"] == tag:
            index = data["intents"].index(intent)
            if question not in data["intents"][index]["patterns"]:
                data["intents"][index]["patterns"].append(question)

    with open("intents.json", "w") as file:
        json.dump(data, file, indent=4, sort_keys=True)


def receive_feedback(identified_tag, tag, response, question, flag):
    data = None
    with open("intents.json") as file:
        data = json.load(file)

        for intent in data["intents"]:
            if intent["tag"] == identified_tag:
                index = data["intents"].index(intent)
                data["intents"][index]["patterns"].remove(question)
        if flag:
            data["intents"].append(
                {
                    "tag": tag,
                    "patterns": [question],
                    "responses": [response],
                    "api_call": "",
                }
            )
        else:
            for intent in data["intents"]:
                if intent["tag"] == tag:
                    index = data["intents"].index(intent)
                    if question not in data["intents"][index]["patterns"]:
                        data["intents"][index]["patterns"].append(question)

    with open("intents.json", "w") as file:
        json.dump(data, file, indent=4, sort_keys=True)

    train_model()
