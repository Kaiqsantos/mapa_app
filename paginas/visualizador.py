import numpy as np
import streamlit as st
from geopy.distance import geodesic
from matplotlib import pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm

modo_escuro = st.session_state["escuro"]

fig, ax = plt.subplots(figsize=(10, 8))

tab1, tab2 = st.tabs(["📈 Gráfico", "📋 Dados"])

df_1_e = tab2.data_editor(st.session_state['df_1'].copy())

estado = st.select_slider('Estados:', sorted(st.session_state["gdf"].copy().reset_index().iloc[:,0].values.tolist()))

modo = st.segmented_control("Âncora:", ["Origem", "Destino"])

if not modo is None:
    mostrar_df = df_1_e.loc[:,[estado]].copy() if modo == "Origem" else df_1_e.loc[[estado],:].copy()
    tab2.markdown(f"""
    <div style="overflow: auto; max-height: 400px; max-width: 800px">
    {mostrar_df.style.set_properties(**{'text-align': 'center'})
    .map(lambda elem: 'background-color: #BBB; color: #000' if elem == 0 else 'background-color: #FFF; color: #000')
    .to_html()} </div>""", unsafe_allow_html=True)


    coords_origem = st.session_state['centroide'].loc[estado]
    cmap_meu = LinearSegmentedColormap.from_list("",np.array([[0., 0., 1.], [0., 1., 1.],
                                                              [0., .5, 0.], [1., 1., 0.], [1., 0., 0.]]))
    cmap = ListedColormap(np.vstack(([1., .5, .75, 1.], cmap_meu(np.linspace(0, 1, 256, endpoint=True)))))

    bounds = np.insert(np.linspace(1, 100, 256, endpoint=True),0, 0)

    sm = ScalarMappable(cmap=cmap, norm=BoundaryNorm(bounds, cmap.N))

    st.session_state['gdf'].plot(ax=ax, color='lightgray', edgecolor='black')

    for it in st.session_state['centroide'].copy().apply(
            lambda _: geodesic(_.coords,coords_origem.coords).km).sort_values(ascending=False).index:
        if modo == "Origem":
            ax.quiver(coords_origem.x, coords_origem.y,
                      st.session_state['centroide'].loc[it].x - coords_origem.x,
                      st.session_state['centroide'].loc[it].y - coords_origem.y,
                      angles='xy', scale_units='xy', scale=1, color=sm.to_rgba(df_1_e.copy().loc[it,estado]))
        else:
            ax.quiver(st.session_state['centroide'].loc[it].x, st.session_state['centroide'].loc[it].y,
                      coords_origem.x - st.session_state['centroide'].loc[it].x,
                      coords_origem.y - st.session_state['centroide'].loc[it].y,
                      angles='xy', scale_units='xy', scale=1, color=sm.to_rgba(df_1_e.copy().loc[estado,it]))
    if modo == "Origem":
        ax.set_title('Mapa do fluxo entre a UF de origem -> UF de destino', color=st.session_state["cores"]['tex'][modo_escuro])
        rco = np.radians(coords_origem.coords)[0]
        origem_xyz = np.array([np.cos(rco[1]) * np.cos(rco[0]),
                               np.cos(rco[1]) * np.sin(rco[0]),
                               np.sin(rco[1])])
        destinos_xyz = np.array([np.array([np.cos(np.radians(d.y)) * np.cos(np.radians(d.x)),
                                     np.cos(np.radians(d.y)) * np.sin(np.radians(d.x)),
                                     np.sin(np.radians(d.y))]) for d in st.session_state['centroide'].copy().drop(estado)])
        res = origem_xyz + np.average(destinos_xyz - origem_xyz, axis=0, weights=df_1_e.copy().loc[:,estado].drop(estado).values)
        res /= np.linalg.norm(res)
        ponderada = {"lat": np.degrees(np.arctan2(res[2], np.sqrt(res[0] ** 2 + res[1] ** 2))),
                     "lon": np.degrees(np.arctan2(res[1], res[0]))}

        ax.quiver(coords_origem.x, coords_origem.y, ponderada["lon"] - coords_origem.x,
                      ponderada["lat"] - coords_origem.y, angles='xy', scale_units='xy',
                      scale=1, color="darkviolet")
    else:
        ax.set_title('Mapa do fluxo entre a UF de destino <- UF de origem', color=st.session_state["cores"]['tex'][modo_escuro])
        rco = np.radians(coords_origem.coords)[0]
        origem_xyz = np.array([np.cos(rco[1]) * np.cos(rco[0]),
                               np.cos(rco[1]) * np.sin(rco[0]),
                               np.sin(rco[1])])
        destinos_xyz = np.array([np.array([np.cos(np.radians(d.y)) * np.cos(np.radians(d.x)),
                                           np.cos(np.radians(d.y)) * np.sin(np.radians(d.x)),
                                           np.sin(np.radians(d.y))]) for d in
                                 st.session_state['centroide'].copy().drop(estado)])
        res = origem_xyz + np.average(destinos_xyz - origem_xyz, axis=0,
                                      weights=df_1_e.copy().loc[estado, :].drop(estado).values)
        res /= np.linalg.norm(res)
        ponderada = {"lat": np.degrees(np.arctan2(res[2], np.sqrt(res[0] ** 2 + res[1] ** 2))),
                     "lon": np.degrees(np.arctan2(res[1], res[0]))}

        ax.quiver(ponderada["lon"], ponderada["lat"], coords_origem.x - ponderada["lon"],
                  coords_origem.y - ponderada["lat"], angles='xy', scale_units='xy',
                  scale=1, color="darkviolet")

    cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.05)
    cbar.set_label('Número de indivíduos', color=st.session_state["cores"]['tex'][modo_escuro])
    cbar.set_ticks(np.linspace(0, 100, 11, endpoint=True))
    cbar.ax.tick_params(axis='both', colors=st.session_state["cores"]['tex'][modo_escuro])
    cbar.minorticks_off()
    ax.scatter(st.session_state['centroide'].copy().x,
               st.session_state['centroide'].copy().y, color='gray',
               edgecolors='black', linewidths=0.5, marker='o', s=20)

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')

    for i in ax.spines.values():
        i.set_color(st.session_state["cores"]['tex'][modo_escuro])

    ax.tick_params(axis='both', colors=st.session_state["cores"]['tex'][modo_escuro])

    ax.xaxis.label.set_color(st.session_state["cores"]['tex'][modo_escuro])
    ax.yaxis.label.set_color(st.session_state["cores"]['tex'][modo_escuro])

    tab1.pyplot(fig)