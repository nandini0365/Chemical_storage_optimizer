from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import io
import base64
import time
import os

app = Flask(__name__)

class ChemicalStorageOptimizer:
    def __init__(self):
        self.chemicals = {}
        self.conflict_graph = nx.Graph()
        self.color_mapping = {}
        self.cabinets = defaultdict(list)
        
    def add_chemical(self, name, hazard_level=1):
        self.chemicals[name] = {'hazard_level': hazard_level}
        self.conflict_graph.add_node(name, hazard_level=hazard_level)
    
    def add_incompatibility(self, chem1, chem2, severity=1):
        self.conflict_graph.add_edge(chem1, chem2, weight=severity)
    
    def greedy_coloring(self):
        colors = {}
        nodes = list(self.conflict_graph.nodes())
        nodes.sort(key=lambda x: self.conflict_graph.degree(x), reverse=True)
        
        for node in nodes:
            neighbor_colors = set()
            for neighbor in self.conflict_graph.neighbors(node):
                if neighbor in colors:
                    neighbor_colors.add(colors[neighbor])
            
            color = 0
            while color in neighbor_colors:
                color += 1
            colors[node] = color
        
        self.color_mapping = colors
        return colors
    
    def welsh_powell_coloring(self):
        colors = {}
        nodes = sorted(self.conflict_graph.nodes(), 
                      key=lambda x: self.conflict_graph.degree(x), 
                      reverse=True)
        
        for node in nodes:
            if node not in colors:
                color = len(colors)
                colors[node] = color
                
                for other_node in nodes:
                    if (other_node not in colors and 
                        not self.conflict_graph.has_edge(node, other_node)):
                        conflict = False
                        for colored_node, colored_color in colors.items():
                            if colored_color == color and self.conflict_graph.has_edge(other_node, colored_node):
                                conflict = True
                                break
                        if not conflict:
                            colors[other_node] = color
        
        self.color_mapping = colors
        return colors
    
    def dsatur_coloring(self):
        colors = {}
        saturation = {node: 0 for node in self.conflict_graph.nodes()}
        uncolored = set(self.conflict_graph.nodes())
        
        while uncolored:
            max_saturation = -1
            selected_node = None
            
            for node in uncolored:
                if saturation[node] > max_saturation:
                    max_saturation = saturation[node]
                    selected_node = node
                elif saturation[node] == max_saturation:
                    if self.conflict_graph.degree(node) > self.conflict_graph.degree(selected_node):
                        selected_node = node
            
            neighbor_colors = set()
            for neighbor in self.conflict_graph.neighbors(selected_node):
                if neighbor in colors:
                    neighbor_colors.add(colors[neighbor])
            
            color = 0
            while color in neighbor_colors:
                color += 1
            
            colors[selected_node] = color
            uncolored.remove(selected_node)
            
            for neighbor in self.conflict_graph.neighbors(selected_node):
                if neighbor in uncolored:
                    neighbor_colors = set()
                    for n_neighbor in self.conflict_graph.neighbors(neighbor):
                        if n_neighbor in colors:
                            neighbor_colors.add(colors[n_neighbor])
                    saturation[neighbor] = len(neighbor_colors)
        
        self.color_mapping = colors
        return colors
    
    def assign_to_cabinets(self):
        """Assign chemicals to storage cabinets based on coloring"""
        self.cabinets = defaultdict(list)
        for chemical, color in self.color_mapping.items():
            self.cabinets[color].append(chemical)
        return self.cabinets
    
    def calculate_metrics(self):
        """Calculate optimization metrics"""
        num_colors = len(set(self.color_mapping.values()))
        num_chemicals = len(self.chemicals)
        num_conflicts = self.conflict_graph.number_of_edges()
        
        safety_violations = 0
        for edge in self.conflict_graph.edges():
            chem1, chem2 = edge
            if self.color_mapping[chem1] == self.color_mapping[chem2]:
                safety_violations += 1
        
        safety_score = 1 - (safety_violations / num_conflicts) if num_conflicts > 0 else 1
        
        # Calculate max cabinet size
        max_cabinet_size = 0
        for chemicals in self.cabinets.values():
            if len(chemicals) > max_cabinet_size:
                max_cabinet_size = len(chemicals)
        
        return {
            'num_cabinets': num_colors,
            'safety_score': safety_score,
            'efficiency': num_chemicals / num_colors if num_colors > 0 else 0,
            'safety_violations': safety_violations,
            'max_cabinet_size': max_cabinet_size
        }
    
    def create_graph_image(self):
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(self.conflict_graph, seed=42)
        
        if self.color_mapping:
            node_colors = [self.color_mapping[node] for node in self.conflict_graph.nodes()]
        else:
            node_colors = ['lightblue'] * len(self.conflict_graph.nodes())
        
        nx.draw(self.conflict_graph, pos, 
                node_color=node_colors, 
                cmap=plt.cm.Set3,
                with_labels=True, 
                node_size=800, 
                font_size=10, 
                font_weight='bold',
                edge_color='gray')
        
        edge_labels = nx.get_edge_attributes(self.conflict_graph, 'weight')
        nx.draw_networkx_edge_labels(self.conflict_graph, pos, edge_labels=edge_labels)
        
        plt.title("Chemical Conflict Graph with Coloring")
        
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        
        return base64.b64encode(img.getvalue()).decode()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
