import networkx as nx
import matplotlib.pyplot as plt
import pyhepmc as hep
import pyhepmc.io as hepio
from particle import Particle
import matplotlib
import random

# Use LaTeX for rendering text in plots
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

# Read HepMC3 file
filename = './Output_HepMC.dat'
events = hepio.ReaderAscii(filename)

# List available events
event_list = []
event = hep.GenEvent()
while not events.failed():
    events.read_event(event)
    event_list.append(event)
    event = hep.GenEvent()

# Prompt user to choose an event
print("Available events:")
for i, evt in enumerate(event_list):
    print(f"Event {i + 1}")

event_choice = int(input(f"Choose an event (1-{len(event_list) - 1}): ")) - 1
chosen_event = event_list[event_choice]

# Create a graph
G = nx.DiGraph()

# Add vertices and edges with particle names as labels
for vertex in chosen_event.vertices:
    G.add_node(vertex.id, pos=(vertex.position.x, vertex.position.y))
    for particle in vertex.particles_out:
        if particle.end_vertex:
            particle_name = Particle.from_pdgid(particle.pid).latex_name
            G.add_edge(vertex.id, particle.end_vertex.id, name=particle_name)
        else:  # Handle end particles
            particle_name = Particle.from_pdgid(particle.pid).latex_name
            end_vertex_id = f"end_{particle.id}"
            G.add_node(end_vertex_id, pos=(vertex.position.x + random.uniform(2, 3) * random.choice([1, -1]), vertex.position.y + random.uniform(2, 3) * random.choice([1, -1])))
            G.add_edge(vertex.id, end_vertex_id, name=particle_name)

# Add initial particles
for particle in chosen_event.particles:
    if particle.status == 4:  # Status code for initial particles
        start_vertex_id = f"start_{particle.id}"
        G.add_node(start_vertex_id, pos=(random.uniform(2, 3) * random.choice([1, -1]), random.uniform(2, 3) * random.choice([1, -1])))
        particle_name = Particle.from_pdgid(particle.pid).latex_name
        if particle.end_vertex:
            G.add_edge(start_vertex_id, particle.end_vertex.id, name=particle_name)

# Use spectral layout to reduce intersections
pos = nx.spectral_layout(G)

# Add a small random perturbation to each node's position to avoid overlap
is_odd = False
for node in pos:
    rnd = random.uniform(0.1, 0.4)
    if is_odd:
        pos[node][1] += rnd  # Stretch vertically
    else:
        pos[node][1] -= rnd
    is_odd = not is_odd

# Draw the graph
nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_color='black')

# Draw edge labels (particle names)
edge_labels = nx.get_edge_attributes(G, 'name')
edge_labels = {k: f'${v}$' for k, v in edge_labels.items()}  # Ensure LaTeX formatting
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black', font_size=17)

plt.show()
