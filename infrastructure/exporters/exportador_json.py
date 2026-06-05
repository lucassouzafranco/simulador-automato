import json
from typing import Union
from application.ports.exportador import ExporterPort
from core.entities.automato import Automato
from core.entities.gramatica import GramaticaRegular

class JsonExporter(ExporterPort):
    """Implementação concreta de exportador estruturado em JSON (.json)."""
    
    def export(self, entidade: Union[Automato, GramaticaRegular]) -> str:
        if isinstance(entidade, Automato):
            data = {
                "id": str(entidade.id),
                "nome": entidade.nome,
                "tipo": entidade.tipo.value,
                "alfabeto": sorted(str(s) for s in entidade.alfabeto.simbolos),
                "estados": sorted(str(e) for e in entidade.estados),
                "estado_inicial": str(entidade.estado_inicial),
                "estados_finais": sorted(str(e) for e in entidade.estados_finais),
                "transicoes": [
                    {
                        "origem": str(t.origem),
                        "simbolo": str(t.simbolo),
                        "destino": str(t.destino)
                    }
                    for t in sorted(
                        entidade.transicoes,
                        key=lambda x: (str(x.origem), str(x.simbolo), str(x.destino))
                    )
                ]
            }
        elif isinstance(entidade, GramaticaRegular):
            data = {
                "id": str(entidade.id),
                "linearidade": entidade.obter_linearidade().value,
                "simbolo_inicial": str(entidade.simbolo_inicial),
                "variaveis": sorted(str(v) for v in entidade.variaveis),
                "terminais": sorted(str(t) for t in entidade.terminais),
                "producoes": [
                    {
                        "esquerda": str(p.esquerda),
                        "direita": [str(x) for x in p.direita] if p.direita else ["ε"]
                    }
                    for p in sorted(
                        entidade.producoes,
                        key=lambda x: (str(x.esquerda), "".join(str(i) for i in x.direita))
                    )
                ]
            }
        else:
            raise TypeError("Tipo de entidade não suportado para exportação em JSON.")
            
        return json.dumps(data, indent=4, ensure_ascii=False)
