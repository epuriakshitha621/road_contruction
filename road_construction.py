"""
Optimal Road Construction Using Graph Optimization
A graph-based road optimization project using Minimum Spanning Tree (Kruskal's Algorithm).
"""

import matplotlib.pyplot as plt
import networkx as nx
import math
from enum import Enum

class TerrainType(Enum):
    FLAT = (1.0, 'lightgreen', 'Flat Land')
    HILLS = (2.0, 'y', 'Hills')
    FOREST = (3.0, 'darkgreen', 'Forest/Protected')
    MOUNTAIN = (4.0, 'orange', 'Mountain')
    RIVER = (5.0, 'blue', 'River Crossing')
    
    def __init__(self, cost_multiplier, color, label):
        self.cost_multiplier = cost_multiplier
        self.color = color
        self.label = label

class CityNode:
    def __init__(self, id, name, x, y, elevation):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.elevation = elevation

class RoadEdge:
    def __init__(self, node1, node2, terrain):
        self.node1 = node1
        self.node2 = node2
        self.terrain = terrain
        self.distance = self.calculate_distance()
        self.elevation_diff = abs(node1.elevation - node2.elevation)
        self.weight = self.calculate_cost()

    def calculate_distance(self):
        return math.hypot(self.node1.x - self.node2.x, self.node1.y - self.node2.y)

    def calculate_cost(self):
        # Base cost is distance
        base_cost = self.distance
        # Terrain penalty
        terrain_cost = base_cost * self.terrain.cost_multiplier
        # Elevation penalty (steeper slopes cost more)
        slope = self.elevation_diff / self.distance if self.distance > 0 else 0
        elevation_cost = slope * 2  # Scaled for realistic weight distribution
        
        return round(terrain_cost + elevation_cost, 2)

class DisjointSet:
    """Union-Find data structure for Kruskal's algorithm."""
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, item):
        if self.parent[item] == item:
            return item
        else:
            self.parent[item] = self.find(self.parent[item])
            return self.parent[item]

    def union(self, set1, set2):
        root1 = self.find(set1)
        root2 = self.find(set2)

        if root1 != root2:
            # Union by rank
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1
            return True
        return False

class RoadNetwork:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, id1, id2, terrain):
        if id1 in self.nodes and id2 in self.nodes:
            edge = RoadEdge(self.nodes[id1], self.nodes[id2], terrain)
            self.edges.append(edge)

    def kruskal_mst(self):
        """
        Kruskal's Algorithm to find the Minimum Spanning Tree.
        This gives us the optimal road network connecting all cities with minimum cost.
        """
        # Sort edges based on weight (greedy approach)
        sorted_edges = sorted(self.edges, key=lambda edge: edge.weight)
        
        mst = []
        ds = DisjointSet(self.nodes.keys())
        
        for edge in sorted_edges:
            # If adding this road doesn't create a cycle
            if ds.union(edge.node1.id, edge.node2.id):
                mst.append(edge)
                
            # Stop early if we've connected all nodes (V-1 edges)
            if len(mst) == len(self.nodes) - 1:
                break
                
        return mst

    def visualize(self, mst_edges=None):
        G = nx.Graph()
        
        pos = {}
        labels = {}
        
        # Add nodes
        for node_id, node in self.nodes.items():
            G.add_node(node_id)
            pos[node_id] = (node.x, node.y)
            labels[node_id] = f"{node.name}\n(E:{node.elevation})"
            
        # Add all potential edges
        for edge in self.edges:
            G.add_edge(edge.node1.id, edge.node2.id, weight=edge.weight, terrain=edge.terrain)
            
        plt.figure(figsize=(14, 9))
        
        # Draw all nodes
        nx.draw_networkx_nodes(G, pos, node_size=1200, node_color='lightblue', edgecolors='black')
        nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')
        
        # Draw all edges lightly (potential roads)
        all_edges = [(e.node1.id, e.node2.id) for e in self.edges]
        nx.draw_networkx_edges(G, pos, edgelist=all_edges, edge_color='gray', width=1.0, alpha=0.3, style='dotted')
        
        # Highlight MST edges if provided
        if mst_edges:
            mst_edge_list = [(e.node1.id, e.node2.id) for e in mst_edges]
            mst_colors = [e.terrain.color for e in mst_edges]
            
            # Draw the chosen roads
            nx.draw_networkx_edges(G, pos, edgelist=mst_edge_list, edge_color=mst_colors, width=4.0, alpha=0.8)
            
            # Draw edge weights only for the chosen roads for clarity
            edge_labels = {(e.node1.id, e.node2.id): f"{e.weight}" for e in mst_edges}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_weight='bold', font_color='red')

            total_cost = sum(e.weight for e in mst_edges)
            plt.title(f"Optimal Road Construction Network (Kruskal's MST)\nTotal Construction Cost: {total_cost:.2f}", fontsize=16, fontweight='bold')
        else:
            plt.title("Potential Road Network and Terrains", fontsize=16, fontweight='bold')
            
        # Create custom legend for terrain types
        legend_elements = [plt.Line2D([0], [0], color=t.color, lw=4, label=f"{t.label} (Cost x{t.cost_multiplier})") for t in TerrainType]
        legend_elements.append(plt.Line2D([0], [0], color='gray', lw=1, linestyle='dotted', label="Rejected Paths"))
        plt.legend(handles=legend_elements, loc='upper left', title="Map Legend", fontsize=10, title_fontsize=12)
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()

