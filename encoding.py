import numpy as np
import matplotlib.pyplot as plt
from ocpa.visualization.log.variants import factory as variants_visualization_factor
import scipy.cluster.hierarchy as sch
from config import *

# 1. OCEL mit ocpa einlesen
# Annahme: Die ocpa-Funktion liefert ein Dictionary mit den Schlüsseln "events" und "objects"
ocel_log = variants_visualization_factor.apply(P2P_LOG)

ocel_log

# Falls die Struktur anders ist, passen Sie bitte die Zugriffspfade an.
events = ocel_log["events"]
objects = ocel_log["objects"]

# 2. Dictionary der Objekte erstellen (zum schnellen Zugriff per Objekt-ID)
object_dict = {obj["id"]: obj for obj in objects}

# 3. Eindeutige Event-Typen und Objekttypen extrahieren
# Hier wird angenommen, dass im Event der Typ unter "event_type" gespeichert ist
# und in den Objekten der Typ unter "object_type".
event_types = {event["event_type"] for event in events}
object_types = {obj["object_type"] for obj in objects}

# 4. Mappings für die Indizes der einzelnen Typen erstellen
event_type_to_index = {et: idx for idx, et in enumerate(sorted(event_types))}
object_type_to_index = {ot: idx for idx, ot in enumerate(sorted(object_types))}

# 5. Für jedes Event ein kombiniertes Encoding erstellen:
#    - One-Hot für den Event-Typ
#    - Multi-Hot für alle beteiligten Objekttypen (unter Annahme, dass die Event-Objekt-Verknüpfung über "object_ids" erfolgt)
event_encodings = []
for event in events:
    # One-Hot Encoding für den Event-Typ
    event_vector = np.zeros(len(event_type_to_index))
    event_vector[event_type_to_index[event["event_type"]]] = 1

    # Multi-Hot Encoding für die Objekttypen (über alle zugehörigen Objekt-IDs)
    object_vector = np.zeros(len(object_type_to_index))
    for obj_id in event.get("object_ids", []):
        obj = object_dict.get(obj_id)
        if obj:
            object_vector[object_type_to_index[obj["object_type"]]] = 1

    # Kombination der beiden Vektoren (z.B. durch Konkatenation)
    combined_vector = np.concatenate([event_vector, object_vector])
    event_encodings.append(combined_vector)

# 6. Encodings in ein NumPy-Array konvertieren (jede Zeile entspricht einem Event)
X = np.array(event_encodings)

# 7. Hierarchisches Clustering durchführen (z. B. mit Ward-Verfahren)
Z = sch.linkage(X, method='ward')

# 8. Dendrogramm plotten
plt.figure(figsize=(10, 7))
dendro = sch.dendrogram(Z)
plt.title("Hierarchisches Clustering Dendrogramm")
plt.xlabel("Events")
plt.ylabel("Distanz")
plt.show()
