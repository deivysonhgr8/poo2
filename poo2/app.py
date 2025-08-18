import streamlit as st
from escola import Escola, simular_dados, GerenciadorArquivos, Turma
from excecoes import (
    MatriculaInvalidaError,
    MatriculaJaExisteError,
    PessoaJaExisteError,
    DadosNaoEncontradosError,
)
import pandas as pd

# Inicializa a classe Escola e o Gerenciador de Arquivos no estado da sessão
if 'escola' not in st.session_state:
    gerenciador_arquivos = GerenciadorArquivos()
    st.session_state.escola = Escola('Construindo o Saber', gerenciador_arquivos)
    
    # Tenta carregar os dados salvos, se não existir, simula novos dados
    try:
        st.session_state.escola.carregar_dados()
        st.success('Dados carregados com sucesso!')
    except DadosNaoEncontradosError:
        simular_dados(st.session_state.escola)
        st.session_state.escola.salvar_dados()
        st.warning('Nenhum dado salvo encontrado. Dados de simulação foram gerados.')

st.title(f'Sistema de Gerenciamento da Escola {st.session_state.escola.nome_escola}')

# Sidebar para navegação
st.sidebar.title('Menu')
opcao = st.sidebar.radio('Escolha uma opção:', 
                         ['Cadastrar', 'Listar/Buscar', 'Análises Gráficas', 'Demonstração de Conceitos'])

if opcao == 'Cadastrar':
    st.header('Cadastramento')
    tipo_cadastro = st.radio('O que você deseja cadastrar?', ['Aluno', 'Funcionário'])

    if tipo_cadastro == 'Aluno':
        st.subheader('Cadastrar Novo Aluno')
        series_options = ['6º ano', '7º ano', '8º ano', '9º ano', '1ª série', '2ª série', '3ª série']
        with st.form('form_aluno', clear_on_submit=True):
            nome = st.text_input('Nome do Aluno', key='aluno_nome')
            idade = st.number_input('Idade do Aluno', min_value=0, key='aluno_idade')
            matricula = st.number_input('Matrícula do Aluno (8 dígitos)', min_value=0, key='aluno_matricula')
            serie = st.selectbox('Série do Aluno', options=series_options, key='aluno_serie')
            submit_button = st.form_submit_button('Cadastrar')

            if submit_button:
                if nome and idade is not None and matricula is not None and serie:
                    try:
                        st.session_state.escola.cadastrar_aluno(nome, int(idade), int(matricula), serie)
                        st.success('Aluno cadastrado com sucesso!')
                        st.session_state.escola.salvar_dados()
                    except (MatriculaInvalidaError, MatriculaJaExisteError, PessoaJaExisteError) as e:
                        st.error(f'Erro no cadastro: {e}')
                else:
                    st.warning('Por favor, preencha todos os campos.')

    else: # tipo_cadastro == 'Funcionário'
        st.subheader('Cadastrar Novo Funcionário')
        escolaridade_options = [
            'Sem escolaridade', 'Ensino fundamental incompleto', 'Ensino fundamental completo',
            'Ensino médio incompleto', 'Ensino médio completo', 'Ensino superior incompleto',
            'Ensino superior completo', 'Mestrado', 'Doutorado'
        ]
        with st.form('form_funcionario', clear_on_submit=True):
            nome = st.text_input('Nome do Funcionário', key='func_nome')
            idade = st.number_input('Idade do Funcionário', min_value=0, key='func_idade')
            cargo = st.text_input('Cargo', key='func_cargo')
            tipo_vinculo = st.selectbox('Tipo de Vínculo', ['CLT', 'PJ', 'Contrato', 'Temporário'], key='func_vinculo')
            escolaridade = st.selectbox('Escolaridade', options=escolaridade_options, key='func_escolaridade')
            submit_button = st.form_submit_button('Cadastrar')

            if submit_button:
                if nome and idade is not None and cargo and tipo_vinculo and escolaridade:
                    try:
                        st.session_state.escola.cadastrar_funcionario(nome, int(idade), cargo, tipo_vinculo, escolaridade)
                        st.success('Funcionário cadastrado com sucesso!')
                        st.session_state.escola.salvar_dados()
                    except PessoaJaExisteError as e:
                        st.error(f'Erro no cadastro: {e}')
                else:
                    st.warning('Por favor, preencha todos os campos.')

elif opcao == 'Listar/Buscar':
    st.header('Listar e Buscar')
    tipo_busca = st.radio('O que você deseja listar/buscar?', ['Alunos', 'Funcionários'])

    termo_busca = st.text_input(f'Buscar {tipo_busca} por nome ou matrícula:')
    
    if st.button('Listar Todos'):
        termo_busca = ''

    if tipo_busca == 'Alunos':
        st.subheader('Alunos Cadastrados')
        if termo_busca:
            encontrados = st.session_state.escola.buscar_aluno(termo_busca)
            if encontrados:
                for i, aluno in enumerate(encontrados, 1):
                    st.markdown(f"---")
                    st.markdown(f"**{i}.** {aluno.exibir_informacoes()}")
            else:
                st.info('Nenhum aluno encontrado.')
        else:
            if st.session_state.escola.alunos:
                df = st.session_state.escola.gerar_dataframe_alunos()
                df.index = df.index + 1
                st.dataframe(df)
            else:
                st.info('Nenhum aluno cadastrado.')

    else: # tipo_busca == 'Funcionários'
        st.subheader('Funcionários Cadastrados')
        if termo_busca:
            encontrados = st.session_state.escola.buscar_funcionario(termo_busca)
            if encontrados:
                for i, funcionario in enumerate(encontrados, 1):
                    st.markdown(f"---")
                    st.markdown(f"**{i}.** {funcionario.exibir_informacoes()}")
            else:
                st.info('Nenhum funcionário encontrado.')
        else:
            if st.session_state.escola.funcionarios:
                df = st.session_state.escola.gerar_dataframe_funcionarios()
                df.index = df.index + 1
                st.dataframe(df)
            else:
                st.info('Nenhum funcionário cadastrado.')

