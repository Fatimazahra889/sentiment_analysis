import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sklearn.svm import SVC
from sklearn.datasets import make_classification

# Force l'affichage correct avec Matplotlib
matplotlib.use('TkAgg')

# Génération de données linéairement séparables
X, y = make_classification(n_samples=100, n_features=2, n_informative=2, n_redundant=0, n_clusters_per_class=1, class_sep=0.5, random_state=42)

# Entraînement du modèle SVM avec soft margin (C faible)
svm_soft = SVC(kernel='linear', C=0.1)
svm_soft.fit(X, y)

# Affichage de la frontière de décision
def plot_decision_boundary(model, X, y):
    xx, yy = np.meshgrid(np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 100),
                         np.linspace(X[:, 1].min() - 1, X[:, 1].max() + 1, 100))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.contourf(xx, yy, Z, alpha=0.3)
    plt.scatter(X[:, 0], X[:, 1], c=y, edgecolors='k', marker='o')
    plt.title("SVM avec séparation linéaire (Soft Margin)")
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.show()

plot_decision_boundary(svm_soft, X, y)
