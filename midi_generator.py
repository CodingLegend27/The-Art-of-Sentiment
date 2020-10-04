import numpy as np
import tensorflow as tf
import midi_loader as me

GENERATED_DIR = './generated'
def preprocess_sentence(text, front_pad='\n ', end_pad=''):
    text = text.replace('\n', ' ').strip()
    text = front_pad+text+end_pad
    return text

def override_neurons(model, layer_index, override):
    h_state, c_state = model.get_layer(index=layer_index).states

    c_state = c_state.numpy()
    for neuron, value in override.items():
        c_state[:,int(neuron)] = int(value)

    model.get_layer(index=layer_index).states = (h_state, tf.Variable(c_state))

def sample_next(predictions, k):
    top_k = tf.math.top_k(predictions, k)
    top_k_choices = top_k[1].numpy().squeeze()
    top_k_values = top_k[0].numpy().squeeze()

    if np.random.uniform(0, 1) < .5:
        predicted_id = top_k_choices[0]
    else:
        p_choices = tf.math.softmax(top_k_values[1:]).numpy()
        predicted_id = np.random.choice(top_k_choices[1:], 1, p=p_choices)[0]

    return predicted_id

def process_init_text(model, init_text, char_to_index, layer_index, override):
    model.reset_states()

    for c in init_text.split(" "):
        try:
            input_eval = tf.expand_dims([char_to_index[c]], 0)

            override_neurons(model, layer_index, override)

            predictions = model(input_eval)
        except KeyError:
            if c != "":
                print("Can't process char", c)

    return predictions

def generate_midi(model, char_to_index, index_to_char, init_text="", seq_len=256, k=3, layer_index=-2, override={}):
    init_text = preprocess_sentence(init_text)

    midi_generated = []

    predictions = process_init_text(model, init_text, char_to_index, layer_index, override)

    model.reset_states()
    for i in range(seq_len):
        predictions = tf.squeeze(predictions, 0).numpy()

        predicted_id = sample_next(predictions, k)

        midi_generated.append(index_to_char[predicted_id])

        override_neurons(model, layer_index, override)

        input_eval = tf.expand_dims([predicted_id], 0)
        predictions = model(input_eval)

    return init_text + " " + " ".join(midi_generated)

def generate_midi_2_sentiments(model, char_to_index, index_to_char, init_text="", seq_len=256, k=3, layer_index=-2, first_override={}, second_override={}):
    first_text = generate_midi(model, char_to_index, index_to_char, "", seq_len=int(seq_len/2), k=k, layer_index=layer_index, override=first_override)
    
    second_text = generate_midi(model, char_to_index, index_to_char, first_text, seq_len=int(seq_len/2), k=k, layer_index=layer_index, override=second_override)
    
    return init_text + " " + second_text
    
    
