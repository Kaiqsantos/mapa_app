import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap, ListedColormap
from PIL import Image
import pandas as pd
import geopandas as gpd
from geopy.distance import geodesic
import sys
import importlib.metadata

st.logo(Image.open("imagens/icone.png"))

modo_escuro = st.session_state["escuro"]

fig, ax = plt.subplots(figsize=(10, 8))
if 'redefinir_mapa' in st.session_state and st.session_state['redefinir_mapa']:
    del st.session_state['redefinir_mapa']
    st.switch_page("mapa.py")


origem = 'BA'
coords_origem = st.session_state['centroide'].loc[origem]
cmap_meu = LinearSegmentedColormap.from_list("",np.array([[0., 0., 1.], [0., 1., 1.],
                                                          [0., .5, 0.], [1., 1., 0.], [1., 0., 0.]]))
cmap = ListedColormap(np.vstack(([1., .5, .75, 1.], cmap_meu(np.linspace(0, 1, 256, endpoint=True)))))

bounds = np.insert(np.linspace(1, 100, 256, endpoint=True),0, 0)

sm = ScalarMappable(cmap=cmap, norm=BoundaryNorm(bounds, cmap.N))

st.session_state['gdf'].plot(ax=ax, color='lightgray', edgecolor='black')

for it in st.session_state['centroide'].copy().apply(
        lambda _: geodesic(_.coords,coords_origem.coords).km).sort_values(ascending=False).index:
    ax.quiver(coords_origem.x, coords_origem.y,
              st.session_state['centroide'].loc[it].x - coords_origem.x,
              st.session_state['centroide'].loc[it].y - coords_origem.y,
              angles='xy', scale_units='xy', scale=1, color=sm.to_rgba(st.session_state["df_1"].copy().loc[it,origem]))

rco = np.radians(coords_origem.coords)[0]
origem_xyz = np.array([np.cos(rco[1]) * np.cos(rco[0]),
                       np.cos(rco[1]) * np.sin(rco[0]),
                       np.sin(rco[1])])
destinos_xyz = np.array([np.array([np.cos(np.radians(d.y)) * np.cos(np.radians(d.x)),
                             np.cos(np.radians(d.y)) * np.sin(np.radians(d.x)),
                             np.sin(np.radians(d.y))]) for d in st.session_state['centroide'].copy().drop(origem)])
res = origem_xyz + np.average(destinos_xyz - origem_xyz, axis=0, weights=st.session_state["df_1"].copy().loc[:,origem].drop(origem).values)
res /= np.linalg.norm(res)
ponderada = {"lat": np.degrees(np.arctan2(res[2], np.sqrt(res[0] ** 2 + res[1] ** 2))),
             "lon": np.degrees(np.arctan2(res[1], res[0]))}

ax.quiver(coords_origem.x, coords_origem.y, ponderada["lon"] - coords_origem.x,
              ponderada["lat"] - coords_origem.y, angles='xy', scale_units='xy',
              scale=1, color="darkviolet")


cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.05)
cbar.set_label('Número de indivíduos', color=st.session_state["cores"]['tex'][modo_escuro])
cbar.set_ticks(np.linspace(0, 100, 11, endpoint=True))
cbar.ax.tick_params(axis='both', colors=st.session_state["cores"]['tex'][modo_escuro])
cbar.minorticks_off()
ax.scatter(st.session_state['centroide'].copy().x,
           st.session_state['centroide'].copy().y, color='gray',
           edgecolors='black', linewidths=0.5, marker='o', s=20)

ax.set_title('Mapa do fluxo entre a UF de origem -> UF de destino', color=st.session_state["cores"]['tex'][modo_escuro])
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

fig.patch.set_facecolor('none')
ax.set_facecolor('none')

for i in ax.spines.values():
    i.set_color(st.session_state["cores"]['tex'][modo_escuro])

ax.tick_params(axis='both', colors=st.session_state["cores"]['tex'][modo_escuro])

ax.xaxis.label.set_color(st.session_state["cores"]['tex'][modo_escuro])
ax.yaxis.label.set_color(st.session_state["cores"]['tex'][modo_escuro])


st.title("Página Inicial")

st.subheader("Mapa", divider="rainbow")

tab1, tab2 = st.tabs(["📈 Gráfico", "📋 Dados"])
tab1.pyplot(fig)

tab2.markdown(f"""
<div style="overflow: auto; max-height: 400px; max-width: 800px">
{st.session_state["df_1"].copy().style.set_properties(**{'text-align': 'center'})
.apply(lambda col: ['background-color: #FFF; color: #000' if col.name == 'BA' else '' for _ in col], axis=0)
.map(lambda x: 'background-color: #BBB; color: #000' if x == 0 else '')
.to_html()}
</div>""", unsafe_allow_html=True)
st.subheader("💡Ideia inicial", divider="gray")
st.markdown("Esse mapa foi criado com a intenção de representar o fluxo migratório dos inscritos no SISU 2023.1 entre "
            "as unidades federativas brasileiras.")
st.subheader("📊 Interpretação", divider="violet")
st.markdown("O gráfico mostra o fluxo migratório de indivíduos que se deslocam da Bahia para as outras unidades "
            "federativas, cada seta colorida representa o número de candidatos que saem da Bahia e se dirigem para "
            "campus de outras unidades federativas brasileiras.  \n\n Sendo:")

