class MatriculaInvalidaError(ValueError):
    """Exceção levantada quando o formato da matrícula é inválido."""
    pass

class MatriculaJaExisteError(ValueError):
    """Exceção levantada quando a matrícula já está cadastrada."""
    pass

class PessoaJaExisteError(ValueError):
    """Exceção levantada quando uma pessoa com o mesmo nome já existe."""
    pass

class DadosNaoEncontradosError(Exception):
    """Exceção levantada quando os arquivos de dados não podem ser carregados."""
    pass

class PessoaNaoEncontradaError(Exception):
    """Exceção levantada quando uma pessoa não é encontrada para exclusão."""
    pass