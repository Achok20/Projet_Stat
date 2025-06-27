import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import datetime
import os

# Import optionnel de reportlab pour la génération de PDF
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Module reportlab non trouvé. Pour installer : pip install reportlab")

def creer_histogramme_pour_pdf(notes, nb_classes, titre="Histogramme", fichier_sortie=None):
    """Crée un histogramme et le sauvegarde pour l'inclusion dans le PDF"""
    if fichier_sortie is None:
        fichier_sortie = f"histogramme_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    # Créer l'histogramme avec un style simple et professionnel
    plt.figure(figsize=(8, 5))
    plt.hist(notes, bins=nb_classes, color='#4472C4', alpha=0.7, edgecolor='#2E4B8C', linewidth=1)
    
    plt.title(titre, fontsize=14, fontweight='bold', color='#2E4B8C', pad=20)
    plt.xlabel("Notes", fontsize=12, color='#333333')
    plt.ylabel("Effectif", fontsize=12, color='#333333')
    plt.grid(axis='y', linestyle='-', linewidth=0.5, color='#E0E0E0', alpha=0.8)
    
    # Améliorer l'apparence générale
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color('#CCCCCC')
    plt.gca().spines['bottom'].set_color('#CCCCCC')
    
    # Sauvegarder l'image
    plt.savefig(fichier_sortie, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()  # Fermer la figure pour libérer la mémoire
    
    return fichier_sortie

def generer_rapport_pdf(stats1=None, stats2=None, fichier1="", fichier2="", 
                       ic1=None, ic2=None, test_results=None, chi2_result=None, alpha_values=None,
                       notes1=None, notes2=None, nb_classes=10):
    """Génère un rapport PDF des résultats statistiques"""
    if not REPORTLAB_AVAILABLE:
        print("Impossible de générer le PDF : module reportlab non installé.")
        return None
        
    filename = f"rapport_statistiques_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Variables pour les fichiers temporaires d'histogrammes
    hist_file1 = None
    hist_file2 = None
    
    # Titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Centré
    )
    story.append(Paragraph("RAPPORT D'ANALYSE STATISTIQUE", title_style))
    story.append(Spacer(1, 12))
    
    # Date
    story.append(Paragraph(f"Date : {datetime.datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Statistiques descriptives
    if stats1:
        story.append(Paragraph("1. STATISTIQUES DESCRIPTIVES", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Tableau pour fichier1
        story.append(Paragraph(f"Fichier : {fichier1}", styles['Heading3']))
        data1 = [
            ['Indicateur', 'Valeur'],
            ['Nombre d\'observations', f"{stats1['n']}"],
            ['Moyenne', f"{stats1['moyenne']:.2f}"],
            ['Écart-type', f"{stats1['ecart_type']:.2f}"],
            ['1er quartile (Q1)', f"{stats1['q1']:.2f}"],
            ['3ème quartile (Q3)', f"{stats1['q3']:.2f}"],
            ['Kurtosis', f"{stats1['kurtosis']:.2f}"],
            ['Skewness', f"{stats1['skewness']:.2f}"]
        ]
        
        table1 = Table(data1)
        table1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table1)
        story.append(Spacer(1, 20))
        
        # Interprétation statistiques descriptives
        story.append(Paragraph("Interprétation :", styles['Heading4']))
        interpretation = f"""
        L'échantillon contient {stats1['n']} observations. La moyenne des notes est de {stats1['moyenne']:.2f} 
        avec un écart-type de {stats1['ecart_type']:.2f}. 50% des notes sont comprises entre {stats1['q1']:.2f} et {stats1['q3']:.2f}.
        
        La kurtosis de {stats1['kurtosis']:.2f} indique une distribution {'plus aplatie' if stats1['kurtosis'] < 0 else 'plus pointue'} 
        que la normale. La skewness de {stats1['skewness']:.2f} révèle une asymétrie 
        {'vers la gauche' if stats1['skewness'] < 0 else 'vers la droite'}.
        """
        story.append(Paragraph(interpretation, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Histogramme pour fichier1
        if notes1 is not None:
            story.append(Paragraph("Histogramme :", styles['Heading4']))
            hist_file1 = creer_histogramme_pour_pdf(notes1, nb_classes, f"Histogramme de {fichier1}")
            img1 = Image(hist_file1, width=5*inch, height=3*inch)
            story.append(img1)
            story.append(Spacer(1, 20))
        
        # Tableau pour fichier2 s'il existe
        if stats2:
            story.append(Paragraph(f"Fichier : {fichier2}", styles['Heading3']))
            data2 = [
                ['Indicateur', 'Valeur'],
                ['Nombre d\'observations', f"{stats2['n']}"],
                ['Moyenne', f"{stats2['moyenne']:.2f}"],
                ['Écart-type', f"{stats2['ecart_type']:.2f}"],
                ['1er quartile (Q1)', f"{stats2['q1']:.2f}"],
                ['3ème quartile (Q3)', f"{stats2['q3']:.2f}"],
                ['Kurtosis', f"{stats2['kurtosis']:.2f}"],
                ['Skewness', f"{stats2['skewness']:.2f}"]
            ]
            
            table2 = Table(data2)
            table2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table2)
            story.append(Spacer(1, 20))
            
            # Interprétation pour fichier2
            story.append(Paragraph("Interprétation :", styles['Heading4']))
            interpretation2 = f"""
            L'échantillon contient {stats2['n']} observations. La moyenne des notes est de {stats2['moyenne']:.2f} 
            avec un écart-type de {stats2['ecart_type']:.2f}. 50% des notes sont comprises entre {stats2['q1']:.2f} et {stats2['q3']:.2f}.
            
            La kurtosis de {stats2['kurtosis']:.2f} indique une distribution {'plus aplatie' if stats2['kurtosis'] < 0 else 'plus pointue'} 
            que la normale. La skewness de {stats2['skewness']:.2f} révèle une asymétrie 
            {'vers la gauche' if stats2['skewness'] < 0 else 'vers la droite'}.
            """
            story.append(Paragraph(interpretation2, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Histogramme pour fichier2
            if notes2 is not None:
                story.append(Paragraph("Histogramme :", styles['Heading4']))
                hist_file2 = creer_histogramme_pour_pdf(notes2, nb_classes, f"Histogramme de {fichier2}")
                img2 = Image(hist_file2, width=5*inch, height=3*inch)
                story.append(img2)
                story.append(Spacer(1, 20))
    
    # Statistiques inférentielles
    if ic1 and test_results:
        story.append(Paragraph("2. STATISTIQUES INFÉRENTIELLES", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Intervalles de confiance
        story.append(Paragraph("2.1 Intervalles de confiance", styles['Heading3']))
        ic_text = f"""
        Intervalle de confiance à {100*(1-alpha_values['ic']):.0f}% pour {fichier1} : 
        [{ic1[0]:.2f}, {ic1[1]:.2f}]
        """
        if ic2:
            ic_text += f"""
            Intervalle de confiance à {100*(1-alpha_values['ic']):.0f}% pour {fichier2} : 
            [{ic2[0]:.2f}, {ic2[1]:.2f}]
            """
        story.append(Paragraph(ic_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Tests de moyenne
        story.append(Paragraph("2.2 Tests de moyenne", styles['Heading3']))
        test_text = f"""
        Test pour {fichier1} (H₀: μ = 10.5) :
        • Statistique t = {test_results['t1']:.2f}
        • p-value = {test_results['p1']:.3f}
        • Conclusion : {'Rejet' if test_results['rejet1'] else 'Non rejet'} de H₀ au seuil {alpha_values['test']}
        """
        story.append(Paragraph(test_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Test du chi-deux
        if chi2_result:
            story.append(Paragraph("2.3 Test d'indépendance du χ²", styles['Heading3']))
            chi2_text = f"""
            • Statistique χ² = {chi2_result['chi2']:.2f}
            • p-value = {chi2_result['p']:.3f}
            • Conclusion : {'Rejet' if chi2_result['rejet'] else 'Non rejet'} de l'indépendance au seuil {alpha_values['chi2']}
            """
            story.append(Paragraph(chi2_text, styles['Normal']))
    
    # Conclusion
    story.append(Spacer(1, 20))
    if ic1 and test_results:
        story.append(Paragraph("3. CONCLUSION", styles['Heading2']))
        conclusion = """
        Cette analyse statistique permet de caractériser la distribution des notes et de tester
        certaines hypothèses. Les résultats des tests d'hypothèses indiquent si les différences
        observées sont statistiquement significatives.
        """
    else:
        story.append(Paragraph("2. CONCLUSION", styles['Heading2']))
        conclusion = """
        Cette analyse descriptive permet de caractériser la distribution des notes de l'échantillon étudié.
        Les indicateurs calculés donnent une vue d'ensemble de la performance des étudiants et de la
        forme de la distribution des résultats.
        """
    story.append(Paragraph(conclusion, styles['Normal']))
    
    # Génération du PDF
    doc.build(story)
    print(f"\nRapport PDF généré : {filename}")
    
    # Nettoyer les fichiers temporaires d'histogrammes
    if hist_file1:
        try:
            os.remove(hist_file1)
        except:
            pass
    if hist_file2:
        try:
            os.remove(hist_file2)
        except:
            pass
    
    return filename

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
            
            # Générer rapport PDF pour les statistiques descriptives
            generer_pdf = input("\nGénérer un rapport PDF des statistiques descriptives ? (o/n) : ")
            if generer_pdf.lower() == 'o':
                generer_rapport_pdf(stats1=stats_notes, fichier1=fichier, notes1=notes, nb_classes=nb_classes)
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
            
            # Générer rapport PDF
            generer_pdf = input("\nGénérer un rapport PDF ? (o/n) : ")
            if generer_pdf.lower() == 'o':
                alpha_vals = {'ic': alpha_ic, 'test': alpha_test, 'chi2': alpha_chi2}
                test_res = {'t1': t1, 'p1': p1, 'rejet1': rejet1, 't2': t2, 'p2': p2, 'rejet2': rejet2}
                chi2_res = {'chi2': chi2, 'p': p_chi2, 'rejet': rejet_chi2}
                stats1 = statistiques_descriptives(notes1)
                stats2 = statistiques_descriptives(notes2)
                # Créer et sauvegarder les histogrammes
                histo1_path = creer_histogramme_pour_pdf(notes1, nb_classes, titre=f"Histogramme de {fichier1}")
                histo2_path = creer_histogramme_pour_pdf(notes2, nb_classes, titre=f"Histogramme de {fichier2}")
                # Inclure les chemins des histogrammes dans le rapport
                generer_rapport_pdf(stats1, stats2, fichier1, fichier2, ic1, ic2, test_res, chi2_res, alpha_vals, notes1, notes2, nb_classes)
        elif choix == "0":
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    menu()