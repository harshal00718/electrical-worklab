import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon
import io
import json
from datetime import datetime
import random
import math

# Page configuration
st.set_page_config(
    page_title="Electronics Workbench",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced components with electrical symbols and parameters
COMPONENTS = {
    "Resistor": {
        "symbol": "zigzag", 
        "params": {"resistance": 1000.0, "power_rating": 0.25, "tolerance": 5.0}, 
        "units": {"resistance": "Ω", "power_rating": "W", "tolerance": "%"},
        "color": "brown"
    },
    "Capacitor": {
        "symbol": "capacitor", 
        "params": {"capacitance": 100e-6, "voltage_rating": 25.0, "type": "Ceramic"}, 
        "units": {"capacitance": "F", "voltage_rating": "V", "type": ""},
        "color": "blue"
    },
    "Inductor": {
        "symbol": "inductor", 
        "params": {"inductance": 1e-3, "current_rating": 1.0, "resistance": 0.1}, 
        "units": {"inductance": "H", "current_rating": "A", "resistance": "Ω"},
        "color": "green"
    },
    "Diode": {
        "symbol": "diode", 
        "params": {"forward_voltage": 0.7, "max_current": 1.0, "reverse_voltage": 50.0}, 
        "units": {"forward_voltage": "V", "max_current": "A", "reverse_voltage": "V"},
        "color": "red"
    },
    "LED": {
        "symbol": "led", 
        "params": {"forward_voltage": 2.0, "forward_current": 0.02, "color": "Red"}, 
        "units": {"forward_voltage": "V", "forward_current": "A", "color": ""},
        "color": "orange"
    },
    "Transistor (NPN)": {
        "symbol": "transistor_npn", 
        "params": {"beta": 100.0, "vbe": 0.7, "vce_sat": 0.2}, 
        "units": {"beta": "", "vbe": "V", "vce_sat": "V"},
        "color": "purple"
    },
    "Battery": {
        "symbol": "battery", 
        "params": {"voltage": 9.0, "capacity": 1000.0, "internal_resistance": 0.1}, 
        "units": {"voltage": "V", "capacity": "mAh", "internal_resistance": "Ω"},
        "color": "black"
    },
    "AC Source": {
        "symbol": "ac_source", 
        "params": {"voltage_rms": 120.0, "frequency": 50.0, "phase": 0.0}, 
        "units": {"voltage_rms": "V", "frequency": "Hz", "phase": "°"},
        "color": "cyan"
    },
    "Ground": {
        "symbol": "ground", 
        "params": {}, 
        "units": {},
        "color": "gray"
    },
    "Switch": {
        "symbol": "switch", 
        "params": {"state": "Open", "contact_resistance": 0.01}, 
        "units": {"state": "", "contact_resistance": "Ω"},
        "color": "yellow"
    },
    "Ammeter": {
        "symbol": "ammeter", 
        "params": {"range": 1.0, "reading": 0.0, "accuracy": 1.0}, 
        "units": {"range": "A", "reading": "A", "accuracy": "%"},
        "color": "darkgreen"
    },
    "Voltmeter": {
        "symbol": "voltmeter", 
        "params": {"range": 10.0, "reading": 0.0, "accuracy": 1.0}, 
        "units": {"range": "V", "reading": "V", "accuracy": "%"},
        "color": "darkblue"
    },
    "Load": {
        "symbol": "load", 
        "params": {"power": 100.0, "voltage": 12.0, "type": "Resistive"}, 
        "units": {"power": "W", "voltage": "V", "type": ""},
        "color": "maroon"
    }
}

# Initialize session state
if 'circuit_components' not in st.session_state:
    st.session_state.circuit_components = []
if 'connections' not in st.session_state:
    st.session_state.connections = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'component_counter' not in st.session_state:
    st.session_state.component_counter = 0

def create_component_symbol(ax, comp_type, x, y, comp_id, params):
    """Draw electrical symbols on matplotlib axis"""
    symbol_type = COMPONENTS[comp_type]["symbol"]
    color = COMPONENTS[comp_type]["color"]
    
    if symbol_type == "zigzag":  # Resistor
        # Zigzag pattern
        zigzag_x = np.linspace(x-0.3, x+0.3, 7)
        zigzag_y = y + 0.1 * np.array([0, 1, -1, 1, -1, 1, 0])
        ax.plot(zigzag_x, zigzag_y, color=color, linewidth=2)
        # Connection lines
        ax.plot([x-0.5, x-0.3], [y, y], color='black', linewidth=1)
        ax.plot([x+0.3, x+0.5], [y, y], color='black', linewidth=1)
        # Add resistance value
        ax.text(x, y-0.2, f"{params.get('resistance', 0):.0f}Ω", ha='center', fontsize=8)
        
    elif symbol_type == "capacitor":  # Capacitor
        # Two parallel lines
        ax.plot([x-0.05, x-0.05], [y-0.2, y+0.2], color=color, linewidth=3)
        ax.plot([x+0.05, x+0.05], [y-0.2, y+0.2], color=color, linewidth=3)
        # Connection lines
        ax.plot([x-0.3, x-0.05], [y, y], color='black', linewidth=1)
        ax.plot([x+0.05, x+0.3], [y, y], color='black', linewidth=1)
        # Add capacitance value
        cap_val = params.get('capacitance', 0)
        if cap_val >= 1e-6:
            ax.text(x, y-0.2, f"{cap_val*1e6:.0f}µF", ha='center', fontsize=8)
        else:
            ax.text(x, y-0.2, f"{cap_val*1e9:.0f}nF", ha='center', fontsize=8)
    
    elif symbol_type == "inductor":  # Inductor
        # Coil representation using arcs
        for i in range(4):
            circle = Circle((x-0.15+i*0.1, y), 0.05, fill=False, color=color, linewidth=2)
            circle.set_clip_box(ax.bbox)
            ax.add_patch(circle)
        # Connection lines
        ax.plot([x-0.3, x-0.2], [y, y], color='black', linewidth=1)
        ax.plot([x+0.2, x+0.3], [y, y], color='black', linewidth=1)
        # Add inductance value
        ind_val = params.get('inductance', 0)
        if ind_val >= 1e-3:
            ax.text(x, y-0.2, f"{ind_val*1e3:.0f}mH", ha='center', fontsize=8)
        else:
            ax.text(x, y-0.2, f"{ind_val*1e6:.0f}µH", ha='center', fontsize=8)
    
    elif symbol_type == "diode":  # Diode
        # Triangle and line
        triangle = Polygon([(x-0.1, y-0.1), (x-0.1, y+0.1), (x+0.05, y)], 
                          closed=True, fill=True, color=color)
        ax.add_patch(triangle)
        ax.plot([x+0.05, x+0.05], [y-0.15, y+0.15], color=color, linewidth=3)
        # Connection lines
        ax.plot([x-0.3, x-0.1], [y, y], color='black', linewidth=1)
        ax.plot([x+0.05, x+0.3], [y, y], color='black', linewidth=1)
    
    elif symbol_type == "led":  # LED
        # Diode with arrows
        triangle = Polygon([(x-0.1, y-0.1), (x-0.1, y+0.1), (x+0.05, y)], 
                          closed=True, fill=True, color=color)
        ax.add_patch(triangle)
        ax.plot([x+0.05, x+0.05], [y-0.15, y+0.15], color=color, linewidth=3)
        # LED arrows
        ax.arrow(x+0.1, y-0.15, 0.05, -0.05, head_width=0.02, head_length=0.02, fc=color, ec=color)
        ax.arrow(x+0.15, y-0.1, 0.05, -0.05, head_width=0.02, head_length=0.02, fc=color, ec=color)
        # Connection lines
        ax.plot([x-0.3, x-0.1], [y, y], color='black', linewidth=1)
        ax.plot([x+0.05, x+0.3], [y, y], color='black', linewidth=1)
    
    elif symbol_type == "transistor_npn":  # NPN Transistor
        # Base line
        ax.plot([x-0.1, x-0.1], [y-0.2, y+0.2], color=color, linewidth=3)
        # Collector and emitter lines
        ax.plot([x-0.1, x+0.1], [y+0.05, y+0.2], color=color, linewidth=2)
        ax.plot([x-0.1, x+0.1], [y-0.05, y-0.2], color=color, linewidth=2)
        # Arrow on emitter
        ax.arrow(x+0.05, y-0.15, 0.03, -0.03, head_width=0.02, head_length=0.02, fc='black', ec='black')
        # Connection points
        ax.plot([x-0.3, x-0.1], [y, y], color='black', linewidth=1)  # Base
        ax.plot([x+0.1, x+0.3], [y+0.2, y+0.2], color='black', linewidth=1)  # Collector
        ax.plot([x+0.1, x+0.3], [y-0.2, y-0.2], color='black', linewidth=1)  # Emitter
    
    elif symbol_type == "battery":  # Battery
        # Long and short lines
        ax.plot([x-0.05, x-0.05], [y-0.2, y+0.2], color=color, linewidth=4)
        ax.plot([x+0.05, x+0.05], [y-0.15, y+0.15], color=color, linewidth=2)
        # Connection lines
        ax.plot([x-0.3, x-0.05], [y, y], color='black', linewidth=1)
        ax.plot([x+0.05, x+0.3], [y, y], color='black', linewidth=1)
        # Voltage label
        ax.text(x, y-0.3, f"{params.get('voltage', 0):.1f}V", ha='center', fontsize=8)
        # Polarity marks
        ax.text(x-0.05, y+0.25, '+', ha='center', fontsize=10, weight='bold')
        ax.text(x+0.05, y+0.25, '-', ha='center', fontsize=10, weight='bold')
    
    elif symbol_type == "ac_source":  # AC Source
        # Circle
        circle = Circle((x, y), 0.15, fill=False, color=color, linewidth=2)
        ax.add_patch(circle)
        # Sine wave inside
        t = np.linspace(-np.pi, np.pi, 50)
        sine_x = x + 0.1 * t / np.pi
        sine_y = y + 0.08 * np.sin(2*t)
        ax.plot(sine_x, sine_y, color=color, linewidth=1)
        # Connection lines
        ax.plot([x-0.3, x-0.15], [y, y], color='black', linewidth=1)
        ax.plot([x+0.15, x+0.3], [y, y], color='black', linewidth=1)
        # Voltage and frequency labels
        ax.text(x, y-0.3, f"{params.get('voltage_rms', 0):.0f}V", ha='center', fontsize=8)
        ax.text(x, y-0.4, f"{params.get('frequency', 0):.0f}Hz", ha='center', fontsize=8)
    
    elif symbol_type == "ground":  # Ground
        ax.plot([x, x], [y, y-0.15], color=color, linewidth=2)
        ax.plot([x-0.15, x+0.15], [y-0.15, y-0.15], color=color, linewidth=3)
        ax.plot([x-0.1, x+0.1], [y-0.2, y-0.2], color=color, linewidth=2)
        ax.plot([x-0.05, x+0.05], [y-0.25, y-0.25], color=color, linewidth=1)
    
    elif symbol_type == "switch":  # Switch
        # Connection points
        ax.plot([x-0.3, x-0.1], [y, y], color='black', linewidth=1)
        ax.plot([x+0.1, x+0.3], [y, y], color='black', linewidth=1)
        # Switch blade
        if params.get("state") == "Open":
            ax.plot([x-0.1, x+0.05], [y, y+0.1], color=color, linewidth=2)
        else:
            ax.plot([x-0.1, x+0.1], [y, y], color=color, linewidth=2)
        # Contact points
        contact1 = Circle((x-0.1, y), 0.02, fill=True, color='black')
        contact2 = Circle((x+0.1, y), 0.02, fill=True, color='black')
        ax.add_patch(contact1)
        ax.add_patch(contact2)
    
    elif symbol_type in ["ammeter", "voltmeter"]:  # Meters
        # Circle
        circle = Circle((x, y), 0.15, fill=False, color=color, linewidth=2)
        ax.add_patch(circle)
        # Letter inside
        letter = "A" if symbol_type == "ammeter" else "V"
        ax.text(x, y, letter, ha='center', va='center', fontsize=12, weight='bold')
        # Connection lines
        ax.plot([x-0.3, x-0.15], [y, y], color='black', linewidth=1)
        ax.plot([x+0.15, x+0.3], [y, y], color='black', linewidth=1)
        # Reading
        reading = params.get('reading', 0)
        ax.text(x, y-0.25, f"{reading:.3f}{letter}", ha='center', fontsize=8)
    
    elif symbol_type == "load":  # Load
        # Rectangle
        rect = Rectangle((x-0.1, y-0.08), 0.2, 0.16, fill=False, color=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, 'LOAD', ha='center', va='center', fontsize=8, weight='bold')
        # Connection lines
        ax.plot([x-0.3, x-0.1], [y, y], color='black', linewidth=1)
        ax.plot([x+0.1, x+0.3], [y, y], color='black', linewidth=1)
        # Power rating
        ax.text(x, y-0.2, f"{params.get('power', 0):.0f}W", ha='center', fontsize=8)
    
    # Add component label
    ax.text(x, y+0.35, f"{comp_type} ({comp_id})", ha='center', fontsize=8, weight='bold')

def draw_circuit():
    """Draw the complete circuit diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(-1, 10)
    ax.set_ylim(-1, 6)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('Circuit Diagram', fontsize=16, weight='bold')
    
    # Draw components
    for comp in st.session_state.circuit_components:
        create_component_symbol(ax, comp['type'], comp['x'], comp['y'], comp['id'], comp['params'])
    
    # Draw connections
    for conn in st.session_state.connections:
        comp1 = next(c for c in st.session_state.circuit_components if c['id'] == conn['from_comp'])
        comp2 = next(c for c in st.session_state.circuit_components if c['id'] == conn['to_comp'])
        
        # Simple straight line connection
        ax.plot([comp1['x']+0.3, comp2['x']-0.3], [comp1['y'], comp2['y']], 
               color='red', linewidth=2, alpha=0.7)
        
        # Add connection points
        ax.plot(comp1['x']+0.3, comp1['y'], 'ro', markersize=4)
        ax.plot(comp2['x']-0.3, comp2['y'], 'ro', markersize=4)
    
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    
    return fig

def calculate_circuit_parameters():
    """Perform basic circuit analysis"""
    results = {
        'total_resistance': 0,
        'total_capacitance': 0,
        'total_inductance': 0,
        'voltage_sources': [],
        'power_consumption': 0,
        'component_analysis': []
    }
    
    # Analyze each component
    for comp in st.session_state.circuit_components:
        comp_analysis = {
            'id': comp['id'],
            'type': comp['type'],
            'parameters': comp['params'].copy()
        }
        
        if comp['type'] == 'Resistor':
            resistance = comp['params'].get('resistance', 0)
            results['total_resistance'] += resistance
            # Calculate power dissipation (assuming some current)
            current = 0.001  # Assume 1mA for demonstration
            power = current**2 * resistance
            comp_analysis['calculated'] = {
                'power_dissipated': power,
                'voltage_drop': current * resistance
            }
        
        elif comp['type'] == 'Capacitor':
            capacitance = comp['params'].get('capacitance', 0)
            if capacitance > 0:
                results['total_capacitance'] += capacitance
            comp_analysis['calculated'] = {
                'energy_stored': 0.5 * capacitance * (comp['params'].get('voltage_rating', 0)**2),
                'reactance_60hz': 1/(2*np.pi*60*capacitance) if capacitance > 0 else float('inf')
            }
        
        elif comp['type'] == 'Inductor':
            inductance = comp['params'].get('inductance', 0)
            results['total_inductance'] += inductance
            comp_analysis['calculated'] = {
                'energy_stored': 0.5 * inductance * (comp['params'].get('current_rating', 0)**2),
                'reactance_60hz': 2*np.pi*60*inductance
            }
        
        elif comp['type'] in ['Battery', 'AC Source']:
            voltage = comp['params'].get('voltage', 0) or comp['params'].get('voltage_rms', 0)
            results['voltage_sources'].append(voltage)
            comp_analysis['calculated'] = {
                'max_power': voltage**2 / comp['params'].get('internal_resistance', 1)
            }
        
        elif comp['type'] == 'Load':
            power = comp['params'].get('power', 0)
            results['power_consumption'] += power
            voltage = comp['params'].get('voltage', 0)
            if voltage > 0:
                current = power / voltage
                resistance = voltage / current if current > 0 else float('inf')
                comp_analysis['calculated'] = {
                    'current': current,
                    'resistance': resistance
                }
        
        results['component_analysis'].append(comp_analysis)
    
    # Overall circuit calculations
    if results['voltage_sources'] and results['total_resistance'] > 0:
        total_voltage = sum(results['voltage_sources'])
        circuit_current = total_voltage / results['total_resistance']
        results['circuit_current'] = circuit_current
        results['total_power'] = total_voltage * circuit_current
    
    return results

def main():
    st.title("🔧 Enhanced Electronics Workbench")
    st.markdown("### Circuit Analysis Tool for Electrical Engineering Students")
    
    # Sidebar for component selection and tools
    with st.sidebar:
        st.header("🔨 Tools & Components")
        
        # Component addition section
        st.subheader("Add Components")
        selected_component = st.selectbox("Select Component:", list(COMPONENTS.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            x_pos = st.number_input("X Position:", min_value=0.0, max_value=9.0, value=2.0, step=0.5)
        with col2:
            y_pos = st.number_input("Y Position:", min_value=0.0, max_value=5.0, value=2.0, step=0.5)
        
        if st.button("➕ Add Component"):
            st.session_state.component_counter += 1
            new_component = {
                'id': st.session_state.component_counter,
                'type': selected_component,
                'x': x_pos,
                'y': y_pos,
                'params': COMPONENTS[selected_component]['params'].copy()
            }
            st.session_state.circuit_components.append(new_component)
            st.success(f"Added {selected_component} to circuit!")
        
        st.divider()
        
        # Connection section
        st.subheader("Create Connections")
        if len(st.session_state.circuit_components) >= 2:
            comp_options = [f"{c['type']} ({c['id']})" for c in st.session_state.circuit_components]
            from_comp = st.selectbox("From Component:", comp_options, key="from_comp")
            to_comp = st.selectbox("To Component:", comp_options, key="to_comp")
            
            if st.button("🔌 Connect Components"):
                from_id = int(from_comp.split('(')[1].split(')')[0])
                to_id = int(to_comp.split('(')[1].split(')')[0])
                
                if from_id != to_id:
                    connection = {'from_comp': from_id, 'to_comp': to_id}
                    if connection not in st.session_state.connections:
                        st.session_state.connections.append(connection)
                        st.success("Connection created!")
                    else:
                        st.warning("Connection already exists!")
                else:
                    st.error("Cannot connect component to itself!")
        else:
            st.info("Add at least 2 components to create connections")
        
        st.divider()
        
        # Circuit management
        st.subheader("Circuit Management")
        if st.button("🧹 Clear Circuit"):
            st.session_state.circuit_components = []
            st.session_state.connections = []
            st.session_state.component_counter = 0
            st.success("Circuit cleared!")
        
        if st.button("🔍 Analyze Circuit"):
            if st.session_state.circuit_components:
                st.session_state.analysis_results = calculate_circuit_parameters()
                st.success("Analysis complete!")
            else:
                st.error("Add components to analyze!")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Circuit Diagram")
        if st.session_state.circuit_components:
            fig = draw_circuit()
            st.pyplot(fig)
            plt.close()  # Prevent memory issues
        else:
            st.info("Add components to see the circuit diagram")
        
        # Component parameters editing
        if st.session_state.circuit_components:
            st.subheader("Component Parameters")
            selected_comp_for_edit = st.selectbox(
                "Select component to edit:",
                [f"{c['type']} ({c['id']})" for c in st.session_state.circuit_components],
                key="edit_comp"
            )
            
            if selected_comp_for_edit:
                comp_id = int(selected_comp_for_edit.split('(')[1].split(')')[0])
                component = next(c for c in st.session_state.circuit_components if c['id'] == comp_id)
                
                st.write(f"Editing: **{component['type']} ({component['id']})**")
                
                # Create input fields for each parameter
                new_params = {}
                for param, value in component['params'].items():
                    unit = COMPONENTS[component['type']]['units'].get(param, '')
                    
                    if isinstance(value, str):
                        new_params[param] = st.text_input(f"{param.replace('_', ' ').title()}", value=value)
                    elif isinstance(value, bool):
                        new_params[param] = st.checkbox(f"{param.replace('_', ' ').title()}", value=value)
                    else:
                        new_params[param] = st.number_input(
                            f"{param.replace('_', ' ').title()} ({unit})",
                            value=float(value),
                            format="%.6f"
                        )
                
                if st.button("💾 Update Parameters"):
                    component['params'] = new_params
                    st.success("Parameters updated!")
                    st.experimental_rerun()
    
    with col2:
        st.subheader("Circuit Analysis")
        
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # Summary metrics
            st.metric("Total Components", len(st.session_state.circuit_components))
            st.metric("Total Connections", len(st.session_state.connections))
            
            if results.get('total_resistance', 0) > 0:
                st.metric("Total Resistance", f"{results['total_resistance']:.2f} Ω")
            
            if results.get('circuit_current'):
                st.metric("Circuit Current", f"{results['circuit_current']:.6f} A")
            
            if results.get('total_power'):
                st.metric("Total Power", f"{results['total_power']:.6f} W")
            
            # Detailed analysis
            with st.expander("Detailed Component Analysis"):
                for comp_data in results['component_analysis']:
                    st.write(f"**{comp_data['type']} ({comp_data['id']})**")
                    
                    # Parameters
                    st.write("Parameters:")
                    for param, value in comp_data['parameters'].items():
                        unit = COMPONENTS[comp_data['type']]['units'].get(param, '')
                        if isinstance(value, float):
                            st.write(f"  - {param.replace('_', ' ').title()}: {value:.6f} {unit}")
                        else:
                            st.write(f"  - {param.replace('_', ' ').title()}: {value} {unit}")
                    
                    # Calculated values
                    if 'calculated' in comp_data:
                        st.write("Calculated:")
                        for calc, value in comp_data['calculated'].items():
                            if isinstance(value, float):
                                st.write(f"  - {calc.replace('_', ' ').title()}: {value:.6f}")
                            else:
                                st.write(f"  - {calc.replace('_', ' ').title()}: {value}")
                    
                    st.divider()
        
        # Export functionality
        st.subheader("Export Data")
        
        if st.button("📊 Generate CSV Report"):
            if st.session_state.circuit_components:
                # Prepare data for CSV
                csv_data = []
                
                # Component data
                for comp in st.session_state.circuit_components:
                    row = {
                        'Component_ID': comp['id'],
                        'Component_Type': comp['type'],
                        'X_Position': comp['x'],
                        'Y_Position': comp['y']
                    }
                    
                    # Add parameters
                    for param, value in comp['params'].items():
                        unit = COMPONENTS[comp['type']]['units'].get(param, '')
                        row[f'{param}_{unit}'.replace(' ', '_')] = value
                    
                    # Add calculated values if analysis was performed
                    if st.session_state.analysis_results:
                        comp_analysis = next(ca for ca in st.session_state.analysis_results['component_analysis']) 