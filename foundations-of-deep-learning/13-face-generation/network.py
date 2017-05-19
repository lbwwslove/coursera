from collections import namedtuple
import config
import layers
import tensorflow as tf
import trainer

Network = namedtuple("Network", [
    "fake_z",
    "fake_x",
    "real_x",
    "d_train_op",
    "g_train_op",
])

def discriminator(images, reuse):
    with tf.variable_scope("discriminator", reuse = reuse):
        # The discriminator is *only* used in training mode.
        return layers.build_layers(
            images,
            config.DISCRIMINATOR_LAYERS,
            True
        )

def generator(fake_z, is_training, reuse):
    with tf.variable_scope("generator", reuse = reuse):
        return layers.build_layers(
            fake_z,
            config.GENERATOR_LAYERS,
            is_training
        )

def network():
    with tf.name_scope("placeholders"):
        real_x = tf.placeholder(
            tf.float32,
            (None, *config.IMAGE_DIMS),
            name = "real_x"
        )

        fake_z = tf.placeholder(
            tf.float32,
            (None, config.Z_DIMS),
            name = "fake_z"
        )

    fake_x = generator(
        fake_z = fake_z,
        is_training = True,
        reuse = False
    )
    discriminator_fake_logits = discriminator(
        images = fake_x,
        reuse = False,
    )
    discriminator_real_logits = discriminator(
        images = real_x,
        reuse = True,
    )

    d_train_op, g_train_op = trainer.trainer(
        real_logits = discriminator_real_logits,
        fake_logits = discriminator_fake_logits
    )

    return Network(
        fake_z = fake_z,
        fake_x = fake_x,
        real_x = real_x,
        d_train_op = d_train_op,
        g_train_op = g_train_op
    )
