import os
import numpy as np
import music21
import math

# Parameter n_pitch: Pitch-Range reicht von 0 bis 127
MAX_PITCH = 128

# Parameter d_[duration]_[dots]: 
SIGN_DUR = "d"

# Parameter v_[velocity]: Lautstärke der folgenden Noten, reicht von 4, 8, 12, ... bis 128 (in 4er-Schritten)
SIGN_VELO = "v"
MIN_VELO = 0
MAX_VELO = 128

# Parameter t_[tempo]: Tempo der folgenden Noten, reicht von 24, 28, 32, ... bis 160 (in 4er-Schritten)
SIGN_TEMP0 = "t"
MIN_TEMP0 = 24
MAX_TEMPO = 128

# Zeichen zur Markierung des Ende des Stücks (End Of File)
SIGN_EOF = "\n"

# neue Note
SIGN_NOTE = "n"

# Zeichen für die Wait-Zeit
SIGN_WAIT = "w"

# 3-punktierte Halbe und 3-punktierte 32-tel
THREE_DOTTED_BREVE = 15
THREE_DOTTED_32ND  = 0.21875



def load_midi(data_path, sample_freq=4, piano_range=(33, 93), transpo_range=10, stretching_range=10):
    text = ""
    vocab = set()
    
    if os.path.isfile(data_path):
        # gegebener Pfad ist eine einzelne Midi-Datei
        file_extension = os.path.splitext(data_path)[1]
        
        if file_extension == ".midi" or file_extension == ".mid":
            text = parse_midi(file_path=data_path, piano_range=piano_range, sample_freq=sample_freq, 
                              transpo_range=transpo_range, stretching_range=stretching_range)
            vocab = set(text.split(" "))
            
    else:
        # Lade jede Datei einzeln
        for file in os.listdir(data_path):
            file_path = os.path.join(data_path, file)
            file_extension = os.path.splitext(file_path)[1]
            
            # Prüfen, ob der file_path kein weiterer Ordner ist und ob die Dateiendung passt (.mid oder .midi)
            if os.path.isfile(file_path) and (file_extension == ".midi" or file_extension == ".mid"):
                encoded_midi = parse_midi(file_path=file_path, piano_range=piano_range, sample_freq=sample_freq, 
                                          transpo_range=transpo_range, stretching_range=stretching_range)
                
                if len(encoded_midi) > 0:
                    words = set(encoded_midi.split(" "))
                    vocab = vocab | words
                    
                    text += encoded_midi + " "

            
        # letztes Leerzeichen wird entfernt
        text = text[:-1]
        
    return text, vocab

def parse_midi(file_path: str, piano_range, sample_freq, transpo_range, stretching_range):
    midi_file_path = None
    
    print(f"> Parse MIDI-File: {file_path}")
    
    # Als Parameter kann auch eine Datei mit Pfad übergeben werden:
    midi_dir = os.path.dirname(file_path)
    midi_name = os.path.basename(file_path).split(".") [0]
    
    # Falls eine txt-Datei von dieser Midi-Datei bereits existiert, wird diese geladen
    midi_txt_name = os.path.join(midi_dir, midi_name + ".txt")
    
    if (os.path.isfile(midi_txt_name)):
        midi_file_path = open(midi_txt_name, "r")
        encoded_midi = midi_file_path.read()
    else:
        # Lade mit Music21 die Midi-Datei
        midi = music21.midi.MidiFile()
        midi.open(file_path)
        midi.read()
        midi.close()
        
        # Konvertierung der Midi-Datei in Liste mit Noten und Akkorden
        encoded_midi = midi_to_encoded(midifile=midi, piano_range=piano_range, sample_freq=sample_freq, 
                                       transpo_range=transpo_range, stretching_range=stretching_range)
        
        if len(encoded_midi) > 0:
            # neue txt-Datei erzeugen
            midi_file_path = open(midi_txt_name, "w+")
            midi_file_path.write(encoded_midi)
            midi_file_path.flush()
        
    
    if midi_file_path: midi_file_path.close()
        
    return encoded_midi

def midi_to_encoded(midifile, piano_range, sample_freq, transpo_range, stretching_range):
    try:
        stream = music21.midi.translate.midiFileToStream(midifile)
    except:
        return []

    piano_roll = midi_to_piano_roll(midi_stream=stream, sample_freq=sample_freq, piano_range=piano_range, 
                                    transpo_range=transpo_range, stretching_range=stretching_range)
        
    encoded = piano_roll_to_encoded(piano_roll)
    return " ".join(encoded)

