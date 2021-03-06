# -*- coding: utf-8 -*- 
# author: Honay.King

import os
import json
import jieba


def load_dict(dictFile):
    if not os.path.exists(dictFile):
        print('[ERROR] load_dict failed! | The params {}'.format(dictFile))
        return None
    with open(dictFile, 'r', encoding='UTF-8') as df:
        dictF = json.load(df)
    text2id, id2text = dict(), dict()
    count = 0
    for key, value in dictF.items():
        text2id[key] = count
        id2text[count] = key
        count += 1
    return text2id, id2text


def text2id(textline, target_dict):
    textline = jieba.lcut(textline)
    text_list = list()
    for i in range(len(textline)):
        if textline[i] in target_dict.keys():
            text_list.append(target_dict[textline[i]])
        else:
            text_list.append(target_dict['_unk_'])
    text_len = len(text_list)
    return text_list, text_len


def read_data(data, source_dict, target_dict):
    source_list, source_lens, target_list, target_lens = list(), list(), list(), list()
    for ind, row in data.iterrows():
        source, source_len = text2id(row['title']+row['ask'], source_dict)
        source_list.append(source)
        source_lens.append(source_len)
        target, target_len = text2id(row['answer'], target_dict)
        target_list.append(target)
        target_lens.append(target_len)
    return [source_list, source_lens], [target_list, target_lens]


def pad_sentence_batch(sentence_batch, padding):
    '''
    对batch中的序列进行补全，保证batch中的每行都有相同的sequence_length
    参数：
    - sentence batch
    - padding: <PAD>对应索引号
    '''
    max_sentence = max([len(sentence) for sentence in sentence_batch])
    return [sentence + [padding] * (max_sentence - len(sentence)) for sentence in sentence_batch]


def get_batches(targets, sources, batch_size, source_padding, target_padding):
    source_list, source_lens = sources
    target_list, target_lens = targets
    for batch_i in range(0, len(source_list)//batch_size):
        start_i = batch_i * batch_size
        source_batch = source_list[start_i: start_i + batch_size]
        source_len_batch = source_lens[start_i: start_i + batch_size]
        target_batch = target_list[start_i: start_i + batch_size]
        target_len_batch = target_lens[start_i: start_i + batch_size]

        pad_sources_batch = pad_sentence_batch(source_batch, source_padding)
        pad_targets_batch = pad_sentence_batch(target_batch, target_padding)

        yield pad_targets_batch, pad_sources_batch, target_len_batch, source_len_batch


if __name__ == "__main__":
    # 测试predict是否OK
    from prediction import Prediction

    model = Prediction()
    model.load_model()

    result = model.predict(department='', title='孕妇经常胃痛会影响到胎儿吗',
                           ask='"我怀上五个多月了,自从怀上以来就经常胃痛(两个胸之间往下一点儿是胃吧?)有时痛十几分钟,有时痛'
                               '半个钟,每次都痛得好厉害,不过痛过这一阵之后就不痛了,我怀上初期饮食不规律,经常吃不下东西,会不'
                               '会是这样引发的呀?我好忧心对胎儿有影响,该怎么办呢?可有食疗的方法可以纾解一下痛呢?"')
    print(result)

    exit(0)
