import numpy as np
from qiskit import Aer, execute
from qiskit.visualization import plot_bloch_vector
from qiskit.visualization.bloch import Bloch

from qiskit.circuit import ParameterVector, Parameter

from qiskit_machine_learning.algorithms import QSVC
from qiskit_machine_learning.kernels import FidelityQuantumKernel


import matplotlib.pyplot as plt
import plotly.graph_objects as go

import seaborn as sns

class_A_color = '#636EFA'
class_B_color = '#EF553B'
good_color = '#00CC96'
bad_color = '#EF553B'
black_color = '#000000'
bloch_sphere_color = '#C0C0C0'

def bloch_sphere_statevector_figure(statevectors = None,data_ys = None):
    """Credits to Maxime Dion <maxime.dion@usherbrooke.ca>"""
    r = 0.98
    u, v = np.mgrid[0:2*np.pi:100j, 0:np.pi:100j]
    sphere_x = r * np.sin(v) * np.cos(u)
    sphere_y = r * np.sin(v) * np.sin(u)
    sphere_z = r * np.cos(v)

    fig = go.FigureWidget()

    surfacecolor = np.zeros(shape=sphere_x.shape) 
    colorscale = [[0, bloch_sphere_color], 
              [1, bloch_sphere_color]]

    bloch_surface = go.Surface(
        x=sphere_x, y=sphere_y, z=sphere_z, surfacecolor = surfacecolor,
        colorscale=colorscale,
        name = 'Sphere', 
        showscale=False,
        opacity=0.5,
        lighting=dict(ambient=1),
        )

    axis_dots_xyzs = np.array([[r,0,0],[0,r,0],[0,0,r],[-r,0,0],[0,-r,0],[0,0,-r]])

    theta = 2*np.pi*np.linspace(0,1)
    cos_t = r*np.cos(theta)
    sin_t = r*np.sin(theta)
    zero_t = np.zeros(theta.shape)
    traces_mesh = list()
    traces_mesh.append( 
        go.Scatter3d(x=cos_t, y=sin_t, z=zero_t,
        name = 'xy plane',mode='lines',showlegend=False,line=dict(color=black_color,width=2))
        )
    traces_mesh.append( 
        go.Scatter3d(y=cos_t, z=sin_t, x=zero_t,
            name = 'yz plane',mode='lines',showlegend=False,line=dict(color=black_color,width=2))
        )
    traces_mesh.append( 
        go.Scatter3d(z=cos_t, x=sin_t, y=zero_t,
            name = 'zx plane',mode='lines',showlegend=False,line=dict(color=black_color,width=2))
        )
    traces_mesh.append( 
        go.Scatter3d(x=[0,0], y=[0,0], z=[-r,r],
            name = 'z axis',mode='lines',showlegend=False,line=dict(color=black_color,width=2))
        )
    traces_mesh.append( 
        go.Scatter3d(y=[0,0], z=[0,0], x=[-r,r],
            name = 'x axis',mode='lines',showlegend=False,line=dict(color=black_color,width=2))
        )
    traces_mesh.append( 
        go.Scatter3d(z=[0,0], x=[0,0], y=[-r,r],
            name = 'y axis',mode='lines',showlegend=False,line=dict(color=black_color,width=2))
        )
    traces_mesh.append( 
        go.Scatter3d(x=np.sqrt(0.5)*sin_t, y=np.sqrt(0.5)*sin_t, z=cos_t,
            name = 'x-y plane',mode='lines',showlegend=False,line=dict(color=black_color,width=1))
        )
    traces_mesh.append( 
        go.Scatter3d(x=np.sqrt(0.5)*sin_t, y=-np.sqrt(0.5)*sin_t, z=cos_t,
            name = 'x+y plane',mode='lines',showlegend=False,line=dict(color=black_color,width=1))
        )

    if statevectors is not None:

        xyzs = statevectors_to_xyzs(statevectors)

        mask_a = data_ys == 0
        trace_a = go.Scatter3d(
            x=xyzs[mask_a,0], y=xyzs[mask_a,1], z=xyzs[mask_a,2],
            name = 'A', 
            mode='markers',
            marker=dict(color=class_A_color, size=8, showscale=False)
            )

        mask_b = data_ys == 1
        trace_b = go.Scatter3d(
            x=xyzs[mask_b,0], y=xyzs[mask_b,1], z=xyzs[mask_b,2],
            name = 'B', 
            mode='markers',
            marker=dict(color=class_B_color, size=8, showscale=False)
            )

    trace_axis_dots = go.Scatter3d(
        x=axis_dots_xyzs[:,0], y=axis_dots_xyzs[:,1], z=axis_dots_xyzs[:,2], 
        mode='markers+text',showlegend=False,
        marker=dict(color=black_color, size=4, showscale=False)
        )
    
    scale_outside = 1.15
    trace_axis_labels = go.Scatter3d(
        x=scale_outside*axis_dots_xyzs[:,0], y=scale_outside*axis_dots_xyzs[:,1], z=scale_outside*axis_dots_xyzs[:,2], 
        mode='text',showlegend=False,
        text = ['X','Y','|0>','-X','-Y','|1>'],
        textposition = "middle center",
        textfont = dict(size=20),
        marker=dict(color=black_color, size=4, showscale=False)
        )

    fig.add_trace(bloch_surface)
    for trace in traces_mesh:
        fig.add_trace(trace)

    fig.add_trace(trace_axis_dots)
    if statevectors is not None:
        fig.add_trace(trace_a)
        fig.add_trace(trace_b)

    fig.add_trace(trace_axis_labels)

    max_lim = 1.2
    fig.update_layout(
        legend=dict(
            x=0,y=.5,
            traceorder="normal",
            font=dict(family="sans-serif",size=20,color="black"),
        ),
        height=500,width=500,
        margin=dict(l=0, r=0, b=0, t=0),
        )

    fig.update_scenes(
        aspectratio=dict(x=1, y=1, z=1),
        xaxis = dict(nticks=4, range=[-max_lim,max_lim],),
        yaxis = dict(nticks=4, range=[-max_lim,max_lim],),
        zaxis = dict(nticks=4, range=[-max_lim,max_lim],),
        xaxis_visible=False, yaxis_visible=False,zaxis_visible=False
        )

    return fig