elif opcao == 'Análises Gráficas':
    st.header('Análises Gráficas')

    # Gráfico de Alunos e Funcionários
    st.subheader('Gráfico de Alunos e Funcionários')
    num_alunos = len(st.session_state.escola.alunos)
    num_funcionarios = len(st.session_state.escola.funcionarios)
    if num_alunos > 0 or num_funcionarios > 0:
        dados_quantidades = pd.DataFrame({
            'Categoria': ['Alunos', 'Funcionários'],
            'Quantidade': [num_alunos, num_funcionarios]
        })
        st.bar_chart(dados_quantidades.set_index('Categoria'), y='Quantidade', use_container_width=True)
    else:
        st.info("Não há dados suficientes para gerar o gráfico de alunos e funcionários.")

    # Gráfico de Alunos por Série (agora ordenado)
    st.subheader('Gráfico de Alunos por Série')
    if st.session_state.escola.alunos:
        df_alunos = st.session_state.escola.gerar_dataframe_alunos()
        series_order = ['6º ano', '7º ano', '8º ano', '9º ano', '1ª série', '2ª série', '3ª série']
        
        series_count = df_alunos['Série'].value_counts().reindex(series_order, fill_value=0)
        
        st.bar_chart(series_count, use_container_width=True)
    else:
        st.info("Nenhum aluno cadastrado para gerar o gráfico por série.")

    # --- Novos gráficos para funcionários ---
    st.subheader('Análises de Funcionários')
    if st.session_state.escola.funcionarios:
        df_funcionarios = st.session_state.escola.gerar_dataframe_funcionarios()

        st.write('#### Distribuição de Funcionários por Escolaridade')
        escolaridade_count = df_funcionarios['Escolaridade'].value_counts()
        st.bar_chart(escolaridade_count, use_container_width=True)

        st.write('#### Distribuição de Funcionários por Vínculo')
        vinculo_count = df_funcionarios['Vínculo'].value_counts()
        st.bar_chart(vinculo_count, use_container_width=True)

        st.write('#### Distribuição de Funcionários por Cargo')
        cargo_count = df_funcionarios['Cargo'].value_counts()
        st.bar_chart(cargo_count, use_container_width=True)
    else:
        st.info("Nenhum funcionário cadastrado para gerar os gráficos.")

elif opcao == 'Demonstração de Conceitos':
    st.header('Demonstração de Conceitos de POO')

    st.subheader('Polimorfismo em Ação')
    if st.session_state.escola.alunos or st.session_state.escola.funcionarios:
        st.markdown('A seguir, a função `exibir_informacoes_de_pessoas` chama a implementação correta do método `exibir_informacoes` para cada tipo de objeto (Aluno ou Funcionário):')
        
        # Cria uma lista mista de alunos e funcionários
        lista_mista = st.session_state.escola.alunos[:5] + st.session_state.escola.funcionarios[:5]
        
        if lista_mista:
            st.code(st.session_state.escola.exibir_informacoes_de_pessoas(lista_mista), language='markdown')
        else:
            st.info("Não há alunos ou funcionários suficientes para esta demonstração.")

    st.subheader('Composição e Delegação')
    st.markdown('A classe `Escola` agora **tem uma** instância de `GerenciadorArquivos` para salvar e carregar dados, delegando essa responsabilidade a ela. Além disso, a classe `Turma` é **composta por** uma lista de objetos `Aluno`.')

    if st.session_state.escola.alunos:
        st.markdown('### Exemplo da classe `Turma`')
        turma_exemplo = Turma('Turma A', '6º ano')
        
        # Adiciona alunos de forma segura usando a delegação
        alunos_da_serie_6 = [a for a in st.session_state.escola.alunos if a.serie == '6º ano']
        if alunos_da_serie_6:
            for aluno in alunos_da_serie_6[:3]: # Adiciona os 3 primeiros alunos do 6º ano
                turma_exemplo.adicionar_aluno(aluno)
            
            st.markdown(f"**Detalhes da Turma:**")
            st.markdown(f"- Nome: {turma_exemplo.nome_turma}")
            st.markdown(f"- Série: {turma_exemplo.serie}")
            st.markdown(f"- Total de alunos: {len(turma_exemplo)}")
            st.markdown(f"**Alunos na turma:**")
            for aluno in turma_exemplo.listar_alunos():
                st.markdown(f"- {aluno.nome}")
        else:
            st.info("Não há alunos do 6º ano para esta demonstração.")