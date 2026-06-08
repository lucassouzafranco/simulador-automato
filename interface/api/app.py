import uuid
import json
import asyncio
from typing import List, Dict, Any, Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

# Core imports
from core import (
    Estado,
    Simbolo,
    Transicao,
    Alfabeto,
    Palavra,
    Automato,
    AFN,
    AFD,
    Variavel,
    Terminal,
    RegraProducao,
    GramaticaRegular,
)

# Infrastructure imports
from infrastructure import (
    InMemoryAutomatonRepository,
    InMemoryGrammarRepository,
    InMemoryDidacticTraceAdapter,
)

# Application imports
from application.use_cases import (
    CriarAFNUseCase,
    ConverterAFNParaAFDUseCase,
    SimularPalavraUseCase,
    MinimizarAFDUseCase,
    ConverterAFParaGRUseCase,
    ConverterGRParaAFUseCase,
)
from application.dtos import (
    CriarAFNInputDTO,
    ConverterAFNParaAFDInputDTO,
    MinimizarAFDInputDTO,
    SimularPalavraInputDTO,
    ConverterAFParaGRInputDTO,
    ConverterGRParaAFInputDTO,
)
from application.dtos.automato import PassoDidaticoDTO

# Import the new Async Queue adapter
from interface.api.adapter import AsyncQueueTraceAdapter

# Setup FastAPI App
app = FastAPI(
    title="Simulador de Autômatos API Didática",
    description="Motor de cálculo com Server-Sent Events (SSE) para acompanhamento didático",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global repositories (in-memory storage)
automaton_repo = InMemoryAutomatonRepository()
grammar_repo = InMemoryGrammarRepository()
trace_adapter = InMemoryDidacticTraceAdapter()

# Recursive function to sanitize frozensets, sets, and custom types to JSON-serializable types
def sanitize_frozensets(val: Any) -> Any:
    if isinstance(val, (frozenset, set)):
        return [sanitize_frozensets(x) for x in val]
    if isinstance(val, list):
        return [sanitize_frozensets(x) for x in val]
    if isinstance(val, dict):
        return {k: sanitize_frozensets(v) for k, v in val.items()}
    if isinstance(val, tuple):
        return tuple(sanitize_frozensets(x) for x in val)
    if isinstance(val, (Estado, Simbolo, Variavel, Terminal)):
        return str(val)
    return val

def serialize_automaton(afd: Automato) -> Dict:
    return sanitize_frozensets({
        "id": str(afd.id),
        "nome": afd.nome,
        "tipo": afd.tipo.value,
        "alfabeto": [str(s) for s in afd.alfabeto.simbolos],
        "estados": [str(e) for e in afd.estados],
        "estado_inicial": str(afd.estado_inicial),
        "estados_finais": [str(f) for f in afd.estados_finais],
        "transicoes": [
            {"origem": str(t.origem), "simbolo": str(t.simbolo), "destino": str(t.destino)}
            for t in afd.transicoes
        ]
    })

def serialize_grammar(grammar: GramaticaRegular) -> Dict:
    return sanitize_frozensets({
        "id": str(grammar.id),
        "linearidade": grammar.obter_linearidade().value,
        "simbolo_inicial": str(grammar.simbolo_inicial),
        "variaveis": [str(v) for v in grammar.variaveis],
        "terminais": [str(t) for t in grammar.terminais],
        "producoes": [
            {
                "esquerda": str(p.esquerda),
                "direita": [str(x) for x in p.direita] if not p.eh_vazia() else ["ε"]
            }
            for p in grammar.producoes
        ]
    })

def serialize_steps(steps: List[PassoDidaticoDTO]) -> List[Dict]:
    return [
        sanitize_frozensets({
            "indice": s.indice,
            "descricao": s.descricao,
            "dados_calculo": s.dados_calculo
        })
        for s in steps
    ]


# Pydantic Schemas for Requests
class TransitionInput(BaseModel):
    origem: str
    simbolo: str
    destino: str

class AutomatonCreateInput(BaseModel):
    nome: str
    alfabeto: List[str]
    estados: List[str]
    estado_inicial: str
    estados_finais: List[str]
    transicoes: List[TransitionInput]

class SimularPalavraInput(BaseModel):
    id_automato: uuid.UUID
    palavra: str

class ConvertNfaToDfaInput(BaseModel):
    id_automato: uuid.UUID

class MinimizeDfaInput(BaseModel):
    id_automato: uuid.UUID

class ConvertAfToGrInput(BaseModel):
    id_automato: uuid.UUID

class ProductionRuleInput(BaseModel):
    esquerda: str
    direita: List[str]

class ConvertGrToAfInput(BaseModel):
    simbolo_inicial: str
    variaveis: List[str]
    terminais: List[str]
    producoes: List[ProductionRuleInput]


# API Endpoints
@app.post("/api/automaton")
def create_automaton(data: AutomatonCreateInput):
    uc = CriarAFNUseCase(automaton_repo)
    dto = CriarAFNInputDTO(
        nome=data.nome,
        alfabeto=data.alfabeto,
        estados=data.estados,
        estado_inicial=data.estado_inicial,
        estados_finais=data.estados_finais,
        transicoes=[t.model_dump() for t in data.transicoes]
    )
    result = uc.execute(dto)
    if not result.sucesso:
        raise HTTPException(status_code=400, detail=result.mensagem_erro)
    
    return {
        "id_automato": str(result.id_automato),
        "nome": result.nome,
        "sucesso": result.sucesso
    }


# SSE Converter Route
@app.post("/api/convert/nfa-to-dfa")
async def convert_nfa_to_dfa(data: ConvertNfaToDfaInput):
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    adapter = AsyncQueueTraceAdapter(loop, queue)
    
    uc = ConverterAFNParaAFDUseCase(automaton_repo, adapter)
    dto = ConverterAFNParaAFDInputDTO(id_automato=data.id_automato)

    # Use Case execution in background thread
    async def run_use_case():
        try:
            return await asyncio.to_thread(uc.execute, dto)
        except Exception as e:
            return e

    use_case_task = asyncio.create_task(run_use_case())

    # SSE streaming generator
    async def event_generator():
        while not use_case_task.done() or not queue.empty():
            try:
                # Retrieve next tracked step from the queue
                step = await asyncio.wait_for(queue.get(), timeout=0.1)
                
                # Simulate the pedagogical streaming delay (200ms)
                await asyncio.sleep(0.2)
                
                step_data = sanitize_frozensets({
                    "indice": step.indice,
                    "descricao": step.descricao,
                    "dados_calculo": step.dados_calculo
                })
                yield f"data: {json.dumps(step_data)}\n\n"
                queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                yield f"event: error\ndata: {str(e)}\n\n"
                break

        # Yield the final resulting automaton once the task is finished
        try:
            result = await use_case_task
            if isinstance(result, Exception):
                raise result
            
            result_data = {
                "id_afd": str(result.id_afd),
                "automato": serialize_automaton(automaton_repo.get_by_id(result.id_afd))
            }
            yield f"event: result\ndata: {json.dumps(result_data)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/minimize")
