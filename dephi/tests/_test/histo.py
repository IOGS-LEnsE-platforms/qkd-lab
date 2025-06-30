import numpy as np
import matplotlib.pyplot as plt

# Liste de données
donnees1 = np.array([1, 6, 2, 3, 3, 3, 4, 4, 5])
donnees2 = np.array([3, 4, 4, 5, 1, 6])

# Définir les mêmes intervalles de classes (bins)
bins = [1, 2, 3, 4, 5, 6, 7]
centres = np.array(bins[:-1]) # + np.array(bins[1:]))

# Histogramme 1
comptes1, _ = np.histogram(donnees1, bins=bins)

# Histogramme 2 (nouvelles données)
comptes2, _ = np.histogram(donnees2, bins=bins)

# Additionner les comptes
comptes_total = comptes1 + comptes2

print("Comptes : ", comptes_total)
print("Bords : ", bins)
print("Centres: ", centres)


plt.figure()
plt.bar(centres, comptes_total, width=1.0, edgecolor='black')
plt.show()