import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import streamlit as st
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, ListedColormap, LinearSegmentedColormap
from matplotlib import colormaps
import geopandas as gpd
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import zipfile
import tempfile
import os


modo_escuro = st.session_state["escuro"]

padrão = None

## FORMAS
formas = df_formas = None

## TEMPO
precisão = data_inicio = hora_inicio = segundo_inicio = milisegundo_inicio = microsegundo_inicio = inicio = intervalo = None

## GRÁFICO
cor_titulo = transparente = cor_fundo = None

## ESCALA
minimo = valor_minimo = maximo = valor_maximo = None

## TIPO
modo = medida = estado = None

## ESCALA DE CORES
zero = corzero = None

container1 = st.container()
container2 = st.container()

with container2:
    confirmar = st.checkbox("Confirmar?")

with container1:
    ## DADOS
    arquivo = st.file_uploader("Carregue os arquivo", type="csv", accept_multiple_files=True, disabled=confirmar)

    if arquivo:
        padrão = st.segmented_control("Configuração Padrão", ["Sim", "Não"], disabled=confirmar, default=None)

    if not padrão is None:
        if padrão == "Não":
            ## FORMAS

            formas = st.segmented_control("Geometrias", ["Padrão", "Carregar"], disabled=confirmar, default=None)
            if not formas is None:
                if formas == "Carregar":
                    arquivo_formas = st.file_uploader("Envie todos os arquivos do shapefile (.cpg, .dbf, .prj, .shp, .shx)",
                                                      type=["cpg", "dbf", "prj", "shp", "shx"],
                                                      accept_multiple_files=True)
                    if len(arquivo_formas) == 5:
                        if sorted([_.name[-3:] for _ in arquivo_formas]) == ["cpg", "dbf", "prj", "shp", "shx"]:
                            shp_nome = [_.name for _ in arquivo_formas if _.name[-3:] == "shp"][0]
                            pasta_geo = tempfile.mkdtemp()
                            for i in arquivo_formas:
                                with open(os.path.join(pasta_geo, i.name), "wb") as f:
                                    f.write(i.getbuffer())
                            df_formas = gpd.read_file(os.path.join(pasta_geo, shp_nome))
                            st.divider()
                else:
                    df_formas = st.session_state["gdf"].copy().reset_index()
                    st.divider()

            ## TEMPO

            if not df_formas is None:
                if len(arquivo) > 1:
                    precisão = st.select_slider("Precisão", options=range(8), format_func=lambda option: ["Microssegundos", "Milissegundos", "Segundos", "Minutos", "Horas", "Dias", "Meses", "Anos"][option], disabled=confirmar)

                    if not precisão is None:
                        data_inicio = st.date_input("Data Inicial:", value=None, format="DD-MM-YYYY", disabled=confirmar)

                    if not data_inicio is None:
                        hora_inicio = st.time_input("Hora Inicial:", value=None, step=60, disabled=confirmar) if precisão <= 4 else time(0,0)

                    if not hora_inicio is None:
                        segundo_inicio = st.slider("Segundos:", value=None, min_value=0, max_value=59, disabled=confirmar) if precisão <= 2 else "00"

                    if not segundo_inicio is None:
                        milisegundo_inicio = st.slider("Milissegundos:", min_value=0, max_value=999, value=None, disabled=confirmar) if precisão <= 1 else "000"

                    if not milisegundo_inicio is None:
                        microsegundo_inicio = st.slider("Microssegundos:", min_value=0, max_value=999, value=None, disabled=confirmar) if precisão <= 0 else "000"


                    if not microsegundo_inicio is None:
                        inicio = datetime.strptime(f"{data_inicio.strftime("%d-%m-%Y")} {hora_inicio.strftime("%H-%M")}-{segundo_inicio}.{str(milisegundo_inicio).zfill(3)}{str(microsegundo_inicio).zfill(3)}", r"%d-%m-%Y %H-%M-%S.%f")
                        intervalo = st.number_input(f"Intervalo (a cada X {["Microssegundos", "Milissegundos", "Segundos", "Minutos", "Horas", "Dias", "Meses", "Anos"][precisão]}):", value=None, min_value=1, step=1, disabled=confirmar)
                        st.divider()

                else:
                    inicio = False
                    intervalo = False

            ## Gráfico

            if not intervalo is None:
                cor_titulo = st.color_picker("Cor do titulo", "#FFF", disabled=confirmar)

            if not cor_titulo is None:
                if cor_titulo != "#FFF":
                    transparente = st.selectbox("Fundo transparente", ("Sim", "Não"), disabled=confirmar)

            if not transparente is None:
                cor_fundo = st.color_picker("Cor do fundo", "#FFF", disabled=confirmar) if transparente == "Não" else False
                st.divider()

            ## ESCALA

            if not cor_fundo is None:
                if cor_fundo != "#FFF":
                    minimo = st.selectbox("Como definir o mínimo?", ("Calculado", "Informado"), index=0, disabled=confirmar)

            if not minimo is None:
                valor_minimo = st.number_input("Mínimo: ", value=None, disabled=confirmar) if minimo == "Informado" else True

            if not valor_minimo is None:
                maximo = st.selectbox("Como definir o máximo?", ("Calculado", "Informado"), index=0, disabled=confirmar)

            if not maximo is None:
                valor_maximo = st.number_input("Máximo: ", disabled=confirmar) if maximo == "Informado" else True
                st.divider()


            ## TIPO

            if not valor_maximo is None:
                modo = st.segmented_control("Âncora:", ["Origem", "Destino"], disabled=confirmar)

            if not modo is None:
                medida = st.radio("Medida:", ["Elemento", "Geral"], disabled=confirmar)

            if not medida is None:
                estado = st.segmented_control("Elemento:", sorted(df_formas.iloc[:,0].values.tolist()), disabled=confirmar) if medida == "Elemento" else True
                st.divider()


            ## ESCALA DE CORES

            if not estado is None:
                zero = st.pills("Diferenciar Zero:", ["Sim", "Não"], disabled=confirmar)

            if not zero is None:
                corzero = st.color_picker("Cor dos vetores iguais a 0", "#FFF", disabled=confirmar) if zero == "Sim" else False
                st.divider()

        else:
            # USADO
            df_formas = st.session_state["gdf"].copy().reset_index()

            #USADO
            precisão = 7
            #USADO
            inicio = datetime.now()
            #USADO
            intervalo = 1


            #USADO
            cor_titulo = st.session_state["cores"]['tex'][modo_escuro]
            #USADO
            cor_fundo = False

            # USADO
            minimo = "Informado"
            # USADO
            valor_minimo = 0
            # USADO
            maximo = "Informado"
            # USADO
            valor_maximo = 100


            modo = "Origem"
            medida = "Elemento"
            estado = "BA"


            zero = "Sim"
            corzero = "#ff80c0"


