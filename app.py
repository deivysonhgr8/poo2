import streamlit as st
from escola import Escola, simular_dados, GerenciadorArquivos, Turma, log_tempo_execucao
from excecoes import (
    MatriculaInvalidaError,
    MatriculaJaExisteError,
    PessoaJaExisteError,
    DadosNaoEncontradosError,
)
import pandas as pd
import time

# Inicializa a classe Escola e o Gerenciador de Arquivos no estado da sessão
if 'escola' not in st.session_state:
    gerenciador_arquivos = GerenciadorArquivos()
    st.session_state.escola = Escola('Construindo o Saber', gerenciador_arquivos)
    
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
    st.header('Demonstração dos Conceitos de POO')

    st.markdown("Nesta seção, exploramos como os conceitos de Programação Orientada a Objetos foram aplicados no código da escola de forma prática.")
    st.markdown("---")

    # EXPANDER: HERANÇA E COMPOSIÇÃO
    with st.expander("Herança e Composição"):
        st.subheader("Herança: A relação 'É um'")
        st.markdown(
            "A **Herança** é um conceito onde uma classe filha (subclasse) herda atributos e métodos de uma classe pai (superclasse). Isso promove a reutilização de código."
        )
        st.markdown(
            "No seu código, a classe `Pessoa` é a superclasse, e as classes `Aluno` e `Funcionario` são as subclasses. Um `Aluno` **é uma** `Pessoa`, e um `Funcionario` **é uma** `Pessoa`."
        )
        st.code("""
# Herança: Pessoa é a superclasse
class Pessoa(IPessoa):
    ...
# Herança: Aluno é uma Pessoa
class Aluno(Pessoa):
    ...
# Herança: Funcionario é uma Pessoa
class Funcionario(Pessoa):
    ...
        """, language="python")

        st.subheader("Composição: A relação 'Tem um'")
        st.markdown(
            "A **Composição** é quando uma classe é 'composta' por objetos de outras classes. A classe **'mãe' tem um** objeto de outra classe como um de seus atributos."
        )
        st.markdown(
            "No seu código, a classe `Escola` **tem um** `GerenciadorArquivos` para lidar com a persistência de dados. A classe `Turma` **tem uma** lista de `Alunos`."
        )
        st.code("""
# Composição: a classe Escola 'tem um' GerenciadorArquivos
class Escola:
    def __init__(self, nome_escola, gerenciador_arquivos):
        self.gerenciador_arquivos = gerenciador_arquivos
        ...
# Composição: a classe Turma 'tem uma' lista de alunos
class Turma:
    def __init__(self, nome_turma, serie):
        self._alunos = []
        ...
        """, language="python")
        st.markdown("---")

    # EXPANDER: POLIMORFISMO
    with st.expander("Polimorfismo"):
        st.subheader("Polimorfismo: O 'múltiplas formas'")
        st.markdown(
            "O **Polimorfismo** permite que o mesmo método se comporte de maneira diferente dependendo do objeto que o chama."
        )
        st.markdown(
            "O método `exibir_informacoes()` está presente nas classes `Pessoa`, `Aluno` e `Funcionario`. Na demonstração abaixo, uma função chama esse método em uma lista que contém tanto `Alunos` quanto `Funcionarios`. O polimorfismo garante que o método correto será chamado para cada objeto, produzindo resultados diferentes."
        )
        if st.session_state.escola.alunos and st.session_state.escola.funcionarios:
            st.markdown('A seguir, a função `exibir_informacoes_de_pessoas` chama a implementação correta do método `exibir_informacoes` para cada tipo de objeto:')
            
            lista_mista = st.session_state.escola.alunos[:2] + st.session_state.escola.funcionarios[:2]
            
            if lista_mista:
                resultado_demonstracao = st.session_state.escola.exibir_informacoes_de_pessoas(lista_mista)
                st.code(resultado_demonstracao, language='markdown')
            else:
                st.info("Não há alunos ou funcionários suficientes para esta demonstração.")
        else:
            st.info("Não há alunos ou funcionários suficientes para esta demonstração.")
        st.markdown("---")

    # EXPANDER: DECORADORES
    with st.expander("Decoradores"):
        st.subheader("Decoradores: Adicionando funcionalidades")
        st.markdown(
            "Um **Decorador** é uma função que envolve outra função para estender ou modificar seu comportamento sem alterar o código original. É representado pelo `@`."
        )
        st.markdown(
            "O decorador `@log_tempo_execucao` é usado para medir e exibir o tempo que os métodos `salvar_dados` e `carregar_dados` levam para rodar."
        )
        st.code("""
# Decorador para logar o tempo de execução
def log_tempo_execucao(func):
    ...
    
class Escola:
    ...
    @log_tempo_execucao
    def salvar_dados(self):
        ...
    @log_tempo_execucao
    def carregar_dados(self):
        ...
        """, language="python")

        if st.button('Testar Decorador: Medir tempo de Salvamento'):
            start_time = time.time()
            st.session_state.escola.salvar_dados()
            end_time = time.time()
            st.success(f"Dados salvos! (Tempo de execução: {end_time - start_time:.4f} segundos)")
        st.markdown("---")

    # EXPANDER: EXCEÇÕES
    with st.expander("Exceções"):
        st.subheader("Exceções: Tratamento de erros")
        st.markdown(
            "**Exceções** são uma forma de lidar com erros previsíveis no código de forma controlada. Em vez de retornar um valor de erro, o código 'lança' uma exceção que pode ser 'capturada' por um bloco `try...except`."
        )
        st.markdown(
            "No seu código, as funções de cadastro não retornam mais `False` em caso de erro. Em vez disso, elas **lançam** exceções personalizadas como `MatriculaInvalidaError`, que são **capturadas** no arquivo `app.py` para exibir uma mensagem de erro clara ao usuário, sem travar o programa."
        )
        st.code("""
# No arquivo escola.py
def cadastrar_aluno(...):
    if len(str(matricula)) != 8:
        raise MatriculaInvalidaError('A matrícula deve ter 8 dígitos.')
    ...
# No arquivo app.py
try:
    st.session_state.escola.cadastrar_aluno(...)
    st.success('Aluno cadastrado!')
except MatriculaInvalidaError as e:
    st.error(f'Erro no cadastro: {e}')
        """, language="python")
        st.markdown("---")

    # EXPANDER: INTERFACES
    with st.expander("Interfaces"):
        st.subheader("Interfaces: O Contrato")
        st.markdown(
            "Uma **Interface** define um contrato: uma classe que implementa essa interface deve obrigatoriamente ter os métodos definidos nela. É como um 'contrato de comportamento'."
        )
        st.markdown(
            "A interface `IPessoa` garante que qualquer classe que a implemente (como `Pessoa`, `Aluno` e `Funcionario`) tenha um método `exibir_informacoes()`. Isso é crucial para o Polimorfismo funcionar corretamente."
        )
        st.code("""
from abc import ABC, abstractmethod
class IPessoa(ABC): # A classe ABC é usada para criar uma classe abstrata/interface
    @abstractmethod # Força a implementação do método
    def exibir_informacoes(self):
        pass
        """, language="python")
        st.markdown("---")

    # EXPANDER: SOLID
    with st.expander("Princípios SOLID"):
        st.subheader("Os Cinco Princípios do SOLID")
        st.markdown(
            "**SOLID** é um acrônimo para cinco princípios de design de software que ajudam a criar código mais robusto, flexível e fácil de manter."
        )
        st.markdown(
            "1.  **S (SRP - Single Responsibility Principle):** Uma classe deve ter apenas uma responsabilidade. A classe `GerenciadorArquivos` agora tem a única responsabilidade de salvar e carregar dados, separando-a da classe `Escola`."
        )
        st.markdown(
            "2.  **O (OCP - Open/Closed Principle):** As classes devem ser abertas para extensão, mas fechadas para modificação. Sua estrutura de herança permite adicionar novos tipos de pessoas (por exemplo, um `Voluntario`) sem alterar as classes existentes."
        )
        st.markdown(
            "3.  **L (LSP - Liskov Substitution Principle):** Objetos de uma subclasse devem poder ser substituídos por objetos da superclasse sem alterar a correção do programa. O método `exibir_informacoes_de_pessoas` demonstra isso, pois funciona corretamente com objetos `Aluno` e `Funcionario`."
        )
        st.markdown(
            "4.  **I (ISP - Interface Segregation Principle):** Interfaces devem ser pequenas e específicas. A interface `IPessoa` tem apenas um método (`exibir_informacoes`), mantendo-a coesa."
        )
        st.markdown(
            "5.  **D (DIP - Dependency Inversion Principle):** Classes de alto nível não devem depender de classes de baixo nível. Ambas devem depender de abstrações. A classe `Escola` agora depende da abstração (`gerenciador_arquivos`) e não da implementação concreta de como salvar os arquivos."
        )