import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

def lire_fichier_notes(path):
    with open(path, "r") as f:
        notes = [float(line.strip()) for line in f if line.strip()]
    return np.array(notes)

def statistiques_descriptives(notes):
    n = len(notes)
    moyenne = np.mean(notes)
    ecart_type = np.std(notes, ddof=1)
    q1 = np.percentile(notes, 25)
    q3 = np.percentile(notes, 75)
    kurtosis = stats.kurtosis(notes, fisher=True, bias=False)
    skewness = stats.skew(notes, bias=False)
    return {
        "n": n,
        "moyenne": moyenne,
        "ecart_type": ecart_type,
        "q1": q1,
        "q3": q3,
        "kurtosis": kurtosis,
        "skewness": skewness
    }

def afficher_statistiques(stats, titre=""):
    print(f"\nStatistiques {titre}")
    print(f"Nombre d'observations : {stats['n']}")
    print(f"Moyenne : {stats['moyenne']:.2f}")
    print(f"Ecart-type : {stats['ecart_type']:.2f}")
    print(f"1er quartile : {stats['q1']:.2f}")
    print(f"3ème quartile : {stats['q3']:.2f}")
    print(f"Kurtosis (aplatissement) : {stats['kurtosis']:.2f}")
    print(f"Skewness (dissymétrie) : {stats['skewness']:.2f}")

def afficher_histogramme(notes, nb_classes, titre="Histogramme"):
    plt.hist(notes, bins=nb_classes, edgecolor='black')
    plt.title(titre)
    plt.xlabel("Notes")
    plt.ylabel("Effectif")
    plt.show()

def intervalle_confiance_moyenne(notes, alpha):
    n = len(notes)
    moyenne = np.mean(notes)
    s = np.std(notes, ddof=1)
    t = stats.t.ppf(1 - alpha/2, df=n-1)
    marge = t * s / np.sqrt(n)
    return moyenne - marge, moyenne + marge

def test_moyenne(notes, mu0, alpha):
    n = len(notes)
    moyenne = np.mean(notes)
    s = np.std(notes, ddof=1)
    t_stat = (moyenne - mu0) / (s / np.sqrt(n))
    p_value = 1 - stats.t.cdf(t_stat, df=n-1)
    rejet = p_value < alpha
    return t_stat, p_value, rejet

def test_chi2_indep(notes1, notes2, nb_classes, alpha):
    # Discrétisation des notes
    bins = np.histogram_bin_edges(np.concatenate([notes1, notes2]), bins=nb_classes)
    table1, _ = np.histogram(notes1, bins)
    table2, _ = np.histogram(notes2, bins)
    tableau = np.array([table1, table2])
    chi2, p, dof, expected = stats.chi2_contingency(tableau)
    rejet = p < alpha
    return chi2, p, rejet

def menu():
    while True:
        print("\nMenu principal :")
        print("1. Statistique descriptive")
        print("2. Statistique inférentielle")
        print("0. Quitter")
        choix = input("Votre choix : ")
        if choix == "1":
            fichier = input("Nom du fichier de notes : ")
            nb_classes = int(input("Nombre de classes pour l'histogramme : "))
            notes = lire_fichier_notes(fichier)
            stats_notes = statistiques_descriptives(notes)
            afficher_statistiques(stats_notes, titre=fichier)
            afficher_histogramme(notes, nb_classes, titre=f"Histogramme de {fichier}")
        elif choix == "2":
            fichier1 = input("Nom du 1er fichier de notes : ")
            fichier2 = input("Nom du 2ème fichier de notes : ")
            notes1 = lire_fichier_notes(fichier1)
            notes2 = lire_fichier_notes(fichier2)
            alpha_ic = float(input("Niveau alpha pour l'intervalle de confiance (ex: 0.05) : "))
            alpha_test = float(input("Niveau alpha pour le test de moyenne (ex: 0.05) : "))
            alpha_chi2 = float(input("Niveau alpha pour le test du chi-deux (ex: 0.05) : "))
            nb_classes = int(input("Nombre de classes pour le chi-deux : "))

            # Estimation mu et sigma
            print("\nEstimation pour", fichier1)
            print(f"  Moyenne : {np.mean(notes1):.2f}, Ecart-type : {np.std(notes1, ddof=1):.2f}")
            print("Estimation pour", fichier2)
            print(f"  Moyenne : {np.mean(notes2):.2f}, Ecart-type : {np.std(notes2, ddof=1):.2f}")

            # Intervalle de confiance
            ic1 = intervalle_confiance_moyenne(notes1, alpha_ic)
            ic2 = intervalle_confiance_moyenne(notes2, alpha_ic)
            print(f"\nIntervalle de confiance {100*(1-alpha_ic):.1f}% pour la moyenne de {fichier1} : [{ic1[0]:.2f}, {ic1[1]:.2f}]")
            print(f"Intervalle de confiance {100*(1-alpha_ic):.1f}% pour la moyenne de {fichier2} : [{ic2[0]:.2f}, {ic2[1]:.2f}]")

            # Test de moyenne (mu0 = 10.5)
            mu0 = 10.5
            t1, p1, rejet1 = test_moyenne(notes1, mu0, alpha_test)
            t2, p2, rejet2 = test_moyenne(notes2, mu0, alpha_test)
            print(f"\nTest de moyenne pour {fichier1} (H0: mu={mu0}) : t={t1:.2f}, p-value={p1:.3f} => {'Rejet' if rejet1 else 'Non rejet'} de H0 au seuil {alpha_test}")
            print(f"Test de moyenne pour {fichier2} (H0: mu={mu0}) : t={t2:.2f}, p-value={p2:.3f} => {'Rejet' if rejet2 else 'Non rejet'} de H0 au seuil {alpha_test}")

            # Test d'indépendance du chi2
            chi2, p_chi2, rejet_chi2 = test_chi2_indep(notes1, notes2, nb_classes, alpha_chi2)
            print(f"\nTest d'indépendance du chi2 : chi2={chi2:.2f}, p-value={p_chi2:.3f} => {'Rejet' if rejet_chi2 else 'Non rejet'} d'indépendance au seuil {alpha_chi2}")

            # Interprétation simple
            print("\nInterprétation :")
            if np.mean(notes1) > np.mean(notes2):
                print(f"  Les étudiants ont eu de meilleurs résultats en {fichier1} qu'en {fichier2}.")
            elif np.mean(notes1) < np.mean(notes2):
                print(f"  Les étudiants ont eu de meilleurs résultats en {fichier2} qu'en {fichier1}.")
            else:
                print("  Les moyennes sont identiques.")

            print("  Voir les p-values pour la significativité statistique des tests.")
        elif choix == "0":
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    menu()