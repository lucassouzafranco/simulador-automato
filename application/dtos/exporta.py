from dataclasses import dataclass
from uuid import UUID
from typing import Optional

@dataclass(frozen=True)
class ExportarResultadoInputDTO:
    id_entidade: UUID
    tipo_entidade: str  # "AUTOMATO" ou "GRAMATICA"
    formato: str        # "TXT" ou "JSON"

@dataclass(frozen=True)
class ExportarResultadoOutputDTO:
    conteudo: str
    caminho_arquivo: Optional[str] = None
