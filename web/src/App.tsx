import React, { useState, useEffect, useRef } from 'react';
import {
  ThemeProvider,
  Page,
  Grid,
  Card,
  Heading,
  Text,
  Button,
  Input,
  Label,
  Badge,
  Separator,
  Stack,
} from './design-system';
import './design-system/tokens/tokens.css';
import './App.css';

const BACKEND_URL = 'http://localhost:8000';

interface Transicao {
  origem: string;
  simbolo: string;
  destino: string;
}

interface RegraProducao {
  esquerda: string;
  direita: string[];
}

interface PassoDidatico {
  indice: number;
  descricao: string;
  dados_calculo: Record<string, any>;
}

function App() {
  // Navigation / Tabs
  const [activeTab, setActiveTab] = useState<'automato' | 'gramatica'>('automato');
  
  // Automaton Form State
  const [nome, setNome] = useState('M1');
  const [estados, setEstados] = useState('q0, q1, q2');
  const [alfabeto, setAlfabeto] = useState('a, b');
  const [estadoInicial, setEstadoInicial] = useState('q0');
  const [estadosFinais, setEstadosFinais] = useState('q1');
  
  const [transicoes, setTransicoes] = useState<Transicao[]>([
    { origem: 'q0', simbolo: 'a', destino: 'q1' },
    { origem: 'q0', simbolo: 'b', destino: 'q2' },
    { origem: 'q1', simbolo: 'a', destino: 'q1' },
    { origem: 'q1', simbolo: 'b', destino: 'q2' },
    { origem: 'q2', simbolo: 'a', destino: 'q1' },
    { origem: 'q2', simbolo: 'b', destino: 'q2' },
  ]);
  
  const [transOrigem, setTransOrigem] = useState('');
  const [transSimbolo, setTransSimbolo] = useState('');
  const [transDestino, setTransDestino] = useState('');

  // Grammar Form State
  const [simboloInicial, setSimboloInicial] = useState('S');
  const [variaveis, setVariaveis] = useState('S, A');
  const [terminais, setTerminais] = useState('a, b');
  const [producoes, setProducoes] = useState<RegraProducao[]>([
    { esquerda: 'S', direita: ['a A', 'b'] },
    { esquerda: 'A', direita: ['a S', 'a'] },
  ]);

  const [prodEsquerda, setProdEsquerda] = useState('');
  const [prodDireita, setProdDireita] = useState('');

  // Simulation State
  const [simularPalavraInput, setSimularPalavraInput] = useState('');

  // Backend / Calculation Results
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const [automatoResult, setAutomatoResult] = useState<any | null>(null);
  const [grammarResult, setGrammarResult] = useState<any | null>(null);
  const [lastAutomatonId, setLastAutomatonId] = useState<string | null>(null);
  
  const [allSteps, setAllSteps] = useState<PassoDidatico[]>([]);
  const [visibleSteps, setVisibleSteps] = useState<PassoDidatico[]>([]);

  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Smooth scroll down when visibleSteps updates
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [visibleSteps]);

  // Streaming simulation helper
  const streamSteps = (steps: PassoDidatico[]) => {
    setAllSteps(steps);
    setVisibleSteps([]);
    if (!steps || steps.length === 0) return;

    let index = 0;
    const interval = setInterval(() => {
      if (index < steps.length) {
        const nextStep = steps[index];
        if (nextStep) {
          setVisibleSteps((prev) => [...prev, nextStep]);
        }
        index++;
      } else {
        clearInterval(interval);
      }
    }, 250);
  };

  // Form handlers: Transitions
  const handleAddTransition = () => {
    if (!transOrigem || !transDestino) return;
    setTransicoes([
      ...transicoes,
      {
        origem: transOrigem.trim(),
        simbolo: transSimbolo.trim() || 'ε',
        destino: transDestino.trim(),
      },
    ]);
    setTransOrigem('');
    setTransSimbolo('');
    setTransDestino('');
  };

  const handleRemoveTransition = (index: number) => {
    setTransicoes(transicoes.filter((_, i) => i !== index));
  };

  // Form handlers: Grammar Productions
  const handleAddProduction = () => {
    if (!prodEsquerda || !prodDireita) return;
    const alternatives = prodDireita.split('|').map((a) => a.trim()).filter(Boolean);
    
    // Check if rule already exists for this variable
    const existingIdx = producoes.findIndex((p) => p.esquerda === prodEsquerda.trim());
    if (existingIdx >= 0) {
      const updated = [...producoes];
      updated[existingIdx].direita = [...new Set([...updated[existingIdx].direita, ...alternatives])];
      setProducoes(updated);
    } else {
      setProducoes([
        ...producoes,
        {
          esquerda: prodEsquerda.trim(),
          direita: alternatives,
        },
      ]);
    }
    
    setProdEsquerda('');
    setProdDireita('');
  };

  const handleRemoveProduction = (index: number) => {
    setProducoes(producoes.filter((_, i) => i !== index));
  };

  // API Call: Create Automaton First (AFN helper)
  const saveAutomaton = async (): Promise<string | null> => {
    const listEstados = estados.split(',').map((e) => e.trim()).filter(Boolean);
    const listAlfabeto = alfabeto.split(',').map((a) => a.trim()).filter(Boolean);
    const listFinais = estadosFinais.split(',').map((f) => f.trim()).filter(Boolean);

    const payload = {
      nome: nome.trim() || 'M1',
      alfabeto: listAlfabeto,
      estados: listEstados,
      estado_inicial: estadoInicial.trim(),
      estados_finais: listFinais,
      transicoes: transicoes,
    };

    try {
      const res = await fetch(`${BACKEND_URL}/api/automaton`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Erro ao criar autômato.');
      }

      const data = await res.json();
      setLastAutomatonId(data.id_automato);
      return data.id_automato;
    } catch (e: any) {
      setError(e.message);
      return null;
    }
  };

  // API Action: Convert AFN to AFD
  const handleConvertNfaToDfa = async () => {
    setError(null);
    setLoading(true);
    setStatusText('Iniciando determinização do AFN (Subset Construction)...');
    
    const id = await saveAutomaton();
    if (!id) {
      setLoading(false);
      return;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/api/convert/nfa-to-dfa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_automato: id }),
      });

      if (!res.ok) {
        throw new Error('Erro ao iniciar a conversão por streaming.');
      }

      setAllSteps([]);
      setVisibleSteps([]);

      const reader = res.body?.getReader();
      if (!reader) {
        throw new Error('Streaming não suportado pelo navegador.');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = 'message';
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.substring(6).trim();
          } else if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.substring(5).trim();
            try {
              const jsonData = JSON.parse(dataStr);
              if (currentEvent === 'result') {
                setAutomatoResult(jsonData.automato);
                setLastAutomatonId(jsonData.id_afd);
              } else if (currentEvent === 'error') {
                setError(jsonData);
              } else {
                setVisibleSteps((prev) => {
                  const updated = [...prev, jsonData];
                  setAllSteps(updated);
                  return updated;
                });
              }
            } catch (err) {
              console.error('Erro ao decodificar JSON do stream:', err);
            }
            currentEvent = 'message';
          }
        }
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // API Action: Minimize AFD
  const handleMinimizeDfa = async () => {
    if (!lastAutomatonId) return;
    setError(null);
    setLoading(true);
    setStatusText('Minimizando o AFD equivalente (Algoritmo de Moore)...');

    try {
      const res = await fetch(`${BACKEND_URL}/api/minimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_automato: lastAutomatonId }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Erro ao minimizar.');
      }

      const data = await res.json();
      setAutomatoResult(data.automato);
      setLastAutomatonId(data.id_afd_minimizado);
      streamSteps(data.passos_didaticos);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // API Action: Convert Automaton to Grammar
  const handleConvertAfToGr = async () => {
    if (!lastAutomatonId) return;
    setError(null);
    setLoading(true);
    setStatusText('Convertendo o autômato para uma Gramática Regular equivalente...');

    try {
      const res = await fetch(`${BACKEND_URL}/api/convert/af-to-gr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_automato: lastAutomatonId }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Erro na conversão.');
      }

      const data = await res.json();
      setGrammarResult(data.gramatica);
      streamSteps(data.passos_didaticos);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // API Action: Simulate Word
  const handleSimulateWord = async () => {
    if (!lastAutomatonId) return;
    setError(null);
    setLoading(true);
    setStatusText(`Simulando a palavra "${simularPalavraInput}" no autômato...`);

    try {
      const res = await fetch(`${BACKEND_URL}/api/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_automato: lastAutomatonId,
          palavra: simularPalavraInput,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Erro na simulação.');
      }

      const data = await res.json();
      streamSteps(data.passos_didaticos);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // API Action: Convert Grammar to Automaton
  const handleConvertGrToAf = async () => {
    setError(null);
    setLoading(true);
    setStatusText('Iniciando conversão da Gramática Regular para AFN...');

    const listVar = variaveis.split(',').map((v) => v.trim()).filter(Boolean);
    const listTerm = terminais.split(',').map((t) => t.trim()).filter(Boolean);

    const payload = {
      simbolo_inicial: simboloInicial.trim(),
      variaveis: listVar,
      terminais: listTerm,
      producoes: producoes,
    };

    try {
      const res = await fetch(`${BACKEND_URL}/api/convert/gr-to-af`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Erro ao converter GR.');
      }

      const data = await res.json();
      setAutomatoResult(data.automato);
      setLastAutomatonId(data.id_automato);
      streamSteps(data.passos_didaticos);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper to format/render math sets and badges correctly
  const renderMathValue = (value: any) => {
    if (value === null || value === undefined) {
      return <Badge variant="outline" className="math-badge">∅</Badge>;
    }
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <Badge variant="outline" className="math-badge">∅</Badge>;
      }
      return (
        <span className="math-value">
          {'{'}
          {value.map((item, idx) => (
            <React.Fragment key={idx}>
              <Badge variant="secondary" className="math-badge">{String(item)}</Badge>
              {idx < value.length - 1 && ', '}
            </React.Fragment>
          ))}
          {'}'}
        </span>
      );
    }
    const valStr = String(value);
    if (valStr === 'epsilon' || valStr === 'ε' || valStr === '&' || valStr === '') {
      return <Badge variant="secondary" className="math-badge">ε</Badge>;
    }
    return <Badge variant="secondary" className="math-badge">{valStr}</Badge>;
  };

  return (
    <ThemeProvider defaultTheme="dark">
      <div className="app-header">
        <div className="logo-section">
          <Heading as="h1">Teoria da Computação</Heading>
          <Badge variant="outline">Simulador & Conversor</Badge>
        </div>
        <Stack direction="row" spacing="3" align="center">
          {loading && (
            <Badge variant="outline" className="animate-pulse">
              {statusText}
            </Badge>
          )}
          <Text size="xs" color="muted">Tema: Dark 🌙</Text>
        </Stack>
      </div>

      <Page container={false} className="main-container">
        <Grid cols={12} gap="6" className="grid-layout">
          
          {/* PAINEL ESQUERDO: ZONA SECUNDÁRIA (CONTROLE) */}
          <div className="left-pane">
            <Card style={{ padding: '1.25rem' }}>
              <div className="tabs-full">
                <div className="tabs-list-full">
                  <button
                    className="tabs-trigger-full"
                    aria-selected={activeTab === 'automato'}
                    onClick={() => setActiveTab('automato')}
                  >
                    Autômato
                  </button>
                  <button
                    className="tabs-trigger-full"
                    aria-selected={activeTab === 'gramatica'}
                    onClick={() => setActiveTab('gramatica')}
                  >
                    Gramática Regular
                  </button>
                </div>

                {/* ABA DE AUTÔMATO */}
                {activeTab === 'automato' && (
                  <div>
                    <div className="form-field">
                      <Label htmlFor="nome">Nome do Autômato</Label>
                      <Input id="nome" value={nome} onChange={(e) => setNome(e.target.value)} />
                    </div>

                    <div className="form-field">
                      <Label htmlFor="estados">Estados (separados por vírgula)</Label>
                      <Input id="estados" value={estados} onChange={(e) => setEstados(e.target.value)} />
                    </div>

                    <div className="form-field">
                      <Label htmlFor="alfabeto">Alfabeto (separados por vírgula)</Label>
                      <Input id="alfabeto" value={alfabeto} onChange={(e) => setAlfabeto(e.target.value)} />
                    </div>

                    <Grid cols={2} gap="3">
                      <div className="form-field">
                        <Label htmlFor="inicial">Estado Inicial</Label>
                        <Input id="inicial" value={estadoInicial} onChange={(e) => setEstadoInicial(e.target.value)} />
                      </div>
                      <div className="form-field">
                        <Label htmlFor="finais">Estados Finais</Label>
                        <Input id="finais" value={estadosFinais} onChange={(e) => setEstadosFinais(e.target.value)} />
                      </div>
                    </Grid>

                    {/* Transições */}
                    <div className="form-field" style={{ marginBottom: '1.5rem' }}>
                      <Label>Tabela de Transições</Label>
                      
                      <Grid cols={3} gap="2" style={{ marginTop: '0.25rem' }}>
                        <Input placeholder="De (ex: q0)" value={transOrigem} onChange={(e) => setTransOrigem(e.target.value)} />
                        <Input placeholder="Lê (ex: a ou ε)" value={transSimbolo} onChange={(e) => setTransSimbolo(e.target.value)} />
                        <Input placeholder="Para (ex: q1)" value={transDestino} onChange={(e) => setTransDestino(e.target.value)} />
                      </Grid>
                      <Button size="sm" variant="outline" style={{ marginTop: '0.5rem' }} onClick={handleAddTransition}>
                        + Adicionar Transição
                      </Button>

                      <div className="transitions-table-container">
                        <table className="transitions-table">
                          <thead>
                            <tr>
                              <th>Origem</th>
                              <th>Lê</th>
                              <th>Destino</th>
                              <th>Ação</th>
                            </tr>
                          </thead>
                          <tbody>
                            {transicoes.map((t, idx) => (
                              <tr key={idx}>
                                <td>{t.origem}</td>
                                <td>{t.simbolo}</td>
                                <td>{t.destino}</td>
                                <td>
                                  <button className="remove-btn" onClick={() => handleRemoveTransition(idx)}>
                                    Excluir
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <Stack spacing="3">
                      <Button fullWidth onClick={handleConvertNfaToDfa} disabled={loading}>
                        Converter para AFD
                      </Button>
                      
                      {lastAutomatonId && (
                        <>
                          <Button fullWidth variant="secondary" onClick={handleMinimizeDfa} disabled={loading}>
                            Minimizar AFD
                          </Button>
                          <Button fullWidth variant="outline" onClick={handleConvertAfToGr} disabled={loading}>
                            Converter para Gramática Regular
                          </Button>
                          
                          <div className="simulation-input-group">
                            <div style={{ flexGrow: 1 }}>
                              <Input
                                placeholder="Palavra para simular (ex: aab)"
                                value={simularPalavraInput}
                                onChange={(e) => setSimularPalavraInput(e.target.value)}
                              />
                            </div>
                            <Button variant="outline" onClick={handleSimulateWord} disabled={loading}>
                              Simular
                            </Button>
                          </div>
                        </>
                      )}
                    </Stack>
                  </div>
                )}

                {/* ABA DE GRAMÁTICA */}
                {activeTab === 'gramatica' && (
                  <div>
                    <Grid cols={3} gap="2">
                      <div className="form-field">
                        <Label htmlFor="g-inicial">Símbolo Inicial</Label>
                        <Input id="g-inicial" value={simboloInicial} onChange={(e) => setSimboloInicial(e.target.value)} />
                      </div>
                      <div className="form-field" style={{ gridColumn: 'span 2' }}>
                        <Label htmlFor="g-variaveis">Variáveis (Não-Terminais)</Label>
                        <Input id="g-variaveis" value={variaveis} onChange={(e) => setVariaveis(e.target.value)} />
                      </div>
                    </Grid>

                    <div className="form-field">
                      <Label htmlFor="g-terminais">Terminais</Label>
                      <Input id="g-terminais" value={terminais} onChange={(e) => setTerminais(e.target.value)} />
                    </div>

                    {/* Produções */}
                    <div className="form-field" style={{ marginBottom: '1.5rem' }}>
                      <Label>Regras de Produção</Label>
                      
                      <Grid cols={12} gap="2" style={{ marginTop: '0.25rem' }}>
                        <div style={{ gridColumn: 'span 4' }}>
                          <Input placeholder="Var (ex: S)" value={prodEsquerda} onChange={(e) => setProdEsquerda(e.target.value)} />
                        </div>
                        <div style={{ gridColumn: 'span 8' }}>
                          <Input placeholder="Alternativas (ex: a A | b)" value={prodDireita} onChange={(e) => setProdDireita(e.target.value)} />
                        </div>
                      </Grid>
                      <Button size="sm" variant="outline" style={{ marginTop: '0.5rem' }} onClick={handleAddProduction}>
                        + Adicionar Regra
                      </Button>

                      <div className="transitions-table-container">
                        <table className="transitions-table">
                          <thead>
                            <tr>
                              <th>Variável</th>
                              <th>Produções</th>
                              <th>Ação</th>
                            </tr>
                          </thead>
                          <tbody>
                            {producoes.map((p, idx) => (
                              <tr key={idx}>
                                <td><strong>{p.esquerda}</strong></td>
                                <td>{p.direita.join(' | ')}</td>
                                <td>
                                  <button className="remove-btn" onClick={() => handleRemoveProduction(idx)}>
                                    Excluir
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <Stack spacing="3">
                      <Button fullWidth onClick={handleConvertGrToAf} disabled={loading}>
                        Converter para AFN
                      </Button>
                    </Stack>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* PAINEL DIREITO: ZONA PRIMÁRIA (TIMELINE) */}
          <div className="right-pane" ref={scrollContainerRef}>
            {error && (
              <Card style={{ borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.05)', marginBottom: '1rem', padding: '1rem' }}>
                <Text color="destructive" weight={600}>Ocorreu um erro no motor:</Text>
                <Text color="destructive" size="sm" style={{ marginTop: '0.25rem' }}>{error}</Text>
              </Card>
            )}

            {visibleSteps.length === 0 ? (
              <div className="empty-state">
                <Heading as="h3" size="lg" style={{ marginBottom: '0.5rem' }}>
                  Motor de Inferência
                </Heading>
                <Text size="sm">O motor de inferência aguarda parâmetros.</Text>
              </div>
            ) : (
              <div className="timeline-container">
                <div className="timeline-line"></div>
                
                {visibleSteps.map((step, idx) => {
                  const isLast = idx === visibleSteps.length - 1;
                  return (
                    <div key={idx} className="timeline-step">
                      <div className={`timeline-circle ${isLast ? 'active' : ''}`}>
                        {step.indice}
                      </div>
                      
                      <div className="timeline-step-content">
                        <div className="step-header">
                          <Text weight={600} size="sm">
                            {step.descricao}
                          </Text>
                        </div>

                        {step.dados_calculo && Object.keys(step.dados_calculo).length > 0 && (
                          <div className="math-grid">
                            {Object.entries(step.dados_calculo).map(([key, val]) => (
                              <React.Fragment key={key}>
                                <div className="math-key">{key}:</div>
                                <div className="math-value">
                                  {renderMathValue(val)}
                                </div>
                              </React.Fragment>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </Grid>
      </Page>
    </ThemeProvider>
  );
}

export default App;
