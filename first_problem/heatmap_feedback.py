import numpy as np
import matplotlib.pyplot as plt

def create_heatmap(column_name, matriz, shake_intensity=None):
    #cividis
    #coolwarm
    created_heatmap = plt.imshow(matriz, aspect='auto', cmap='coolwarm', vmin=0, vmax=10)
    plt.title(column_name)
    plt.colorbar()
    
    plt.axis('off')
    
    for i, row in enumerate(matriz):
        for j, value in enumerate(row):
            if np.isnan(value):
                continue
            
            # Escrita dos dados
            plt.text(j, i, f"{value:.4f}", ha='center', va='center')
            
            # Escrever localização
            plt.text(
                j,
                i - 0.35, 
                f"Área: {(i*4+j) + 1}", 
                ha='center', 
                va='center',
                fontsize=6,
                color=(74/255, 37/255, 11/255, 1.0),
                fontweight='bold'
            )
            
            if shake_intensity is None or column_name == "shake_intensity":
                continue
            
            plt.text(
                j, 
                i + 0.35, 
                f"shake: {shake_intensity[i][j]:.4f}", 
                ha='center', 
                va='center',
                fontsize=6,
                color=(74/255, 37/255, 11/255, 1.0),
                fontweight='bold'
            )

def save_heatmap(column_name, matriz, shake_intensity=None):
    create_heatmap(column_name, matriz, shake_intensity)
    plt.savefig(f'figures/{column_name}.png', dpi=300, bbox_inches='tight')