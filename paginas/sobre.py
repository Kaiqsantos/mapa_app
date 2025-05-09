import streamlit as st

st.title("Autores")

st.markdown("""
### 👥💻⚙️ Equipe de Desenvolvimento

**Denise Nunes Viola**\\
Docente Permanente, Departamento de Estatística/IME/UFBA\\
viola@ufba.br

**Joel Costa Santana Junior**\\
Graduando em Estatística/UFBA\\
joelcsj003@gmail.com

**Kaíque Queirós dos Santos**\\
Graduando em Estatística/UFBA\\
kaiqueqs@ufba.br


### 👥🔎✅ Equipe de Garantia de Qualidade

**Filipe Oliveira Silva**\\
Graduando em Estatística/UFBA\\
silva.filipe@ufba.br

**Maiara Carvalho Santana**\\
Graduanda em Estatística/UFBA\\
maiara.carvalho57@gmail.com

**Natasha Sayuri Serra Minamigata**\\
Graduanda em Estatística/UFBA\\
natasha.minamigata@ufba.br


---""")

st.markdown(f"### 🛠️ Tecnologias Utilizadas \n - **Linguagem:** Python 3.12 \n - **Bibliotecas:** \n ")

st.markdown("  \n".join(st.session_state["pacotes"]))