import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import streamlit as st
from PIL import Image
import pandas as pd
import geopandas as gpd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, ListedColormap, LinearSegmentedColormap
from matplotlib import colormaps
from datetime import datetime, time, date
from dateutil.relativedelta import relativedelta
import zipfile
import tempfile
import os


modo_escuro = st.session_state["escuro"]
fig, ax = plt.subplots(figsize=(10,8))

titulo = ax.set_title('', color=st.session_state["cores"]['tex'][modo_escuro])
fig.patch.set_facecolor('none')

for i in ax.spines.values():
    i.set_color(st.session_state["cores"]['tex'][modo_escuro])
st.session_state['gdf'].copy().plot(ax=ax, color='lightgray', edgecolor='black')
ax.tick_params(axis='both', colors=st.session_state["cores"]['tex'][modo_escuro])
ax.xaxis.label.set_color(st.session_state["cores"]['tex'][modo_escuro])
ax.yaxis.label.set_color(st.session_state["cores"]['tex'][modo_escuro])
ax.set(xlabel='Longitude', ylabel='Latitude', facecolor='none')

estado=None

confirmar = st.checkbox("Confirmar?")

arquivo = st.file_uploader("Carregue os arquivos", type="csv", accept_multiple_files=True, disabled=confirmar)
if arquivo:
    formas = st.segmented_control("Geometrias", ["Padrão", "Carregar"], disabled=confirmar, default="Padrão")
    if formas:
        arquivos_formas = False if formas == "Carregar" else True
        if not arquivos_formas is None:
            precisão = st.select_slider("Precisão", options=range(8), format_func=lambda option: ["Microssegundos", "Milissegundos", "Segundos", "Minutos", "Horas", "Dias", "Meses", "Anos"][option], disabled=confirmar, value=7) if len(arquivo) > 1 else True
            if not precisão is None:
                data_inicio = st.date_input("Data Inicial:", value="today", format="DD-MM-YYYY", disabled=confirmar) if len(arquivo)>1 else date(1,1,1)
                if not data_inicio is None:
                    hora_inicio = st.time_input("Hora Inicial:", value=None, step=60, disabled=confirmar) if len(arquivo)>1 and precisão <= 4 else time(0,0)
                    if not hora_inicio is None:
                        segundo_inicio = st.slider("Segundos:", min_value=0, max_value=59, disabled=confirmar) if len(arquivo)>1 and precisão <= 2 else "00"
                        if not segundo_inicio is None:
                            milisegundo_inicio = st.slider("Milissegundos:", min_value=0, max_value=999, value=None, disabled=confirmar) if len(arquivo)>1 and precisão <= 1 else "000"
                            if not milisegundo_inicio is None:
                                microsegundo_inicio = st.slider("Microssegundos:", min_value=0, max_value=999, value=None, disabled=confirmar) if len(arquivo)>1 and precisão <= 0 else "000"
                                if not microsegundo_inicio is None:
                                    intervalo = st.number_input(f"Intervalo (a cada X {["Microssegundos", "Milissegundos", "Segundos", "Minutos", "Horas", "Dias", "Meses", "Anos"][precisão]}):", value=1, min_value=1, step=1, disabled=confirmar) if len(arquivo)>1 else 0
                                    if not intervalo is None:
                                        inicio = datetime.strptime(f"{data_inicio.strftime("%d-%m-%Y")} {hora_inicio.strftime("%H-%M")}-{segundo_inicio}.{str(milisegundo_inicio).zfill(3)}{str(microsegundo_inicio).zfill(3)}", r"%d-%m-%Y %H-%M-%S.%f") if len(arquivo)>1 else False
                                        velocidade = st.number_input("Velocidade:", min_value=0, step=1, disabled=confirmar, value=1000) if len(arquivo)>1 else 1
                                        if velocidade:
                                            modo = st.segmented_control("Âncora:", ["Origem", "Destino"], disabled=confirmar)
                                            if modo:
                                                minimo = st.selectbox("Como definir o mínimo?", ("Calculado", "Informado"), index=0, disabled=confirmar)
                                                if minimo:
                                                    valor_minimo = st.number_input("Mínimo: ", value=None, disabled=confirmar) if minimo == "Informado" else True
                                                    if not valor_minimo is None:
                                                        maximo = st.selectbox("Como definir o máximo?", ("Calculado", "Informado"), index=0, disabled=confirmar)
                                                        if maximo:
                                                            valor_maximo = st.number_input("Máximo: ", value=None, disabled=confirmar) if maximo == "Informado" else True
                                                            if not valor_maximo is None:
                                                                resumo = st.selectbox("Ponto resumo da forma:", ("Centroide", "Centro Mediano", "Borda", "Inacessível", "Representativo", "Aleatório", "Centro"), index=0, disabled=confirmar)
                                                                if resumo:
                                                                    cor1 = st.color_picker("Cor dos Centróides", "#FFF", disabled=confirmar)
                                                                    if cor1 != "#FFF":
                                                                        zero = st.pills("Diferenciar Zero:", ["Sim", "Não"], disabled=confirmar)
                                                                        if zero:
                                                                            corzero = st.color_picker("Cor dos vetores iguais a 0", "#FFF", disabled=confirmar) if zero == "Sim" else "#FFFFFF"
                                                                            if corzero != "#FFF":
                                                                                escaladecores = st.multiselect('Escolha uma escala de Cor', ["Padrão"] + list(colormaps), max_selections=1, disabled=confirmar)
                                                                                if escaladecores:
                                                                                    medida = st.radio("Medida:", ["Elemento", "Geral"], disabled=confirmar)
                                                                                    if medida:
                                                                                        if formas == "Padrão":
                                                                                            df_formas = st.session_state["gdf"].copy().reset_index()
                                                                                        estado = st.segmented_control("Elemento:", sorted(df_formas.iloc[:,0].values.tolist()), disabled=confirmar) if medida == "Elemento" else True