if confirmar and not corzero is None:
    gerar = st.toggle("Gerar gráfico")
    if gerar:
        fig, ax = plt.subplots(figsize=(10, 8))

        fig.patch.set_facecolor(cor_fundo if cor_fundo else 'none')

        for i in ax.spines.values():
            i.set_color(cor_titulo)
        ax.tick_params(axis='both', colors=cor_titulo)
        ax.xaxis.label.set_color(cor_titulo)
        ax.yaxis.label.set_color(cor_titulo)
        ax.set(xlabel='Longitude', ylabel='Latitude', facecolor=cor_fundo if cor_fundo else 'none')

        dfs = [pd.read_csv(_,index_col=0) for _ in arquivo]
        df_formas = df_formas.copy().sort_values(by=df_formas.columns[0]).reset_index(drop=True)
        pontos_resumo = df_formas.copy().to_crs(epsg=5880).centroid.to_crs(epsg=4674).to_frame()
        pontos_resumo.index = df_formas.iloc[:,0].values
        df_formas.copy().plot(ax=ax, color='lightgray', edgecolor='black')
        scat = ax.scatter(pontos_resumo.iloc[:,0].x, pontos_resumo.iloc[:,0].y,
                          c="#bc6c25", edgecolors='black', linewidths=0.5, marker='o', s=20)

        title = ax.text(0.5, 1.05, "", transform=ax.transAxes, ha="center", va="bottom",
                        bbox={'alpha': 0}, color=cor_titulo)
        minimo_real = np.array([b.min().min() for b in dfs]).min() if minimo == "Calculado" else np.array(valor_minimo)
        maximo_real = np.array([b.min().min() for b in dfs]).min() if maximo == "Calculado" else np.array(valor_maximo)

        ## SETAS

        Q = {}
        if medida == "Elemento":
            for i in df_formas.iloc[:,0]:
                if i != estado:
                    if modo == "Origem":
                        Q[i] = ax.quiver(pontos_resumo.loc[estado,0].x,
                                         pontos_resumo.loc[estado,0].y,
                                         pontos_resumo.loc[i,0].x-pontos_resumo.loc[estado,0].x,
                                         pontos_resumo.loc[i,0].y-pontos_resumo.loc[estado,0].y,
                                         angles='xy', scale_units='xy', scale=1)
                    else:
                        Q[i] = ax.quiver(pontos_resumo.loc[i, 0].x,
                                         pontos_resumo.loc[i, 0].y,
                                         pontos_resumo.loc[estado, 0].x - pontos_resumo.loc[i, 0].x,
                                         pontos_resumo.loc[estado, 0].y - pontos_resumo.loc[i, 0].y,
                                         angles='xy', scale_units='xy', scale=1)

        ## ESCALA DE CORES
        cmap_meu = LinearSegmentedColormap.from_list("", np.array([[0., 0., 1.], [0., 1., 1.],
                                                                   [0., .5, 0.], [1., 1., 0.], [1., 0., 0.]]))
        cmap = ListedColormap(np.vstack(([1., .5, .75, 1.], cmap_meu(np.linspace(0, 1, 256,
                                                                                 endpoint=True)))))

        bounds = np.insert(np.linspace(1, 100, 256, endpoint=True), 0, 0)
        sm = ScalarMappable(cmap=cmap, norm=BoundaryNorm(bounds, cmap.N))

        ## LEGENDA DE CORES
        cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.05)
        cbar.set_label('Número de indivíduos', color=st.session_state["cores"]['tex'][modo_escuro])
        cbar.set_ticks(np.linspace(0, 100, 11, endpoint=True))
        cbar.ax.tick_params(axis='both', colors=st.session_state["cores"]['tex'][modo_escuro])
        cbar.minorticks_off()

        ## ANIMAÇÃO
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
                title.set_text(f"Mapa do fluxo entre a {"UF de origem -> UF de destino" if modo=="Origem" else "UF de destino <- UF de origem"} {(tempostr[:-3 if precisão == 1 else len(tempostr)])}")
            else:
                title.set_text(
                    f"Mapa do fluxo entre a {"UF de origem -> UF de destino" if modo == "Origem" else "UF de destino <- UF de origem"}")

            for j in df_formas.iloc[:, 0]:
                if medida == "Elemento":
                    if modo == "Origem":
                        if j != estado:
                            Q[j].set_color(sm.to_rgba(dfs[frame].loc[j,estado]))
                    else:
                        if j != estado:
                            Q[j].set_color(sm.to_rgba(dfs[frame].loc[estado,j]))

            plt.savefig(os.path.join(frame_dir, f"frame_{frame:04d}.png"))

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

        ani = animation.FuncAnimation(fig, update, frames=len(arquivo), interval=1000, blit=True)
        ani.save(filename=tmp_apng.name, writer="pillow", dpi=100)
        ani.save(filename=tmp_gif.name, writer="pillow", dpi=100)

        with zipfile.ZipFile(path_zip, "w") as zf:
            zf.write(path_apng, arcname="animacao.apng")
            zf.write(path_gif, arcname="animacao.gif")

            for filename in sorted(os.listdir(frame_dir)):
                zf.write(os.path.join(frame_dir, filename), arcname=os.path.join("frames", filename))

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

