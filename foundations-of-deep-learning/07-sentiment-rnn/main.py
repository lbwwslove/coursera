from collections import Counter, namedtuple
import numpy as np
import string
import tensorflow as tf

BatchInfo = namedtuple("BatchInfo", [
    "epoch_idx",
    "batch_idx",
    "inputs",
    "labels",
    "num_batches",
])
RunInfo = namedtuple("RunInfo", [
    "session",
    "graph",
    "data_set",
    "saver",
])

def run_batch(run_info, batch_info):
    ri = run_info
    initial_cell_states = run_info.session.run(
        ri.graph.initial_cell_states
    )

    avg_cost, accuracy, _ = ri.session.run([
        ri.graph.avg_cost, ri.graph.accuracy, ri.graph.optimizer
    ], feed_dict = {
        ri.graph.inputs: batch_info.inputs,
        ri.graph.labels: batch_info.labels,
        ri.graph.keep_prob: 0.5,
        ri.graph.initial_cell_states: initial_cell_states
    })

    print(f"Epoch: {batch_info.epoch_idx}/{NUM_EPOCHS}",
          f"Batch: {batch_info.batch_idx}/{batch_info.num_batches}",
          f"Train loss: {avg_cost:.3f}",
          f"accuracy: {accuracy:.3f}")

def run_validation(run_info, batch_info):
    ri = run_info

    initial_cell_states = ri.session.run(ri.graph.initial_cell_states)

    validation_accuracy = 0.0
    (validation_x, validation_y) = ri.data_set.dataset("validation")
    num_batches = ri.data_set.num_batches(validation_x, validation_y)
    batches = run_info.data_set.get_batches(validation_x, validation_y)
    for inputs, labels in batches:
        feed = {inputs_: x,
                labels_: y,
                keep_prob: 1,
                initial_state: val_state}
        batch_accuracy = sess.run(ri.accuracy, feed_dict = {
            ri.graph.inputs: inputs,
            ri.graph.labels: labels,
            ri.graph.keep_prob: 1.0,
        })
        validation_accuracy += batch_acc

    validation_accuracy /= num_batches
    print(f"Val acc: {validation_accuracy:.3f}")

def run_epoch(run_info, epoch_idx):
    (train_x, train_y) = run_info.data_set.dataset("train")
    batches = run_info.data_set.get_batches(train_x, train_y)
    num_batches = run_info.data_set.num_batches(train_x, train_y)
    for batch_idx, (inputs, labels) in enumerate(batches, 1):
        batch_info = BatchInfo(
            epoch_idx = epoch_idx,
            batch_idx = batch_idx,
            inputs = inputs,
            labels = labels,
            num_batches = num_batches
        )

        run_batch(run_info, batch_info)

        if batch_idx % BATCHES_PER_VALIDATION == 0:
            run_validation()

def run(session):
    data_set = DataSet()
    run_info = RunInfo(
        session = session,
        graph = build_graph(data_set.vocab_size()),
        data_set = data_set,
        saver = tf.train.Saver()
    )

    print(f"Label counts: {run_info.data_set.label_counts()}")

    session.run(tf.global_variables_initializer())
    for epoch_idx in range(NUM_EPOCHS):
        run_epoch(run_info, epoch_idx)
        run_info.saver.save(session, CHECKPOINT_NAME)

with tf.Session() as session:
    run(session)