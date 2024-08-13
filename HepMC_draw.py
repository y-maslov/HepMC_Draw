import networkx as nx
import matplotlib.pyplot as plt
import pyhepmc as hep
import pyhepmc.io as hepio
from particle import Particle
import matplotlib
import random
import numpy as np

# Use LaTeX for rendering text in plots
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

# Read HepMC3 file
filename = './Output_HepMC.dat'
events = hepio.ReaderAscii(filename)

# List available events with their IDs
event_list = []
event_ids = []
event = hep.GenEvent()
while not events.failed():
    events.read_event(event)
    event_list.append(event)
    event_ids.append(event.event_number)
    event = hep.GenEvent()

# Prompt user to choose an event by its actual ID
print("Available events:")
for evt_id in event_ids:
    print(f"Event ID: {evt_id}")

event_choice = int(input(f"Choose an event ID from the list above: "))
chosen_event_index = event_ids.index(event_choice)
chosen_event = event_list[chosen_event_index]

# Create a DiGraph to ensure only one edge per connection
G = nx.DiGraph()

# Add vertices and edges with particle names and PDG codes as labels
for vertex in chosen_event.vertices:
    G.add_node(vertex.id, pos=(vertex.position.x, vertex.position.y))
    for particle in vertex.particles_out:
        particle_name = Particle.from_pdgid(particle.pid).latex_name
        particle_label = f"{particle_name} ({particle.pid})"  # Include PDG code in the label
        if particle.end_vertex:
            # If the edge already exists, concatenate the particle names
            if G.has_edge(vertex.id, particle.end_vertex.id):
                existing_name = G[vertex.id][particle.end_vertex.id]['name']
                G[vertex.id][particle.end_vertex.id]['name'] = f"{existing_name}, {particle_label}"
            else:
                G.add_edge(vertex.id, particle.end_vertex.id, name=particle_label)
        else:
            # Handle particles without an end vertex
            end_vertex_id = f"end_{particle.id}"
            if end_vertex_id not in G:
                G.add_node(end_vertex_id, pos=(vertex.position.x + random.choice([3, 4, 5, 6]) * random.choice([1, -1]), vertex.position.y + random.choice([3, 4, 5, 6]) * random.choice([1, -1])))
            G.add_edge(vertex.id, end_vertex_id, name=particle_label)

# Ensure all start particles are visualized
for particle in chosen_event.particles:
    if particle.status == 4:  # Status code for initial particles
        start_vertex_id = f"start_{particle.id}"
        if start_vertex_id not in G:
            G.add_node(start_vertex_id, pos=(random.choice([3, 4, 5, 6]) * random.choice([1, -1]), random.choice([3, 4, 5, 6]) * random.choice([1, -1])))
        particle_name = Particle.from_pdgid(particle.pid).latex_name
        particle_label = f"{particle_name} ({particle.pid})"  # Include PDG code in the label
        if particle.end_vertex:
            if G.has_edge(start_vertex_id, particle.end_vertex.id):
                existing_name = G[start_vertex_id][particle.end_vertex.id]['name']
                G[start_vertex_id][particle.end_vertex.id]['name'] = f"{existing_name}, {particle_label}"
            else:
                G.add_edge(start_vertex_id, particle.end_vertex.id, name=particle_label)

# Use spectral layout to reduce intersections
pos = nx.spectral_layout(G)

# Draw the graph
fig, ax = plt.subplots()
nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_color='black')

# Draw edge labels with particle names and PDG codes
edge_labels = nx.get_edge_attributes(G, 'name')
edge_labels = {k: f'${v}$' for k, v in edge_labels.items()}  # Ensure LaTeX formatting
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black', font_size=17)

# Connect the event handling functions to the figure for dragging nodes
selected_node = None

def on_press(event):
    global selected_node
    if event.inaxes is not None:
        closest_node, min_dist = None, float('inf')
        for node, (x, y) in pos.items():
            dist = np.hypot(x - event.xdata, y - event.ydata)
            if dist < min_dist:
                closest_node, min_dist = node, dist
        if min_dist < 0.05:  # Adjust threshold for sensitivity
            selected_node = closest_node

def on_release(event):
    global selected_node
    selected_node = None

def on_motion(event):
    if selected_node is not None and event.inaxes is not None:
        pos[selected_node] = np.array([event.xdata, event.ydata])
        plt.cla()
        nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_color='black')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black', font_size=17)
        plt.draw()

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

plt.show()