def main():
    network = RoadNetwork()
    
    # 1. Create Vertices (Cities/Junctions)
    # Args: id, name, x, y, elevation
    network.add_node(CityNode(1, "Capital City", 0, 0, 100))
    network.add_node(CityNode(2, "Rivertown", 4, 3, 50))
    network.add_node(CityNode(3, "Mountain Base", 1, 6, 200))
    network.add_node(CityNode(4, "High Peak", 3, 8, 800))
    network.add_node(CityNode(5, "Forest Village", 7, 5, 120))
    network.add_node(CityNode(6, "Plainsville", 8, 0, 80))
    network.add_node(CityNode(7, "Lake Edge", 5, -2, 60))

    # 2. Create Edges (Potential Roads)
    # Args: (id1, id2, TerrainType)
    
    # Roads from Capital City
    network.add_edge(1, 2, TerrainType.RIVER)
    network.add_edge(1, 3, TerrainType.HILLS)
    network.add_edge(1, 6, TerrainType.FLAT)
    network.add_edge(1, 7, TerrainType.FLAT)
    
    # Roads from Rivertown
    network.add_edge(2, 3, TerrainType.HILLS)
    network.add_edge(2, 5, TerrainType.FOREST)
    network.add_edge(2, 6, TerrainType.FLAT)
    
    # Roads around mountains
    network.add_edge(3, 4, TerrainType.MOUNTAIN)
    network.add_edge(3, 5, TerrainType.FOREST)
    network.add_edge(4, 5, TerrainType.MOUNTAIN)
    
    # Eastern roads
    network.add_edge(5, 6, TerrainType.FLAT)
    network.add_edge(6, 7, TerrainType.RIVER)

    print("--- Optimal Road Construction Optimization ---")
    print("Calculating minimum-cost road network...\n")
    
    # 3. Find optimal route using Kruskal's MST
    optimal_roads = network.kruskal_mst()
    
    # 4. Print results
    print("Optimal Roads Selected:")
    print("-" * 50)
    total_cost = 0
    for edge in optimal_roads:
        print(f"✅ {edge.node1.name:15} -> {edge.node2.name:15}")
        print(f"   Terrain: {edge.terrain.label:15} | Base Dist: {edge.distance:.2f} | Elev Diff: {edge.elevation_diff} | Final Cost: {edge.weight}")
        total_cost += edge.weight
    
    print("-" * 50)
    print(f"Total Network Cost: {total_cost:.2f}\n")
    print("Generating visualization... Please close the window to exit.")
    
    # 5. Visualize the result
    network.visualize(optimal_roads)

if __name__ == "__main__":
    main()