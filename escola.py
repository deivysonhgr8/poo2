from abc import ABC, abstractmethod
import pandas as pd
import random
import string
import os
import time
from excecoes import (
    MatriculaInvalidaError,
    MatriculaJaExisteError,
    PessoaJaExisteError,
    DadosNaoEncontradosError,
)

# Decorador para logar o tempo de execução de um método
def log_tempo_execucao(func):
    """Um decorador que loga o tempo de execução de uma função."""
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fim = time.time()
        print(f"O método '{func.__name__}' levou {fim - inicio:.4f} segundos para executar.")
        return resultado
    return wrapper

# Interface IPessoa define um contrato 
class IPessoa(ABC):
    @abstractmethod
    def exibir_informacoes(self):
        pass

# Herança: Pessoa é a superclasse
class Pessoa(IPessoa):
    def __init__(self, nome, idade):
        self._nome = nome
        self._idade = idade

    @property
    def nome(self):
        return self._nome

    @property
    def idade(self):
        return self._idade

    def exibir_informacoes(self):
        # Implementação polimórfica padrão
        return f"Nome: {self.nome} | Idade: {self.idade} anos"

# Herança: Aluno é uma Pessoa
class Aluno(Pessoa):
    def __init__(self, nome, idade, matricula, serie):
        super().__init__(nome, idade)
        self._matricula = matricula
        self._serie = serie

    @property
    def matricula(self):
        return self._matricula

    @property
    def serie(self):
        return self._serie

    # Polimorfismo: sobrescrita do método 
    def exibir_informacoes(self):
        return (
            f"**Aluno**\n"
            f"{super().exibir_informacoes()}\n"
            f"Matrícula: {self.matricula}\n"
            f"Série: {self.serie}"
        )

# Herança: Funcionario é uma Pessoa
class Funcionario(Pessoa):
    def __init__(self, nome, idade, cargo, tipo_vinculo, escolaridade):
        super().__init__(nome, idade)
        self._cargo = cargo
        self._tipo_vinculo = tipo_vinculo
        self._escolaridade = escolaridade

    @property
    def cargo(self):
        return self._cargo

    @property
    def tipo_vinculo(self):
        return self._tipo_vinculo

    @property
    def escolaridade(self):
        return self._escolaridade

    # Polimorfismo: sobrescrita do método 
    def exibir_informacoes(self):
        return (
            f"**Funcionário**\n"
            f"{super().exibir_informacoes()}\n"
            f"Cargo: {self.cargo}\n"
            f"Vínculo: {self.tipo_vinculo}\n"
            f"Escolaridade: {self.escolaridade}"
        )

# Composição: a classe Turma é composta por (tem uma) lista de alunos 
class Turma:
    def __init__(self, nome_turma, serie):
        self.nome_turma = nome_turma
        self.serie = serie
        self._alunos = []

    def adicionar_aluno(self, aluno):
        if not isinstance(aluno, Aluno):
            raise TypeError("Apenas objetos da classe Aluno podem ser adicionados à turma.")
        self._alunos.append(aluno)
    
    def listar_alunos(self):
        return self._alunos

    def __len__(self):
        return len(self._alunos)

# Classe para lidar com persistência de dados (SRP e DIP)
class GerenciadorArquivos:
    def salvar_dados(self, alunos, funcionarios):
        try:
            # Salva alunos
            if alunos:
                df_alunos = pd.DataFrame([
                    {'Nome': a.nome, 'Idade': a.idade, 'Matrícula': a.matricula, 'Série': a.serie}
                    for a in alunos
                ])
                df_alunos.to_csv('alunos.csv', index=False)
            elif os.path.exists('alunos.csv'):
                os.remove('alunos.csv')
            
            # Salva funcionários
            if funcionarios:
                df_funcionarios = pd.DataFrame([
                    {'Nome': f.nome, 'Idade': f.idade, 'Cargo': f.cargo, 'Vínculo': f.tipo_vinculo, 'Escolaridade': f.escolaridade}
                    for f in funcionarios
                ])
                df_funcionarios.to_csv('funcionarios.csv', index=False)
            elif os.path.exists('funcionarios.csv'):
                os.remove('funcionarios.csv')
        except Exception as e:
            raise IOError(f"Erro ao salvar dados: {e}")

    def carregar_dados(self):
        alunos, funcionarios = [], []
        try:
            if os.path.exists('alunos.csv'):
                df_alunos = pd.read_csv('alunos.csv')
                for _, row in df_alunos.iterrows():
                    alunos.append(Aluno(row['Nome'], row['Idade'], row['Matrícula'], row['Série']))
            
            if os.path.exists('funcionarios.csv'):
                df_funcionarios = pd.read_csv('funcionarios.csv')
                for _, row in df_funcionarios.iterrows():
                    funcionarios.append(Funcionario(row['Nome'], row['Idade'], row['Cargo'], row['Vínculo'], row['Escolaridade']))
            return alunos, funcionarios
        except Exception as e:
            raise DadosNaoEncontradosError(f"Erro ao carregar dados: {e}")

