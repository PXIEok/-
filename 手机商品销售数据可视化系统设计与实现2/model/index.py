import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Dense, Concatenate
import pandas
import os
from math import sqrt
from utils.query import querys


def predict(user_id_to_predict):
    userList = querys('select * from user', [], 'select')
    noticesList = querys('select * from notices', [], 'select')
    startList = []
    for n in noticesList:
        for u in userList:
            if n[3] == u[1]:
                startList.append([int(u[0]), int(n[-2]), int(n[-1])])
    user_ids = [x[0] for x in startList]
    item_ids = [x[1] for x in startList]

    num_users = max(user_ids) + 1
    num_items = max(item_ids) + 1

    embedding_size = 10
    user_input = Input(shape=(1,), name='user_input')
    item_input = Input(shape=(1,), name='item_input')

    user_embedding = Embedding(input_dim=num_users, output_dim=embedding_size, input_length=1)(user_input)
    item_embedding = Embedding(input_dim=num_items, output_dim=embedding_size, input_length=1)(item_input)

    user_flat = Flatten()(user_embedding)
    item_flat = Flatten()(item_embedding)

    concat = Concatenate()([user_flat, item_flat])
    dense1 = Dense(64, activation='relu')(concat)
    dense2 = Dense(32, activation='relu')(dense1)

    output = Dense(num_items, activation='softmax')(dense2)

    model = Model(inputs=[user_input, item_input], outputs=output)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    model.fit([np.array(user_ids), np.array(item_ids)], np.array(item_ids), epochs=20, batch_size=2)

    user_id_to_predict = user_id_to_predict

    if user_id_to_predict < num_users:
        inputs = np.array([user_id_to_predict])
        predictions = model.predict([inputs, np.zeros_like(inputs)])

        num_recommendations = 5
        top_item_indices = np.argsort(predictions.flatten())[-num_recommendations:][::-1]
        resultList = []
        productsList = querys('select * from products', [], 'select')

        for top_item_id in top_item_indices:
            for travel in productsList:
                if top_item_id == travel[0]:
                    resultList.append(travel)
        return resultList
    else:
        print("索引超出范围，无法进行预测。")


if __name__ == "__main__":
    print(predict(1))
