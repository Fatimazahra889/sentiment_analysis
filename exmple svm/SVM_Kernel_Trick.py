import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_moons

# Génération d'un dataset en forme de lunes (non-linéaire)
X, y = make_moons(n_samples=200, noise=0.1, random_state=42)

# Entraînement du modèle SVM avec un noyau gaussien (RBF)
svm_rbf = SVC(kernel='rbf', C=1, gamma=0.5)
svm_rbf.fit(X, y)

# Fonction d'affichage de la frontière de décision
def plot_decision_boundary(model, X, y):
    xx, yy = np.meshgrid(np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 100),
                         np.linspace(X[:, 1].min() - 1, X[:, 1].max() + 1, 100))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
    plt.scatter(X[:, 0], X[:, 1], c=y, edgecolors='k', cmap='coolwarm')
    plt.title("SVM avec noyau RBF (non-linéaire)")
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.show()

plot_decision_boundary(svm_rbf, X, y)