def demo():
    # Create a demo optimization
    optimizer = ChemicalStorageOptimizer()
    
    # Add demo chemicals
    demo_chemicals = [
        ('HCl', 3), ('NaOH', 2), ('Ethanol', 2), 
        ('Acetone', 2), ('H2O2', 3), ('NaCN', 3)
    ]
    
    for chem, hazard in demo_chemicals:
        optimizer.add_chemical(chem, hazard)
    
    # Add demo incompatibilities
    demo_incompatibilities = [
        ('HCl', 'NaOH', 3), ('HCl', 'Ethanol', 1),
        ('NaOH', 'Ethanol', 1), ('Ethanol', 'H2O2', 3),
        ('Acetone', 'H2O2', 3), ('NaCN', 'HCl', 3)
    ]
    
    for chem1, chem2, severity in demo_incompatibilities:
        optimizer.add_incompatibility(chem1, chem2, severity)
    
    # Perform coloring and assign to cabinets
    optimizer.greedy_coloring()
    optimizer.assign_to_cabinets()
    metrics = optimizer.calculate_metrics()
    
    # Create graph image
    graph_image = optimizer.create_graph_image()
    
    return render_template('results.html', 
                         graph_image=graph_image,
                         cabinets=dict(optimizer.cabinets),
                         chemicals=optimizer.chemicals,
                         metrics=metrics,
                         is_demo=True)

@app.route('/results')
def results():
    # This route will be used when coming from custom optimization
    return render_template('results.html', is_demo=False)

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        
        optimizer = ChemicalStorageOptimizer()
        
        # Add chemicals
        for chem in data['chemicals']:
            optimizer.add_chemical(chem['name'], int(chem['hazard']))
        
        # Add incompatibilities
        for conflict in data['incompatibilities']:
            optimizer.add_incompatibility(conflict['chem1'], conflict['chem2'], int(conflict['severity']))
        
        # Test different algorithms
        algorithms = {
            'Greedy Coloring': optimizer.greedy_coloring,
            'Welsh-Powell': optimizer.welsh_powell_coloring,
            'DSATUR': optimizer.dsatur_coloring
        }
        
        results = {}
        
        for algo_name, algo_func in algorithms.items():
            start_time = time.time()
            coloring = algo_func()
            end_time = time.time()
            
            cabinets = optimizer.assign_to_cabinets()
            metrics = optimizer.calculate_metrics()
            
            results[algo_name] = {
                'coloring': coloring,
                'metrics': metrics,
                'time': end_time - start_time,
                'cabinets': dict(optimizer.cabinets)
            }
        
        # Use best algorithm for final result
        best_algo = min(results.keys(), 
                       key=lambda x: (results[x]['metrics']['num_cabinets'], 
                                    -results[x]['metrics']['safety_score']))
        
        best_results = results[best_algo]
        graph_image = optimizer.create_graph_image()
        
        return jsonify({
            'success': True,
            'results': results,
            'best_algorithm': best_algo,
            'graph_image': graph_image,
            'chemicals': optimizer.chemicals
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == "__main__":
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