def minimize_dfa(data: MinimizeDfaInput):
    trace_adapter.clean()
    uc = MinimizarAFDUseCase(automaton_repo, trace_adapter)
    dto = MinimizarAFDInputDTO(id_automato=data.id_automato)
    try:
        result = uc.execute(dto)
        return {
            "id_afd_minimizado": str(result.id_afd_minimizado),
            "automato": serialize_automaton(automaton_repo.get_by_id(result.id_afd_minimizado)),
            "passos_didaticos": serialize_steps(result.passos_didaticos)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/simulate")
def simulate_word(data: SimularPalavraInput):
    trace_adapter.clean()
    uc = SimularPalavraUseCase(automaton_repo, trace_adapter)
    dto = SimularPalavraInputDTO(id_automato=data.id_automato, palavra=data.palavra)
    try:
        result = uc.execute(dto)
        return {
            "aceita": result.aceita,
            "passos_didaticos": serialize_steps(result.passos_didaticos)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/convert/af-to-gr")
def convert_af_to_gr(data: ConvertAfToGrInput):
    trace_adapter.clean()
    uc = ConverterAFParaGRUseCase(automaton_repo, grammar_repo, trace_adapter)
    dto = ConverterAFParaGRInputDTO(id_automato=data.id_automato)
    try:
        result = uc.execute(dto)
        return {
            "id_gramatica": str(result.id_gramatica),
            "gramatica": serialize_grammar(grammar_repo.get_by_id(result.id_gramatica)),
            "passos_didaticos": serialize_steps(result.passos_didaticos)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/convert/gr-to-af")
def convert_gr_to_af(data: ConvertGrToAfInput):
    trace_adapter.clean()
    try:
        var_set = {v.strip() for v in data.variaveis if v.strip()}
        term_set = {t.strip() for t in data.terminais if t.strip()}
        
        variaveis = frozenset(Variavel(v) for v in var_set)
        terminais = frozenset(Terminal(t) for t in term_set)
        simbolo_inicial = Variavel(data.simbolo_inicial.strip())
        
        producoes = []
        for p in data.producoes:
            esq_var = Variavel(p.esquerda.strip())
            for dir_str in p.direita:
                dir_str = dir_str.strip()
                if not dir_str or dir_str in ("ε", "epsilon", "&"):
                    producoes.append(RegraProducao(esquerda=esq_var, direita=(Terminal("ε"),)))
                else:
                    parts = dir_str.split()
                    if len(parts) == 1:
                        part = parts[0]
                        if len(part) == 2 and part[0] in term_set and part[1] in var_set:
                            producoes.append(RegraProducao(esquerda=esq_var, direita=(Terminal(part[0]), Variavel(part[1]))))
                        elif len(part) == 2 and part[0] in var_set and part[1] in term_set:
                            producoes.append(RegraProducao(esquerda=esq_var, direita=(Variavel(part[0]), Terminal(part[1]))))
                        elif part in var_set:
                            producoes.append(RegraProducao(esquerda=esq_var, direita=(Variavel(part),)))
                        elif part in term_set:
                            producoes.append(RegraProducao(esquerda=esq_var, direita=(Terminal(part),)))
                        else:
                            raise ValueError(f"Símbolo desconhecido no lado direito: {part}")
                    elif len(parts) == 2:
                        p1, p2 = parts[0], parts[1]
                        if p1 in term_set and p2 in var_set:
                            producoes.append(RegraProducao(esquerda=esq_var, direita=(Terminal(p1), Variavel(p2))))
                        elif p1 in var_set and p2 in term_set:
                            producoes.append(RegraProducao(esquerda=esq_var, direita=(Variavel(p1), Terminal(p2))))
                        else:
                            raise ValueError(f"Produção linear não-regular inválida: {dir_str}")
                    else:
                        raise ValueError(f"Lado direito da produção excede o tamanho regular: {dir_str}")
                        
        grammar = GramaticaRegular(
            variaveis=variaveis,
            terminais=terminais,
            simbolo_inicial=simbolo_inicial,
            producoes=frozenset(producoes)
        )
        
        grammar_repo.save(grammar)
        
        uc = ConverterGRParaAFUseCase(automaton_repo, grammar_repo, trace_adapter)
        dto = ConverterGRParaAFInputDTO(id_gramatica=grammar.id)
        result = uc.execute(dto)
        
        return {
            "id_automato": str(result.id_automato),
            "automato": serialize_automaton(automaton_repo.get_by_id(result.id_automato)),
            "passos_didaticos": serialize_steps(result.passos_didaticos)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/docs")
def list_docs():
    import os
    base_path = os.getcwd()
    docs_dir = None
    for _ in range(4):
        candidate = os.path.join(base_path, 'docs')
        if os.path.isdir(candidate):
            docs_dir = candidate
            break
        base_path = os.path.dirname(base_path)
    
    if not docs_dir:
        raise HTTPException(status_code=404, detail="Diretório de documentação não encontrado.")
    
    metadata = {
        "arquitetura": "Arquitetura do Sistema",
        "camada_aplicacao": "Casos de Uso & Aplicação",
        "especificacoes_formais": "Especificações Formais",
        "instrucoes_execucao": "Instruções de Inicialização",
        "manual_tecnico": "Manual Técnico do Motor",
        "manual_usuario": "Manual de Operação",
        "modelo_dominio": "Modelo de Domínio & Estrutura"
    }
    
    available_docs = []
    try:
        for filename in sorted(os.listdir(docs_dir)):
            if filename.endswith(".md"):
                doc_id = filename[:-3]
                title = metadata.get(doc_id, doc_id.replace("_", " ").title())
                available_docs.append({
                    "id": doc_id,
                    "title": title,
                    "filename": filename
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler docs: {str(e)}")
        
    return available_docs


@app.get("/api/docs/{doc_id}")
def get_doc(doc_id: str):
    import os
    base_path = os.getcwd()
    docs_dir = None
    for _ in range(4):
        candidate = os.path.join(base_path, 'docs')
        if os.path.isdir(candidate):
            docs_dir = candidate
            break
        base_path = os.path.dirname(base_path)
        
    if not docs_dir:
        raise HTTPException(status_code=404, detail="Diretório de documentação não encontrado.")
        
    filename = f"{doc_id}.md"
    file_path = os.path.join(docs_dir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
        
    metadata = {
        "arquitetura": "Arquitetura do Sistema",
        "camada_aplicacao": "Casos de Uso & Aplicação",
        "especificacoes_formais": "Especificações Formais",
        "instrucoes_execucao": "Instruções de Inicialização",
        "manual_tecnico": "Manual Técnico do Motor",
        "manual_usuario": "Manual de Operação",
        "modelo_dominio": "Modelo de Domínio & Estrutura"
    }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "id": doc_id,
            "title": metadata.get(doc_id, doc_id.replace("_", " ").title()),
            "content": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler arquivo: {str(e)}")

# ==============================================================================
# INTEGRAÇÃO DOS ARQUIVOS ESTÁTICOS DO FRONTEND
# ==============================================================================
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web", "dist")

if os.path.exists(frontend_path):
    # Servir assets (JS, CSS, imagens)
    assets_dir = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Catch-all para servir o index.html (SPA routing) ou arquivos raiz estáticos
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Endpoint da API não encontrado.")
            
        file_path = os.path.join(frontend_path, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        return FileResponse(os.path.join(frontend_path, "index.html"))
