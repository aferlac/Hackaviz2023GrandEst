# Packages nécessaires
import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st
import matplotlib.pyplot as plt 

@st.cache_data
def chargement(file):
    df = pd.read_csv(file)
    return df

# Parametrage de la page
st.set_page_config(page_title=" HACKAVIZ GRAND EST 2023 ",
                   layout='centered',
                   initial_sidebar_state='auto')
st.markdown("""
            <style>
            .main {background-color:#fdfdfe}
            </style>
            """,
            unsafe_allow_html=True
            )
background_color = '#fdfdfe'

# définition des couleurs par classe de POI
def color(classe):
    '''
    Affectation d'une couleur par classe de POI
    Entrée = Classe de POI
    Sortie = Couleur
    '''
    if classe == 'Monuments':
        col = 'blue'
    elif classe=='Paysage':
        col = 'green'
    elif classe=='Info touristes':
        col = 'orange'
    elif classe=='Activites':
        col = 'red'
    elif classe=='Commerces':
        col = 'purple'
    else:
        col='black'
    return col

# Texte d'introduction
st.title("Vous avez réservé dans la région Grand Est.")
st.header("Que découvrir à 1 heure de votre lieu de séjour ?")

# Chargement des données
data_com = chargement('./data_com_app.csv') # Données des communes ayant des réservations de séjour (Nom, département, latitude, longitude, ...)

df_poi=chargement('./poi_hackaviz_grand_est_1.csv')
for i in range(2,61):
    df_poi=pd.concat([df,chargement('./poi_hackaviz_grand_est_'+str(i)+'.csv')])
    df_poi.reset_index(inplace=True)
    df_poi.drop('index', axis=1, inplace=True)
df_poi.drop_duplicates(inplace=True)
df_poi.reset_index(inplace=True) # Données des POI (Nom, commune, classe, latitude, longitude, distance aux communes du data_com)

# Choix du département de séjour
col1, col2, col3= st.columns([1,1,1])
departement = col1.selectbox("Dans quel département ?",
                            ('Ardennes', 'Aube', 'Marne', 'Haute-Marne', 'Meurthe-et-Moselle', 'Meuse', 'Moselle', 'Bas-Rhin', 'Haut-Rhin', 'Vosges'),
                            index=None,
                            placeholder="Choisissez ...")

# Choix de la ville de séjour
ville = col2.selectbox("Dans quelle commune ?",
                      data_com[data_com['libdept']==departement]['libcom'].unique(),
                      index=None,
                      placeholder="Choisissez ...")

# Choix du mode de déplacement pour parcourir 1 heure
pied = 'à pied (1 h ≃ 5 km)'
velo = 'à vélo (1 h ≃ 15 km)'
auto = 'en voiture (1 h ≃ 50 km)'
mode_deplac = col3.selectbox("Comment vous déplacez vous ?",
                            (pied, velo, auto),
                            index=None,
                            placeholder="Choisissez ...")

# Création des graphiques
if (ville!=None) & (mode_deplac!=None):

    # Récupération du code insee de la ville de séjour
    code_ville = str(list(data_com[(data_com['libcom']==ville)&(data_com['libdept']==departement)]['com'])[0])
    if len(code_ville) == 4:
        code_ville = '0'+code_ville

    # Sélection des paramêtres en fonction du mode de déplacement
    if mode_deplac == pied:
        distance, zoom = 5, 12
    if mode_deplac == velo:
        distance, zoom = 15, 10
    if mode_deplac == auto:
        distance, zoom = 50, 9

    # Création du df selon la ville de séjour et le mode de déplacement (distance)
    df = df_poi[['desc','libcom','libdept','lat','lon','classe',code_ville]]
    df = df[df[code_ville]<=distance]

    # Création une carte centrée sur la commune choisie
    lat_carte = data_com[(data_com['libcom']==ville)&(data_com['libdept']==departement)]['lat_com']
    lon_carte = data_com[(data_com['libcom']==ville)&(data_com['libdept']==departement)]['lon_com']
    carte_points = folium.Map([lat_carte, lon_carte],
                                zoom_start=zoom,
                                tiles="cartodbpositron")

    # Ajout des points pour chaque emplacement de POI
    for element in df.index:
        html = '<h4>'+df['desc'][element]+'</h4><strong>'+df['libcom'][element]+'</strong><br>'+df['classe'][element]
        folium.CircleMarker([df['lat'][element],
                            df['lon'][element]],
                            radius=2, fill=True,
                            popup=html,
                            color=color(df['classe'][element])
                            ).add_to(carte_points)

    # Ajout du marqueur sur le centre de la commune choisie    
    folium.Marker([lat_carte, lon_carte],popup=ville).add_to(carte_points)

    # Ajout du cercle à la distance choisie
    folium.Circle([lat_carte, lon_carte], radius=distance*1000, color='#042e60').add_to(carte_points)

    # Affichage de la carte
    folium_static(carte_points)

    # Ajout d'un bargraph du nombre de POI par classe de POI
    # Construction du df 
    Classe, Nombre, couleur = [], [], []
    for element in df['classe'].unique():
        Classe.append(element)
        Nombre.append(len(df[df['classe']==element]))
        couleur.append(color(element))   
    df2 = pd.DataFrame({'Classe':Classe, 'Nombre':Nombre, 'Couleur':couleur}).sort_values(by='Nombre',ascending=False)

    # Tracé du bargraph
    width = 0.8       # the width of the bars
    fig, ax = plt.subplots(figsize=(20,10))
    p1 = ax.bar(df2['Classe'], df2['Nombre'], width, color=df2['Couleur'])
    ax.axhline(0, color='grey', linewidth=0.8)
    ax.set_title("Nombre de points d'intérêt dans les "+str(distance)+' km', fontsize=30)
    ax.xaxis.set_tick_params(labelsize = 25)
    ax.tick_params(bottom = False)
    ax.set_yticks([])
    for pos in ['right', 'top', 'bottom', 'left']:
        plt.gca().spines[pos].set_visible(False)
    ax.bar_label(p1, fontsize=25)
    # Affichage du bargraph
    st.pyplot(fig)

    # Texte de conclusion
    col1, col2, col3= st.columns([1,2,1])
    col2.header("Bon séjour chez nous !")
    st.write('---')
