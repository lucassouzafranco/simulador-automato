from abc import ABC, abstractmethod
from typing import Union
from core.entities.automato import Automato
from core.entities.gramatica import GramaticaRegular

class ExporterPort(ABC):
    """Porta genérica para exportação de autômatos ou gramáticas em diversos formatos."""
    
    @abstractmethod
    def export(self, entidade: Union[Automato, GramaticaRegular]) -> str:
        """
        Gera a representação textual formatada da entidade informada.
        
        Args:
            entidade: Uma entidade de Autômato ou Gramática Regular.
            
        Returns:
            str: O conteúdo exportado em formato string.
        """
        pass