def piano_roll_to_encoded(piano_roll):
    # Konvertierung der piano_roll in eine Liste mit Strings, die die Noten darstellen sollen
    encoded = {}
    counter = 0
    
    for version in piano_roll:
        # letztes Tempo, Geschwindigkeit und Dauer auf -1 setzen
        _tempo = -1
        _velo = -1
        _duration = -1.0
        
        version_encoded = []
        
        for i in range(len(version)):
            # die letzten Noten sind in der letzten Reihe gespeichert
            tempo = version[i, -1][0]
            
            # neues Tempo wird hinzugefügt
            if tempo != 0 and tempo != _tempo:
                version_encoded.append(SIGN_TEMP0 + "_" + str(int(tempo)))
                _tempo = tempo
            
            # Fahre mit dem aktuellen Time Step fort
            for next_step in range(len(version[i]) -1):
                duration = version[i, next_step][0]
                velo = int(version[i, next_step][1])
                
                # neues Tempo
                if velo != 0 and velo != _velo:
                    version_encoded.append(SIGN_VELO + "_" + str(velo))
                    _velo = velo
                
                # neue Duration
                if duration != 0 and duration != _duration:
                    duration_tuple = music21.duration.durationTupleFromQuarterLength(duration)
                    version_encoded.append(SIGN_DUR + "_" + duration_tuple.type + "_" + str(duration_tuple.dots))
                    _duration = duration
                
                # neue Note wird hinzugefügt
                if velo != 0 and duration != 0:
                    version_encoded.append(SIGN_NOTE + "_" + str(next_step))

            # Ende dieses Zeitabschnittes
            if (len(version_encoded) > 0) and version_encoded[-1][0] == SIGN_WAIT:
                # 'Warte'-Zeit wird um 1 erhöht
                version_encoded[-1] = "w_" + str(int(version_encoded[-1].split("_")[1]) + 1)
            else:
                version_encoded.append("w_1")
            
        # Ende des Stücks markieren
        version_encoded.append(SIGN_EOF)
        
        # Check, ob diese Version der MIDI-Datei nicht schon mal hinzugefügt wurde
        version_encoded_str = " ".join(version_encoded)
        if version_encoded_str not in encoded:
            encoded[version_encoded_str] = counter
        
        counter += 1
    
    return encoded.keys()


def write(encoded_midi, path):
    # Erzeugt eine Midi-Datei mit dem gegebenen Midi-Daten
    midi = encoded_to_midi(encoded_midi)
    midi.open(path, "wb")
    midi.write()
    midi.close()

def encoded_to_midi(note_encoded, ts_duration=0.25):
    notes = []
    
    velo = 100
    duration = "16th"
    dots = 0
    
    ts = 0
    for note in note_encoded.split(" "):
        if len(note) == 0:
            continue
        elif note[0] == SIGN_WAIT:
            wait_counter = int(note.split("_")[1])
            ts += wait_counter
            
        elif note[0] == SIGN_NOTE:
            pitch = int(note.split("_")[1])
            note = music21.note.Note(pitch)
            note.duration = music21.duration.Duration(type=duration, dots=dots)
            note.offset = ts * ts_duration
            note.volume.velocity = velo
            notes.append(note)
        
        elif note[0] == SIGN_DUR:
            duration = note.split("_")[1]
            dots = int(note.split("_")[2])
        
        elif note[0] == SIGN_VELO:
            velo = int(note.split("_")[1])
        
        elif note[0] == SIGN_TEMP0:
            if note.split("_")[1] != "": 
                tempo = int(note.split("_")[1])
                
                if tempo > 0: 
                    mark = music21.tempo.MetronomeMark(number=tempo)
                    mark.offset = ts * ts_duration
                    notes.append(mark)
        
    piano = music21.instrument.fromString("Piano")
    notes.insert(0, piano)
    
    piano_stream = music21.stream.Stream(notes)
    main_stream = music21.stream.Stream([piano_stream])

    midi_file = music21.midi.translate.streamToMidiFile(main_stream)
    return midi_file


def midi_parse_notes(midi_stream, sample_freq):
    note_filter = music21.stream.filters.ClassFilter('Note')
    
    events = []
    notes_list = midi_stream.recurse().addFilter(note_filter)
    for note in notes_list:
        pitch = note.pitch.midi
        dur = note.duration.quarterLength
        velo = note.volume.velocity
        
        # Abrunden
        offset = math.floor(note.offset * sample_freq)
        
        events.append((pitch, dur, velo, offset))
        
    return events

def midi_parse_chords(midi_stream, sample_freq):
    chord_filter = music21.stream.filters.ClassFilter('Chord')
    
    events = []
    chords_list = midi_stream.recurse().addFilter(chord_filter)
    for chord in chords_list:
        pitches_in_chord = chord.pitches
        for p in pitches_in_chord:
            pitch = p.midi
            dur = chord.duration.quarterLength
            velo = chord.volume.velocity
            offset = math.floor(chord.offset * sample_freq)
            
            events.append((pitch, dur, velo, offset))
        
    return events