def statevectors_to_xyzs(statevectors):
    """Credits to Maxime Dion <maxime.dion@usherbrooke.ca>"""
    
    phis = np.angle(statevectors[:,1]) - np.angle(statevectors[:,0])
    thetas = np.arccos(np.abs(statevectors[:,0])) + np.arcsin(np.abs(statevectors[:,1]))
    xyzs = np.zeros((statevectors.shape[0],3))
    xyzs[:,0] = np.sin(thetas) * np.cos(phis)
    xyzs[:,1] = np.sin(thetas) * np.sin(phis)
    xyzs[:,2] = np.cos(thetas)

    return xyzs


def plot_decision_boundary(model, X, y, pad=1):
    x_min, x_max = X[:, 0].min() - pad, X[:, 0].max() + pad
    y_min, y_max = X[:, 1].min() - pad, X[:, 1].max() + pad
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))

    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    cmap = plt.cm.RdBu
    plt.contourf(xx, yy, Z, alpha=0.4, cmap=cmap)
    plt.scatter(X[:, 0], X[:, 1], c=y, alpha=0.8, cmap=cmap)
    plt.show()


def statevectors_for_circuit(circuit, data):
    backend = Aer.get_backend('statevector_simulator')
    n_circuits = data.shape[0]
    statevectors = np.zeros((n_circuits,2),dtype = complex)
    for i in range(n_circuits):

        feature_map = circuit.assign_parameters((data[i,0], data[i,1]))
        # Run the quantum circuit on a statevector simulator backend
        job = backend.run(feature_map)
        result = job.result()
        outputstate = result.get_statevector(feature_map, decimals=3)
        statevectors[i,:] = outputstate
    
    return statevectors
        
def plot_kernel_matrix(X_train, y_train, data_encoding_circuit):

    X_train_class_0 = [x for x, y in zip(X_train, y_train) if y == 0]
    X_train_class_1 = [x for x, y in zip(X_train, y_train) if y == 1]
    X_train_sorted = np.array([*X_train_class_0, *X_train_class_1])

    kernel = FidelityQuantumKernel(feature_map=data_encoding_circuit)
    qsvc = QSVC(quantum_kernel=kernel)
    kernel_matrix = qsvc.quantum_kernel.evaluate(X_train_sorted)
    sns.heatmap(kernel_matrix)
