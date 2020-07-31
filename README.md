# The Art of Sentiment

KI-Projekt im Rahmen des [Bundeswettbewerb "Künstliche Intelligenz"](https://bw-ki.de/) 2020.

## Beschreibung der Idee
Unsere Idee ist es, eine KI so zu trainieren, dass diese Musik komponiert, welche zu einer im Text, Foto oder auch im Video dargestellten Gefühlslage passt.

## Vorgehensweise
Für unser Projekt brauchen wir Fotodateien denen ein menschliches Gefühl zugeordnet ist um unsere KI trainieren zu können. Hierdurch sollte die KI dann selbstständig anderen Fotos ein Gefühl zuweisen können und die passende Musik dazu komponieren. Damit die KI die passende Musik komponieren kann muss sie mit Tonspuren trainiert werden, denen ein Genre, die jeweilige Lautstärke, die Geschwindigkeit und das beim Menschen erzeugte Gefühl zugeordnet ist.

## Datensätze
### Folgende Datensätze werden voraussichtlich verwendet:

*   Analyse der Gefühlslage des eingegebenen Textes:

    https://www.kaggle.com/kazanova/sentiment140 (1,6 Millionen englische Twitter-Beiträge)
    
    https://www.kaggle.com/iwilldoit/emotions-sensor-data-set (englische Wörter mit entsprechender Gefühlslage)

----

*   Analyse der Emotionen von Musik:

    https://github.com/HuiZhangDB/PMEmo 

    https://www.kaggle.com/uwrfkaggler/ravdess-emotional-song-audio? (Emotionen von Sprache und Gesang)

    https://www.jyu.fi/hytk/fi/laitokset/mutku/en/research/projects2/past-projects/coe/materials/emotion/soundtracks/Index (Antrag für Download muss noch gestellt werden)

    https://github.com/mdeff/fma 

----

*   Trainieren einer KI auf Musik:
    
    https://bitmidi.com/
    
    https://www.classicalarchives.com/