def midi_parse_metronome(midi_stream, sample_freq):
    metro_filter = music21.stream.filters.ClassFilter('MetronomeMark')
    events = []
        
    metro_list = midi_stream.recurse().addFilter(metro_filter)
    for metro in metro_list:
        time = int(metro.number)
        offset = math.floor(metro.offset * sample_freq)
        events.append((time, offset))
        
    return events


def midi_to_notes(midi_stream, sample_freq, transpo_range):
    notes = []
    notes += midi_parse_notes(midi_stream=midi_stream, sample_freq=sample_freq)
    notes += midi_parse_chords(midi_stream=midi_stream, sample_freq=sample_freq)
    
    # Transponieren aller Noten in die gewünschte Lage
    transposed_notes = transpose_notes(notes, transpo_range)
    return transposed_notes
    

def transpose_notes(notes, transpo_range):
    transpos = []
    
    first_key = -math.floor(transpo_range/2)
    last_key = math.ceil(transpo_range/2)
    
    for key in range(first_key, last_key):
        notes_in_key = []
        for n in notes:
            pitch, dur, velo, offset = n
            new_pitch = pitch + key
            notes_in_key.append((new_pitch, dur, velo, offset))
        
        transpos.append(notes_in_key)
        
    return transpos


def midi_to_piano_roll(midi_stream, sample_freq, piano_range, transpo_range, stretching_range):
    # Anzahl time_steps im Piano-Roll berechnen
    time_steps = math.floor(midi_stream.duration.quarterLength * sample_freq) + 1
    
    # Midi-Datei --> Liste mit (pitch, duration, velocity, offset)
    transpos = midi_to_notes(midi_stream=midi_stream, sample_freq=sample_freq, transpo_range=transpo_range)
    
    time_events = midi_parse_metronome(midi_stream=midi_stream, sample_freq=sample_freq)
    time_stretches = stretch_time(time_events=time_events, stretching_range=stretching_range)
    
    piano_roll_notes = notes_to_piano_roll(transpositions=transpos, time_stretches=time_stretches, 
                                          time_steps=time_steps, piano_range=piano_range)
    return piano_roll_notes


def notes_to_piano_roll(transpositions, time_stretches, time_steps, piano_range):
    performances = []
    
    min_pitch, max_pitch = piano_range
    
    for t in range(len(transpositions)):
        for s in range(len(time_stretches)):
            # neue Piano-Roll mit berechneter Größe
            # Zusätzliche Dimension, um am Anfang die Lautstärke und Dauer zu beschreiben
            piano_roll = np.zeros((time_steps, MAX_PITCH + 1, 2))
            
            for note in transpositions[t]:
                pitch, dur, velo, offset = note
                if dur == 0.0:
                    continue
                
                pitch = clamp_pitch(pitch=pitch, max=max_pitch, min=min_pitch)
                
                piano_roll[offset, pitch][0] = clamp_duration(dur)
                piano_roll[offset, pitch][1] = discretize_value(val=velo, bins=32, range_=(MIN_VELO, MAX_VELO))
                                
            for time_events in time_stretches[s]:
                time, offset = time_events
                piano_roll[offset, -1][0] = discretize_value(val=time, bins=100, range_=(MIN_TEMP0, MAX_TEMPO))
                                
            performances.append(piano_roll)
        
    return performances


def stretch_time(time_events, stretching_range):
    stretches = []
    
    slower_time = -math.floor(stretching_range/2)
    faster_time = math.ceil(stretching_range/2)
    
    for stretch_time in range(slower_time, faster_time):
        time_events_in_stretch = []
        for e in time_events:
            time, offset = e
            s_time = time + 0.05 * stretch_time * MAX_TEMPO
            time_events_in_stretch.append((s_time, offset))
            
        stretches.append(time_events_in_stretch)
    
    return stretches

def discretize_value(val, bins, range_):
    min_val, max_val = range_
    
    val = int(max(min_val, val))
    val = int(min(val, max_val))
    
    bin_size = (max_val/bins)
    
    return math.floor(val/bin_size) * bin_size

def clamp_pitch(pitch, max, min):
    while pitch < min:
        pitch += 12
    while pitch >= max:
        pitch -= 12
    
    return pitch


def clamp_duration(dur, max=THREE_DOTTED_BREVE, min=THREE_DOTTED_32ND):
    # falls die gegebene Dauer (dur) höher als das Maximum (3-punktierte Halbe) ist
    if dur > max:
        dur = max
        
    # falls die Dauer kleiner als das Minimum (3-punktierte 32-tel) ist
    if dur < min:
        dur = min
    
    dur_tuple = music21.duration.durationTupleFromQuarterLength(dur)
    
    if dur_tuple.type == "inexpressible":
        duration_clos_type = music21.duration.quarterLengthToClosestType(dur)[0]
        dur = music21.duration.typeToDuration[duration_clos_type]
        
    return dur