# Classe Escola adaptada para o Streamlit
class Escola:
    def __init__(self, nome_escola, gerenciador_arquivos):
        self.nome_escola = nome_escola
        self._alunos = []
        self._funcionarios = []
        self.gerenciador_arquivos = gerenciador_arquivos # Inversão de Dependência (DIP)

    @property
    def alunos(self):
        return self._alunos

    @property
    def funcionarios(self):
        return self._funcionarios

    def cadastrar_aluno(self, nome, idade, matricula, serie):
        # Lançamento de exceções personalizadas para melhor tratamento de erros 
        if len(str(matricula)) != 8:
            raise MatriculaInvalidaError('A matrícula deve ter exatamente 8 dígitos.')
        if any(aluno.matricula == matricula for aluno in self._alunos):
            raise MatriculaJaExisteError(f'A matrícula {matricula} já existe.')
        if any(aluno.nome.lower() == nome.lower() for aluno in self._alunos):
            raise PessoaJaExisteError(f'Já existe um aluno com o nome {nome}.')
        
        novo_aluno = Aluno(nome, idade, matricula, serie)
        self._alunos.append(novo_aluno)

    def cadastrar_funcionario(self, nome, idade, cargo, tipo_vinculo, escolaridade):
        # Lançamento de exceções personalizadas
        if any(f.nome.lower() == nome.lower() for f in self._funcionarios):
            raise PessoaJaExisteError(f'Já existe um funcionário com o nome {nome}.')
        
        novo_funcionario = Funcionario(nome, idade, cargo, tipo_vinculo, escolaridade)
        self._funcionarios.append(novo_funcionario)

    def buscar_aluno(self, termo):
        encontrados = [a for a in self._alunos if termo.lower() in a.nome.lower() or str(termo) == str(a.matricula)]
        return encontrados

    def buscar_funcionario(self, termo):
        encontrados = [f for f in self._funcionarios if termo.lower() in f.nome.lower()]
        return encontrados

    def gerar_dataframe_alunos(self):
        data = [{'Nome': a.nome, 'Idade': a.idade, 'Matrícula': a.matricula, 'Série': a.serie} for a in self._alunos]
        return pd.DataFrame(data)

    def gerar_dataframe_funcionarios(self):
        data = [{'Nome': f.nome, 'Idade': f.idade, 'Cargo': f.cargo, 'Vínculo': f.tipo_vinculo, 'Escolaridade': f.escolaridade} for f in self._funcionarios]
        return pd.DataFrame(data)

    @log_tempo_execucao
    def salvar_dados(self):
        self.gerenciador_arquivos.salvar_dados(self._alunos, self._funcionarios)
    
    @log_tempo_execucao
    def carregar_dados(self):
        self._alunos, self._funcionarios = self.gerenciador_arquivos.carregar_dados()

    # Exemplo de Polimorfismo: método que exibe informações de qualquer pessoa 
    def exibir_informacoes_de_pessoas(self, lista_pessoas):
        if not lista_pessoas:
            return "Nenhuma pessoa para exibir."
        
        resultado = []
        for pessoa in lista_pessoas:
            # O mesmo método 'exibir_informacoes()' se comporta de forma diferente
            # dependendo se o objeto é um Aluno, Funcionario ou Pessoa.
            resultado.append(pessoa.exibir_informacoes())
        return "\n\n---\n\n".join(resultado)


def simular_dados(escola, num_alunos=100, num_funcionarios=100):
    nomes_comuns = ['Ana', 'Bruno', 'Carla', 'Daniel', 'Eduarda', 'Felipe', 'Gabriela', 'Henrique', 'Isabela', 'João', 'Letícia', 'Marcos', 'Natália', 'Otávio', 'Patrícia', 'Ricardo', 'Sofia', 'Thiago', 'Vitória', 'Pedro']
    sobrenomes_comuns = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Pereira', 'Ferreira', 'Lima', 'Rodrigues', 'Almeida', 'Costa']
    series_options = ['6º ano', '7º ano', '8º ano', '9º ano', '1ª série', '2ª série', '3ª série']
    cargos = ['Professor', 'Secretário', 'Limpeza', 'Porteiro', 'Bibliotecário', 'Merendeira']
    tipos_vinculo = ['CLT', 'PJ', 'Contrato', 'Temporário']
    escolaridade_options = ['Sem escolaridade', 'Ensino fundamental incompleto', 'Ensino fundamental completo', 'Ensino médio incompleto', 'Ensino médio completo', 'Ensino superior incompleto', 'Ensino superior completo', 'Mestrado', 'Doutorado']

    matriculas_usadas = set()
    for i in range(num_alunos):
        nome = f"{random.choice(nomes_comuns)} {random.choice(sobrenomes_comuns)}"
        idade = random.randint(11, 18)
        
        matricula = 0
        while True:
            matricula = random.randint(10000000, 99999999)
            if matricula not in matriculas_usadas:
                matriculas_usadas.add(matricula)
                break
        
        serie = random.choice(series_options)
        try:
            escola.cadastrar_aluno(nome, idade, matricula, serie)
        except (MatriculaInvalidaError, MatriculaJaExisteError, PessoaJaExisteError) as e:
            print(f"Erro ao simular aluno: {e}")

    nome_coordenador = f"Maria {random.choice(sobrenomes_comuns)}"
    idade_coordenador = random.randint(30, 60)
    escolaridade_coordenador = random.choice(['Ensino superior completo', 'Mestrado', 'Doutorado'])
    try:
        escola.cadastrar_funcionario(nome_coordenador, idade_coordenador, 'Coordenador', 'CLT', escolaridade_coordenador)
    except PessoaJaExisteError as e:
        print(f"Erro ao simular coordenador: {e}")

    for i in range(num_funcionarios - 1):
        nome = f"{random.choice(nomes_comuns)} {random.choice(sobrenomes_comuns)}"
        idade = random.randint(25, 60)
        cargo = random.choice(cargos)
        tipo_vinculo = random.choice(tipos_vinculo)
        escolaridade = random.choice(escolaridade_options)
        try:
            escola.cadastrar_funcionario(nome, idade, cargo, tipo_vinculo, escolaridade)
        except PessoaJaExisteError as e:
            print(f"Erro ao simular funcionário: {e}")