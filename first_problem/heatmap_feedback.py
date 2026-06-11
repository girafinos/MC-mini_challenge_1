import numpy as np
import matplotlib.pyplot as plt

# ROW = 5
# COLUMN = 4

# # Dados
# learning_rates = ['0.001', '0.005', '0.01']
# batch_sizes = ['8', '16', '20', '32']

# Matriz: linhas = learning rates, colunas = batch sizes
# map_values = np.array([
#     [0.504, 0.529, 0.788, 0.773],
#     [0.879, 0.882, 0.882, 0.878],
#     [0.900, 0.898, 0.897, 0.898]
# ])

# plt.figure(figsize=(7, 5))

# heatmap = plt.imshow(map_values, aspect='auto')

# plt.xticks(np.arange(len(batch_sizes)), batch_sizes)
# plt.yticks(np.arange(len(learning_rates)), learning_rates)

# plt.xlabel('Batch size')
# plt.ylabel('Learning rate')
# plt.title('teste')

# cbar = plt.colorbar(heatmap)
# cbar.set_label('mAP@0.5:0.95')

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
            plt.text(j, i, value, ha='center', va='center')
            
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
            
            plt.text(
                j, 
                i + 0.35, 
                f"shake: {shake_intensity[i][j]}", 
                ha='center', 
                va='center',
                fontsize=6,
                color=(74/255, 37/255, 11/255, 1.0),
                fontweight='bold'
            )

# for i in range(ROW):
#     if i == 5:
#         for j in range(3):
#             valor = map_values[i, j]
#             plt.text(j, i, f'{valor:.3f}', ha='center', va='center')

#     for j in range(COLUMN):
#         valor = map_values[i, j]
#         plt.text(j, i, f'{valor:.3f}', ha='center', va='center')

intensity_matrix = [
    [0.7089, 1.5460, 4.8670, 4.6199],
    [0.6647, 1.1540, 4.6646, 1.6324],
    [1.0804, 1.5700, 2.5602, 4.3976],
    [2.4622, 3.4445, 2.2098, 1.1502],
    [1.6302, 3.5189, 1.9742, np.nan]
]

heat_matrix = [
    [4.7401, 3.4135, 7.2754, 5.4687],
    [4.2053, 2.9380, 8.5000, 7.4997],
    [7.4560, 5.6769, 6.2890, 3.1828],
    [3.8899, 6.1258, 3.5346, 5.1828],
    [1.9102, 3.3564, 2.7485, np.nan]
]

create_heatmap("sewer_and_water", heat_matrix, intensity_matrix)
plt.savefig('figures/sewer_and_water.png', dpi=300, bbox_inches='tight')
plt.show()