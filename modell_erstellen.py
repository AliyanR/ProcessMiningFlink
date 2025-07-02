from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

# Bleibt immer statisch

# Petri-Netz: A → B → C
net = PetriNet("SimpleProcess")

# Orte
p_start = PetriNet.Place("start")
p_ab = PetriNet.Place("p_ab")
p_bc = PetriNet.Place("p_bc")
p_end = PetriNet.Place("end")
net.places.update({p_start, p_ab, p_bc, p_end})

# Transitionen
t_a = PetriNet.Transition("A", "A")
t_b = PetriNet.Transition("B", "B")
t_c = PetriNet.Transition("C", "C")
net.transitions.update({t_a, t_b, t_c})

# Arcs
petri_utils.add_arc_from_to(p_start, t_a, net)
petri_utils.add_arc_from_to(t_a, p_ab, net)
petri_utils.add_arc_from_to(p_ab, t_b, net)
petri_utils.add_arc_from_to(t_b, p_bc, net)
petri_utils.add_arc_from_to(p_bc, t_c, net)
petri_utils.add_arc_from_to(t_c, p_end, net)

# Markierungen
initial_marking = Marking()
initial_marking[p_start] = 1
final_marking = Marking()
final_marking[p_end] = 1

# Export als PNML
pnml_exporter.apply(net, initial_marking, "modell.pnml", final_marking=final_marking)

print("✅ Modell wurde als 'modell.pnml' gespeichert.")
