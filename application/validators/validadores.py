from core.exceptions.validacao import InvarianteVioladaException

def validar_criar_afn_dto(dto) -> None:
    """Valida sintática e estruturalmente os dados de entrada para criação de um AFN."""
    if not dto.nome or not isinstance(dto.nome, str):
        raise InvarianteVioladaException("O nome do autômato deve ser uma string não vazia.")
    
    if not isinstance(dto.alfabeto, list):
        raise InvarianteVioladaException("O alfabeto deve ser uma lista de símbolos.")
        
    for s in dto.alfabeto:
        if not isinstance(s, str) or len(s) != 1:
            raise InvarianteVioladaException(f"Símbolo do alfabeto '{s}' deve ser um único caractere.")
            
    if not isinstance(dto.estados, list) or not dto.estados:
        raise InvarianteVioladaException("O autômato deve possuir uma lista de estados não vazia.")
        
    for est in dto.estados:
        if not isinstance(est, str) or not est:
            raise InvarianteVioladaException("Os rótulos dos estados devem ser strings não vazias.")
            
    if dto.estado_inicial not in dto.estados:
        raise InvarianteVioladaException(f"O estado inicial '{dto.estado_inicial}' deve pertencer ao conjunto de estados.")
        
    if not isinstance(dto.estados_finais, list):
        raise InvarianteVioladaException("Os estados finais devem ser fornecidos como lista.")
        
    for f in dto.estados_finais:
        if f not in dto.estados:
            raise InvarianteVioladaException(f"O estado final '{f}' deve pertencer ao conjunto de estados.")
            
    if not isinstance(dto.transicoes, list):
        raise InvarianteVioladaException("As transições devem ser fornecidas como lista de dicionários.")
        
    for idx, t in enumerate(dto.transicoes):
        if not isinstance(t, dict) or not all(k in t for k in ("origem", "simbolo", "destino")):
            raise InvarianteVioladaException(f"Transição no índice {idx} é inválida. Deve conter 'origem', 'simbolo' e 'destino'.")
        if t["origem"] not in dto.estados:
            raise InvarianteVioladaException(f"Transição {t} possui origem '{t['origem']}' inexistente.")
        if t["destino"] not in dto.estados:
            raise InvarianteVioladaException(f"Transição {t} possui destino '{t['destino']}' inexistente.")
        if t["simbolo"] not in dto.alfabeto and t["simbolo"] not in ("ε", "epsilon", "&", ""):
            raise InvarianteVioladaException(f"Símbolo '{t['simbolo']}' na transição não pertence ao alfabeto e não é ε.")
