import json

words_list = []
with open("words.txt", encoding= "utf-8") as word_read:
    for i in word_read:
        word = i.lower().split("\n")[0]
        if word != "":
            words_list.append(word)
with open("words.json", "w", encoding= "utf-8") as word_write:
    json.dump(words_list, word_write)