class DomainException(Exception):
    """Exceção base para todas as violações de regras do domínio formal."""
    pass


class EstadoInvalidoException(DomainException):
    """Lançada quando um estado referenciado não pertence ao conjunto de estados do autômato."""
    pass


class SimboloInvalidoException(DomainException):
    """Lançada quando um símbolo não faz parte do alfabeto do autômato."""
    pass


class InvarianteVioladaException(DomainException):
    """Lançada quando regras matemáticas formais do autômato ou gramática são violadas."""
    pass


class NaoDeterminismoException(DomainException):
    """Lançada quando há múltiplos caminhos ou transições vazias em um autômato determinístico."""
    pass


class GramaticaNaoRegularException(DomainException):
    """Lançada quando regras de produção de uma gramática violam o padrão de linearidade."""
    pass