st.markdown(fr"<p><span style='color:#FF0000; background-color: {st.session_state["cores"]["pbg"][False]}; border-radius: 10px; padding: 3px; font-weight:bold;'>Vermelho</span> quando o fluxo da unidade federativa de origem para a unidade federativa de destino atinge o máximo</p>", unsafe_allow_html=True)
st.markdown(fr"<p><span style='color:#FFFF00; background-color: {st.session_state["cores"]["pbg"][True]}; border-radius: 10px; padding: 3px; font-weight:bold;'>Amarelo</span> quando o fluxo da unidade federativa de origem para a unidade federativa de destino atinge 75% da amplitude total</p>", unsafe_allow_html=True)
st.markdown(fr"<p><span style='color:#008000; background-color: {st.session_state["cores"]["pbg"][True]}; border-radius: 10px; padding: 3px; font-weight:bold;'>Verde</span> quando o fluxo da unidade federativa de origem para a unidade federativa de destino atinge a semi-amplitude</p>", unsafe_allow_html=True)
st.markdown(fr"<p><span style='color:#00FFFF; background-color: {st.session_state["cores"]["pbg"][True]}; border-radius: 10px; padding: 3px; font-weight:bold;'>Azul Claro</span> quando o fluxo da unidade federativa de origem para a unidade federativa de destino atinge 25% da amplitude total</p>", unsafe_allow_html=True)
st.markdown(fr"<p><span style='color:#0000FF; background-color: {st.session_state["cores"]["pbg"][False]}; border-radius: 10px; padding: 3px; font-weight:bold;'>Azul</span> quando o fluxo da unidade federativa de origem para a unidade federativa de destino atinge o mínimo (diferente de 0)</p>", unsafe_allow_html=True)
st.markdown(fr"<p><span style='color:#FF80C0; background-color: {st.session_state["cores"]["pbg"][True]}; border-radius: 10px; padding: 3px; font-weight:bold;'>Rosa</span> quando não houve fluxo da unidade federativa de origem para a unidade federativa de destino</p>", unsafe_allow_html=True)
st.markdown(fr"<p><span style='color:#9400D3; background-color: {st.session_state["cores"]["pbg"][False]}; border-radius: 10px; padding: 3px; font-weight:bold;'>Roxo</span> o vetor resultante da média ponderada dos outros vetores</p>", unsafe_allow_html=True)

st.subheader("✅ Vantagens", divider="green")
st.markdown("1. **Visualização clara de fluxos geográficos**: Torna fácil perceber o deslocamento dos indivíduos.\n"
            "2. **Percepção imediata de intensidade**: As cores destacam os estados com maior recebimento/envio de indivíduos.\n"
            "3. **Acessível para o público geral**: Mesmo quem não tem formação estatística entende o gráfico rapidamente.\n"
            "4. **Fácil identificação de padrões regionais**: Mostra a força de atração do campus no contexto regional e nacional.")

st.subheader("❌ Desvantagens", divider="red")
st.markdown("1. **Não permite comparação entre múltiplos destinos/origens**: O gráfico está centrado em uma única unidade federativa, o que impede assim a análise entre todas as unidades.\n"
            "2. **Não permite comparação simultânea entre destino e origem**: Mesmo para um número pequeno de categorias a visualização não fica adequada.")

st.subheader("⚠️ Limitações", divider="orange")
st.markdown("1. **Simplificação geográfica**: Usa o centroide da unidade federativa como origem, o que omite variações "
            "dentro do próprio estado."
            "\n2. **Escala de cores pode esconder pequenas variações**: Estados com poucos candidatos podem parecer "
            "irrelevantes dependendo da paleta."
            "\n3. **Variação temporal**: O gráfico estático representa um único momento no tempo, não capta tendências "
            "ou sazonalidades ao longo do tempo."
            "\n4. **Agregação**: O uso de unidades federativas como unidade de análise esconde variações "
            "intraestaduais e pode levar à falácia ecológica")

st.subheader("🧭 Ideal para...", divider="blue")
st.markdown("1. **Identificação de padrões para segmentação**: Ajuda a definir agrupamentos geográficos para análises posteriores, podendo por exemplo auxiliar os itens 2. e 3.\n"
            "2. **Planejamento estratégico federal**: a delimitação de estratégias de política pública baseadas em "
            "origem e destino dos candidatos."
            "\n3. **Planejamento estratégico de universidades**: Compreender de onde vêm seus alunos para orientar "
            "políticas de apoio, expansão ou descentralização."
            "\n4. **Comunicação visual**: Devido a facilidade na compreensão, é interessante na incorporação em painéis"
            " espaciais.")

pacotes = set()
for nome_modulo in sys.modules:
    try:
        dist = importlib.metadata.distribution(nome_modulo)
        pacotes.add((dist.metadata['Name'], dist.version))
    except:
        continue

st.session_state["pacotes"] = {rf"**Nome:** :blue-badge[{nome}] na **versão:** :green-badge[{versao}]"
                               for nome, versao in sorted(pacotes)}
