import os
import numpy as np
import matplotlib.pyplot as plt

# Ordner zum Speichern der Graphen
PLOTS_DIR = "./results"

def plot_logits(xs, ys, top_neurons):
    for n in top_neurons:
        plot_logit_and_save(xs, ys, n)
        
def plot_logit_and_save(xs, ys, index_neuron):
    sentiment_unit = xs[:, index_neuron]
    
    plt.ylabel('Anzahl der Phrasen')
    plt.xlabel('Wert des Gefühls-Neuron')
    plt.hist(sentiment_unit[ys == -1], bins=50, alpha=0.5, label='Negative Phrase')
    plt.hist(sentiment_unit[ys == 1], bins=50, alpha=0.5, label='Positive Phrase')
    plt.legend()
    plt.savefig(os.path.join(PLOTS_DIR, "neuron_" + str(index_neuron) + '.png'))
    plt.clf()
    
def plot_weight_contribs(coef):
    plt.title('Werte der Gewichtungen')
    plt.tick_params(axis='both', which='major')
    
    norm = np.linalg.norm(coef)
    coef = coef/norm
    
    plt.plot(range(len(coef[0])), coef.T)
    plt.xlabel('Index des Neurons')
    plt.ylabel('Gewichtung des Neuron')
    plt.savefig(os.path.join(PLOTS_DIR, "gewichtungen.png"))