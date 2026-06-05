from application.ports.repositorio_automato import AutomatonRepositoryPort
from application.dtos.automato import CriarAFNInputDTO, CriarAFNOutputDTO
from application.validators.validadores import validar_criar_afn_dto
from core import Estado, Simbolo, Transicao, Alfabeto, AFN

class CriarAFNUseCase:
    """Caso de uso responsável por instanciar, validar e salvar um novo AFN."""
    
    def __init__(self, repository: AutomatonRepositoryPort) -> None:
        self.repository = repository

    def execute(self, dto: CriarAFNInputDTO) -> CriarAFNOutputDTO:
        try:
            validar_criar_afn_dto(dto)

            estados = frozenset(Estado(label) for label in dto.estados)
            simbolos = frozenset(Simbolo(char) for char in dto.alfabeto)
            alfabeto = Alfabeto(simbolos)
            
            estado_inicial = Estado(dto.estado_inicial)
            estados_finais = frozenset(Estado(label) for label in dto.estados_finais)

            transicoes = set()
            for t in dto.transicoes:
                origem = Estado(t["origem"])
                destino = Estado(t["destino"])
                if t["simbolo"] in ("ε", "epsilon", "&", ""):
                    simbolo = Simbolo.epsilon()
                else:
                    simbolo = Simbolo(t["simbolo"])
                transicoes.add(Transicao(origem=origem, simbolo=simbolo, destino=destino))

            afn = AFN(
                nome=dto.nome,
                alfabeto=alfabeto,
                estados=estados,
                estado_inicial=estado_inicial,
                estados_finais=estados_finais,
                transicoes=frozenset(transicoes)
            )

            self.repository.save(afn)

            return CriarAFNOutputDTO(
                id_automato=afn.id,
                nome=afn.nome,
                sucesso=True
            )
        except Exception as e:
            return CriarAFNOutputDTO(
                id_automato=None,
                nome=dto.nome,
                sucesso=False,
                mensagem_erro=str(e)
            )