if confirmar and not estado is None:
    gerar = st.toggle("Gerar gráfico")
    if gerar:
        dfs = [pd.read_csv(i,index_col=0) for i in arquivo]
        df_formas = df_formas.copy().sort_values(by=df_formas.columns[0]).reset_index(drop=True)
        if resumo == "Centroide":
            pontos_resumo = df_formas.copy().to_crs(epsg=5880).centroid.to_crs(epsg=4674).to_frame()
        else:
            pass
            pontos_resumo = ''
        pontos_resumo.index = df_formas.iloc[:,0].values
        df_formas.copy().plot(ax=ax, color='lightgray', edgecolor='black')
        scat = ax.scatter(pontos_resumo.iloc[:,0].x, pontos_resumo.iloc[:,0].y,
                          c=cor1, edgecolors='black', linewidths=0.5, marker='o', s=20)

        title = ax.text(0.5, 1.05, "", transform=ax.transAxes, ha="center", va="bottom",
                        bbox={'alpha': 0}, color=st.session_state["cores"]['tex'][modo_escuro])
        minimo_real = np.array([b.min().min() for b in dfs]).min() if minimo == "Calculado" else np.array(valor_minimo)
        maximo_real = np.array([b.min().min() for b in dfs]).min() if maximo == "Calculado" else np.array(valor_maximo)
        Q = {}
        if medida == "Elemento":
            if modo == "Origem":
                for i in df_formas.iloc[:,0]:
                    if i != estado:
                        Q[i] = ax.quiver(pontos_resumo.loc[estado,0].x,
                                         pontos_resumo.loc[estado,0].y,
                                         pontos_resumo.loc[i,0].x-pontos_resumo.loc[estado,0].x,
                                         pontos_resumo.loc[i,0].y-pontos_resumo.loc[estado,0].y,
                                         angles='xy', scale_units='xy', scale=1)
            else:
                for i in df_formas.iloc[:, 0]:
                    if i != estado:
                        Q[i] = ax.quiver(pontos_resumo.loc[i, 0].x,
                                         pontos_resumo.loc[i, 0].y,
                                         pontos_resumo.loc[estado, 0].x - pontos_resumo.loc[i, 0].x,
                                         pontos_resumo.loc[estado, 0].y - pontos_resumo.loc[i, 0].y,
                                         angles='xy', scale_units='xy', scale=1)

        cmap_meu = LinearSegmentedColormap.from_list("", np.array([[0., 0., 1.], [0., 1., 1.],
                                                                   [0., .5, 0.], [1., 1., 0.], [1., 0., 0.]]))
        cmap = ListedColormap(np.vstack(([1., .5, .75, 1.], cmap_meu(np.linspace(0, 1, 256,
                                                                                 endpoint=True)))))

        bounds = np.insert(np.linspace(1, 100, 256, endpoint=True), 0, 0)

        sm = ScalarMappable(cmap=cmap, norm=BoundaryNorm(bounds, cmap.N))
        cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.05)
        cbar.set_label('Número de indivíduos', color=st.session_state["cores"]['tex'][modo_escuro])
        cbar.set_ticks(np.linspace(0, 100, 11, endpoint=True))
        cbar.ax.tick_params(axis='both', colors=st.session_state["cores"]['tex'][modo_escuro])
        cbar.minorticks_off()
        def update(frame):
            if len(arquivo) >1:
                tempo = inicio + relativedelta(years=intervalo * frame if precisão == 7 else 0,
                                               months=intervalo * frame if precisão == 6 else 0,
                                               days=intervalo * frame if precisão == 5 else 0,
                                               hours=intervalo * frame if precisão == 4 else 0,
                                               minutes=intervalo * frame if precisão == 3 else 0,
                                               seconds=intervalo * frame if precisão == 2 else 0,
                                               microseconds=intervalo * (1000 if precisão==1 else 1) * frame if precisão <= 1 else 0)
                tempostr = tempo.strftime(
                    f"{" Dia:%d" if precisão <= 5 else ""}{" Mês:%m" if precisão <= 6 else ""}"
                    f"{" Ano:%Y" if precisão <= 7 else ""}{" hora:%H" if precisão <= 4 else ""}"
                    f"{" min:%M" if precisão <= 3 else ""}{" seg:%S" if precisão <= 2 else ""}"
                    f"{" ms:%f" if precisão <= 1 else ""}")
                tempostr = "\nPeriodo:" + tempostr
            title.set_text(f"Mapa do fluxo entre a {"UF de origem -> UF de destino" if modo=="Origem" else "UF de destino <- UF de origem"}"
                           f"{(tempostr[:-3 if precisão == 1 else len(tempostr)]) if len(arquivo) > 1 else ""}")

            for i in df_formas.iloc[:,0]:
                if medida == "Elemento":
                    if modo == "Origem":
                        if i != estado:
                            Q[i].set_color(sm.to_rgba(dfs[frame].loc[i,estado]))
                    else:
                        if i != estado:
                            Q[i].set_color(sm.to_rgba(dfs[frame].loc[estado,i]))
            frame_path = os.path.join(frame_dir, f"frame_{frame:04d}.png")
            plt.savefig(frame_path)
            # tmp_png = tempfile.NamedTemporaryFile(suffix=".png", mode="w", delete=False)
            # plt.savefig(tmp_png.name)
            # zf.write(tmp_png.name)
            # tmp_png.close()
            return title, *Q.values(),


        tmp_apng = tempfile.NamedTemporaryFile(suffix=".apng", delete=False)
        tmp_gif = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
        tmp_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        frame_dir = tempfile.mkdtemp()

        path_apng = tmp_apng.name
        path_gif = tmp_gif.name
        path_zip = tmp_zip.name

        tmp_apng.close()
        tmp_gif.close()
        tmp_zip.close()

        ani = animation.FuncAnimation(fig, update, frames=len(arquivo), interval=velocidade)
        ani.save(filename=tmp_apng.name, writer="pillow", dpi=100)
        ani.save(filename=tmp_gif.name, writer="pillow", dpi=100)

        with zipfile.ZipFile(path_zip, "w") as zf:
            zf.write(path_apng, arcname="animacao.apng")
            zf.write(path_gif, arcname="animacao.gif")

            for filename in sorted(os.listdir(frame_dir)):
                frame_path = os.path.join(frame_dir, filename)
                zf.write(frame_path, arcname=os.path.join("frames", filename))

        st.image(path_apng)

        with open(path_apng, "rb") as file:
            arquivo_apng = file.read()
        with open(path_gif, "rb") as file:
            arquivo_gif = file.read()
        with open(path_zip, "rb") as file:
            arquivo_zip = file.read()

        st.download_button(label="📥 Baixar APNG", data=arquivo_apng, file_name="animacao.apng", mime="image/apng")
        st.download_button(label="📥 Baixar GIF", data=arquivo_gif, file_name="animacao.gif", mime="image/gif")
        st.download_button(label="📦 Baixar ZIP", data=arquivo_zip, file_name="animacoes.zip", mime="application/zip")

