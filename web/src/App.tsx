import React, { useState, useEffect, useRef } from 'react';
import './design-system/tokens/tokens.css';
import './App.css';
const getBackendUrl = () => {
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  if (host.endsWith('.github.dev') || host.endsWith('.gitpod.io')) {
    const protocol = window.location.protocol;
    const parts = host.split('.');
    let base = parts[0];
    base = base.replace(/-5173$/, '').replace(/-3000$/, '').replace(/-8000$/, '');
    const domain = parts.slice(1).join('.');
    return `${protocol}//${base}-8000.${domain}`;
  }
  return `${window.location.protocol}//${host}:8000`;
};
const BACKEND_URL = getBackendUrl();

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

interface DocMetadata {
  id: string;
  title: string;
  filename: string;
}

function parseMathToHtml(math: string): string {
  let res = math;

  // Substituir comandos padrão do LaTeX por equivalentes Unicode
  res = res.replace(/\\Sigma/g, 'Σ');
  res = res.replace(/\\delta/g, 'δ');
  res = res.replace(/\\epsilon/g, 'ε');
  res = res.replace(/\\cup/g, ' ∪ ');
  res = res.replace(/\\cap/g, ' ∩ ');
  res = res.replace(/\\emptyset/g, '∅');
  res = res.replace(/\\neq/g, ' ≠ ');
  res = res.replace(/\\in/g, ' ∈ ');
  res = res.replace(/\\notin/g, ' ∉ ');
  res = res.replace(/\\mid/g, ' | ');
  res = res.replace(/\\dots/g, '...');
  res = res.replace(/\\mathcal\{P\}/g, '𝒫');
  
  // Limpar formatação LaTeX auxiliar
  res = res.replace(/\\left/g, '');
  res = res.replace(/\\right/g, '');
  res = res.replace(/\\quad/g, ' ');
  res = res.replace(/\\text\{([^{}]+)\}/g, '$1');
  res = res.replace(/\\{/g, '{');
  res = res.replace(/\\}/g, '}');
  
  // Operador de união grande: \bigcup_{r \in R}
  res = res.replace(/\\bigcup_\{([^}]+)\}/g, '⋃<sub>$1</sub>');
  res = res.replace(/\\bigcup/g, '⋃');
  
  // Símbolo do chapéu: \hat{\delta} -> δ̂
  res = res.replace(/\\hat\{\\delta\}/g, 'δ̂');
  res = res.replace(/\\hat\{([^}]+)\}/g, '$1̂');
  
  // Setas
  res = res.replace(/\\xrightarrow\{([^}]+)\}/g, ' ⎯( $1 )→ ');
  res = res.replace(/\\rightarrow/g, ' → ');
  
  // Subscritos & Sobrescritos (executar 3 vezes para suportar aninhamento leve)
  for (let i = 0; i < 3; i++) {
    res = res.replace(/_\{([^}]+)\}/g, '<sub>$1</sub>');
    res = res.replace(/_([a-zA-Z0-9])/g, '<sub>$1</sub>');
    res = res.replace(/\^\{([^}]+)\}/g, '<sup>$1</sup>');
    res = res.replace(/\^([a-zA-Z0-9'*])/g, '<sup>$1</sup>');
  }

  return `<span class="math-expr">${res}</span>`;
}

function parseMarkdownToHtml(md: string): string {
  if (!md) return '';

  // 1. Escapar entidades HTML básicas para evitar colisão com tags reais
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // 2. Blocos de equação (block math): $$ ... $$
  html = html.replace(/\$\$([\s\S]*?)\$\$/g, (match, math) => {
    return `<div class="math-block">${parseMathToHtml(math)}</div>`;
  });

  // 3. Equações em linha (inline math): $ ... $
  html = html.replace(/\$([^$\n]+)\$/g, (match, math) => {
    return parseMathToHtml(math);
  });

  // 4. Blocos de código: ``` ... ```
  html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
    const cleanCode = code.replace(/</g, '&lt;').replace(/>/g, '&gt;').trim();
    return `<pre><code>${cleanCode}</code></pre>`;
  });

  // 5. Código em linha (inline code): `code`
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');

  // 6. Cabeçalhos
  html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
  html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');

  // 7. Divisores
  html = html.replace(/^---\s*$/gm, '<hr />');

  // 8. Negrito e Itálico
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // 9. Processamento de Listas e Parágrafos linha a linha
  const lines = html.split('\n');
  let result: string[] = [];
  let inList = false;
  let inBlockquote = false;
  let paragraphBuffer: string[] = [];

  const flushParagraph = () => {
    if (paragraphBuffer.length > 0) {
      result.push(`<p>${paragraphBuffer.join(' ')}</p>`);
      paragraphBuffer = [];
    }
  };

  const flushList = () => {
    if (inList) {
      result.push('</ul>');
      inList = false;
    }
  };

  const flushBlockquote = () => {
    if (inBlockquote) {
      result.push('</blockquote>');
      inBlockquote = false;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Linha em branco encerra parágrafo ou listas ativas
    if (trimmed === '') {
      flushParagraph();
      flushList();
      flushBlockquote();
      continue;
    }

    // Se for um bloco HTML pré-computado (h1-h4, pre, hr, math-block)
    if (trimmed.startsWith('<h') || trimmed.startsWith('<pre') || trimmed.startsWith('<hr') || trimmed.startsWith('<div class="math-block"')) {
      flushParagraph();
      flushList();
      flushBlockquote();
      result.push(trimmed);
      continue;
    }

    // Citação (blockquote)
    if (trimmed.startsWith('&gt;') || trimmed.startsWith('>')) {
      flushParagraph();
      flushList();
      if (!inBlockquote) {
        result.push('<blockquote>');
        inBlockquote = true;
      }
      const quoteContent = (trimmed.startsWith('&gt;') ? trimmed.substring(4) : trimmed.substring(1)).trim();
      result.push(`<p>${quoteContent}</p>`);
      continue;
    } else {
      flushBlockquote();
    }

    // Item de lista com marcador (* ou -)
    const listMatch = line.match(/^(\s*)[-*]\s+(.+)$/);
    if (listMatch) {
      flushParagraph();
      if (!inList) {
        result.push('<ul>');
        inList = true;
      }
      const indent = listMatch[1].length;
      if (indent >= 2) {
        result.push(`<li style="margin-left: 20px;">${listMatch[2]}</li>`);
      } else {
        result.push(`<li>${listMatch[2]}</li>`);
      }
      continue;
    }

    // Item de lista ordenada (numérica)
    const numListMatch = line.match(/^(\s*)\d+\.\s+(.+)$/);
    if (numListMatch) {
      flushParagraph();
      if (!inList) {
        result.push('<ol>');
        inList = true;
      }
      const indent = numListMatch[1].length;
      if (indent >= 2) {
        result.push(`<li style="margin-left: 20px;">${numListMatch[2]}</li>`);
      } else {
        result.push(`<li>${numListMatch[2]}</li>`);
      }
      continue;
    }

    // Se chegamos aqui, é uma linha de texto padrão. Se havia uma lista aberta, fecha ela.
    if (inList) {
      // Determina se fecha como ul ou ol
      const lastListTag = result.join('').lastIndexOf('<ul') > result.join('').lastIndexOf('<ol') ? '</ul>' : '</ol>';
      result.push(lastListTag);
      inList = false;
    }

    paragraphBuffer.push(trimmed);
  }

  // Descarregar buffers restantes
  flushParagraph();
  if (inList) {
    result.push('</ul>');
  }
  flushBlockquote();

  return result.join('\n');
}
const FolderIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
    <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2z"/>
  </svg>
);

const ChartIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
    <line x1="18" y1="20" x2="18" y2="10"/>
    <line x1="12" y1="20" x2="12" y2="4"/>
    <line x1="6" y1="20" x2="6" y2="14"/>
  </svg>
);

const SettingsIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3"/>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
  </svg>
);

const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '8px' }}>
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

const BookOpenIcon = ({ size = 20 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
  </svg>
);

const ClockIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}>
    <circle cx="12" cy="12" r="10"/>
    <polyline points="12 6 12 12 16 14"/>
  </svg>
);

const PenIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}>
    <path d="M12 20h9"/>
    <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>
  </svg>
);

function App() {
  // Navigation / Tabs
  const [activeTab, setActiveTab] = useState<'automato' | 'gramatica'>('automato');
  const [currentNav, setCurrentNav] = useState<'simulador' | 'documentacao'>('simulador');

  // Documentation State
  const [docList, setDocList] = useState<DocMetadata[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [selectedDocContent, setSelectedDocContent] = useState<string | null>(null);
  const [docLoading, setDocLoading] = useState(false);
  
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

  // Limpa o estado e o ID do último autômato se a definição mudar
  useEffect(() => {
    setLastAutomatonId(null);
    setAutomatoResult(null);
    setAllSteps([]);
    setVisibleSteps([]);
    setError(null);
  }, [nome, estados, alfabeto, estadoInicial, estadosFinais, transicoes]);

  // Fetch documents list when documentation nav is active
  useEffect(() => {
    if (currentNav === 'documentacao') {
      const fetchDocsList = async () => {
        try {
          const res = await fetch(`${BACKEND_URL}/api/docs`);
          if (!res.ok) throw new Error('Erro ao buscar lista de documentações.');
          const data = await res.json();
          setDocList(data);
          if (data.length > 0 && !selectedDocId) {
            setSelectedDocId(data[0].id);
          }
        } catch (err: any) {
          console.error(err);
        }
      };
      fetchDocsList();
    }
  }, [currentNav]);

  // Fetch active document content
  useEffect(() => {
    if (currentNav === 'documentacao' && selectedDocId) {
      const fetchDocContent = async () => {
        setDocLoading(true);
        try {
          const res = await fetch(`${BACKEND_URL}/api/docs/${selectedDocId}`);
          if (!res.ok) throw new Error('Erro ao carregar conteúdo do documento.');
          const data = await res.json();
          setSelectedDocContent(data.content);
        } catch (err: any) {
          console.error(err);
        } finally {
          setDocLoading(false);
        }
      };
      fetchDocContent();
    }
  }, [currentNav, selectedDocId]);

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
    }, 3000);
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

  // API Action: Convert AFN to AFD (SSE Streaming)
  const handleConvertNfaToDfa = async () => {
    setError(null);
    setLoading(true);
    setStatusText('Convertendo AFN para AFD...');
    setAutomatoResult(null);
    
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
    setStatusText('Minimizando o AFD...');
    setAutomatoResult(null);

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
    setStatusText('Convertendo para Gramática...');
    setGrammarResult(null);

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
    setStatusText(`Simulando a palavra...`);

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
    setStatusText('Convertendo Gramática para AFN...');
    setAutomatoResult(null);

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

  // Helper to format/render math values inside timeline
  const renderMathValue = (value: any) => {
    if (value === null || value === undefined) {
      return <span className="math-chip empty">∅</span>;
    }
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="math-chip empty">∅</span>;
      }
      return (
        <span className="math-val">
          {'{'}
          {value.map((item, idx) => (
            <React.Fragment key={idx}>
              <span className="math-chip">{String(item)}</span>
              {idx < value.length - 1 && ', '}
            </React.Fragment>
          ))}
          {'}'}
        </span>
      );
    }
    const valStr = String(value);
    if (valStr === 'epsilon' || valStr === 'ε' || valStr === '&' || valStr === '') {
      return <span className="math-chip">ε</span>;
    }
    return <span className="math-chip">{valStr}</span>;
  };

  // Reading time helper
  const getReadingTime = (text: string | null) => {
    if (!text) return 0;
    const words = text.split(/\s+/).length;
    return Math.ceil(words / 200);
  };

  return (
    <div id="root">
      {/* Top Navigation Bar */}
      <header className="topbar">
        <div className="topbar-left">
          <div className="topbar-logo">
            <span className="topbar-logo-icon">Σ</span>
            SIN 141 - Teoria da Computação
          </div>
          <nav className="topbar-nav">
            <button 
              className={`topbar-nav-btn ${currentNav === 'simulador' ? 'active' : ''}`}
              onClick={() => setCurrentNav('simulador')}
            >
              Simulador
            </button>
            <button 
              className={`topbar-nav-btn ${currentNav === 'documentacao' ? 'active' : ''}`}
              onClick={() => setCurrentNav('documentacao')}
            >
              Documentação
            </button>
          </nav>
        </div>
        <div className="topbar-right">
          {loading && (
            <div className="topbar-status-pill">
              <span className="status-dot loading" />
              {statusText}
            </div>
          )}
          {!loading && error && (
            <div className="topbar-status-pill">
              <span className="status-dot error" />
              Motor Offline
            </div>
          )}
          {!loading && !error && (
            <div className="topbar-status-pill">
              <span className="status-dot" />
              Motor de Cálculo Online
            </div>
          )}
        </div>
      </header>

      {/* Main Content View Switch */}
      {currentNav === 'simulador' ? (
        <div className="main-layout">
          {/* Leftmost Sidebar */}
          <aside className="sidebar">
            <div className="sidebar-section">
              <div className="sidebar-section-label">Planejamento</div>
              <button
                className={`sidebar-item ${currentNav === 'simulador' && activeTab === 'automato' ? 'active' : ''}`}
                onClick={() => {
                  setCurrentNav('simulador');
                  setActiveTab('automato');
                }}
              >
                <FolderIcon />
                Simuladores
              </button>
              <button
                className={`sidebar-item ${currentNav === 'simulador' && activeTab === 'gramatica' ? 'active' : ''}`}
                onClick={() => {
                  setCurrentNav('simulador');
                  setActiveTab('gramatica');
                }}
              >
                <ChartIcon />
                Gramáticas
              </button>
              <button
                className="sidebar-item"
                onClick={() => {
                  setCurrentNav('simulador');
                  setActiveTab('automato');
                  if (lastAutomatonId) {
                    handleMinimizeDfa();
                  } else {
                    alert('Defina e converta um autômato primeiro antes de minimizar!');
                  }
                }}
              >
                <SettingsIcon size={16} />
                Minimizador
              </button>
            </div>
          </aside>

          {/* Outer Split View */}
          <div className="content-area">
            {/* Controls Panel (Form) */}
            <div className="panel-left">
              <div className="panel-left-header">
                <div className="panel-left-title">Configurar Modelo</div>
                <div className="panel-tab-group">
                  <button
                    className={`panel-tab-btn ${activeTab === 'automato' ? 'active' : ''}`}
                    onClick={() => setActiveTab('automato')}
                  >
                    Autômato
                  </button>
                  <button
                    className={`panel-tab-btn ${activeTab === 'gramatica' ? 'active' : ''}`}
                    onClick={() => setActiveTab('gramatica')}
                  >
                    Gramática Regular
                  </button>
                </div>
              </div>

              <div className="panel-left-body">
                {activeTab === 'automato' && (
                  <>
                    <div className="field">
                      <label className="field-label" htmlFor="nome">Identificador</label>
                      <input className="field-input" id="nome" value={nome} onChange={(e) => setNome(e.target.value)} />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="estados">Estados</label>
                      <input className="field-input" id="estados" value={estados} onChange={(e) => setEstados(e.target.value)} />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="alfabeto">Alfabeto</label>
                      <input className="field-input" id="alfabeto" value={alfabeto} onChange={(e) => setAlfabeto(e.target.value)} />
                    </div>
                    <div className="field-row">
                      <div className="field">
                        <label className="field-label" htmlFor="inicial">Estado Inicial</label>
                        <input className="field-input" id="inicial" value={estadoInicial} onChange={(e) => setEstadoInicial(e.target.value)} />
                      </div>
                      <div className="field">
                        <label className="field-label" htmlFor="finais">Estados Finais</label>
                        <input className="field-input" id="finais" value={estadosFinais} onChange={(e) => setEstadosFinais(e.target.value)} />
                      </div>
                    </div>

                    <div className="field">
                      <div className="trans-header">
                        <label className="field-label">Transições</label>
                      </div>
                      <div className="trans-add-row">
                        <input className="field-input" placeholder="Origem" value={transOrigem} onChange={(e) => setTransOrigem(e.target.value)} />
                        <input className="field-input" placeholder="Lê" value={transSimbolo} onChange={(e) => setTransSimbolo(e.target.value)} />
                        <input className="field-input" placeholder="Destino" value={transDestino} onChange={(e) => setTransDestino(e.target.value)} />
                      </div>
                      <button className="btn btn-secondary btn-sm btn-full" onClick={handleAddTransition}>
                        + Adicionar Transição
                      </button>
                    </div>

                    {transicoes.length > 0 && (
                      <div className="trans-table-wrap">
                        <table className="trans-table">
                          <thead>
                            <tr>
                              <th>Origem</th>
                              <th>Lê</th>
                              <th>Destino</th>
                              <th style={{ width: '40px' }} />
                            </tr>
                          </thead>
                          <tbody>
                            {transicoes.map((t, idx) => (
                              <tr key={idx}>
                                <td>{t.origem}</td>
                                <td>{t.simbolo}</td>
                                <td>{t.destino}</td>
                                <td>
                                  <button className="btn-remove-trans" onClick={() => handleRemoveTransition(idx)}>×</button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </>
                )}

                {activeTab === 'gramatica' && (
                  <>
                    <div className="field">
                      <label className="field-label" htmlFor="g-inicial">Símbolo Inicial</label>
                      <input className="field-input" id="g-inicial" value={simboloInicial} onChange={(e) => setSimboloInicial(e.target.value)} />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="g-variaveis">Variáveis (Não-Terminais)</label>
                      <input className="field-input" id="g-variaveis" value={variaveis} onChange={(e) => setVariaveis(e.target.value)} />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="g-terminais">Terminais</label>
                      <input className="field-input" id="g-terminais" value={terminais} onChange={(e) => setTerminais(e.target.value)} />
                    </div>

                    <div className="field">
                      <label className="field-label">Regras de Produção</label>
                      <div className="trans-add-row" style={{ gridTemplateColumns: '80px 1fr' }}>
                        <input className="field-input" placeholder="Var" value={prodEsquerda} onChange={(e) => setProdEsquerda(e.target.value)} />
                        <input className="field-input" placeholder="Ex: a A | b" value={prodDireita} onChange={(e) => setProdDireita(e.target.value)} />
                      </div>
                      <button className="btn btn-secondary btn-sm btn-full" style={{ marginTop: '4px' }} onClick={handleAddProduction}>
                        + Adicionar Regra
                      </button>
                    </div>

                    {producoes.length > 0 && (
                      <div className="trans-table-wrap">
                        <table className="trans-table">
                          <thead>
                            <tr>
                              <th>Variável</th>
                              <th>Produções</th>
                              <th style={{ width: '40px' }} />
                            </tr>
                          </thead>
                          <tbody>
                            {producoes.map((p, idx) => (
                              <tr key={idx}>
                                <td>{p.esquerda}</td>
                                <td>{p.direita.join(' | ')}</td>
                                <td>
                                  <button className="btn-remove-trans" onClick={() => handleRemoveProduction(idx)}>×</button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </>
                )}
              </div>

              <div className="panel-left-footer">
                {activeTab === 'automato' && (
                  <>
                    <button className="btn btn-primary btn-full" onClick={handleConvertNfaToDfa} disabled={loading}>
                      Converter para AFD
                    </button>
                    {lastAutomatonId && (
                      <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
                        <button className="btn btn-secondary btn-full btn-sm" onClick={handleMinimizeDfa} disabled={loading}>
                          Minimizar
                        </button>
                        <button className="btn btn-outline btn-full btn-sm" onClick={handleConvertAfToGr} disabled={loading}>
                          Para Gramática
                        </button>
                      </div>
                    )}
                  </>
                )}

                {activeTab === 'gramatica' && (
                  <button className="btn btn-primary btn-full" onClick={handleConvertGrToAf} disabled={loading}>
                    Converter para AFN
                  </button>
                )}
              </div>
            </div>

            {/* Primary Viewport (Output and Trace Timeline) */}
            <div className="panel-right">
              <div className="panel-right-header">
                <div className="panel-right-title">Rastreamento de Execução</div>
                <div className="panel-right-meta">
                  <span className="meta-badge">Inferência Ativa</span>
                </div>
              </div>

              <div className="panel-right-body" ref={scrollContainerRef}>
                {error && (
                  <div className="error-banner">
                    <span className="error-banner-icon">⚠️</span>
                    <div className="error-banner-text">
                      <div className="error-banner-label">Falha no Motor Didático</div>
                      {error}
                    </div>
                  </div>
                )}

                {/* Real-time Result Panels */}
                {automatoResult && (
                  <div className="result-panel">
                    <div className="result-panel-header">
                      <span className="result-panel-title">Automato Gerado ({automatoResult.nome})</span>
                      <span className="meta-badge success">Equivalente</span>
                    </div>
                    <div className="result-panel-body">
                      <div className="result-stat-grid">
                        <div className="result-stat">
                          <div className="result-stat-label">Inicial</div>
                          <div className="result-stat-value">{automatoResult.estado_inicial}</div>
                        </div>
                        <div className="result-stat">
                          <div className="result-stat-label">Estados</div>
                          <div className="result-stat-value">{automatoResult.estados?.length || 0}</div>
                        </div>
                        <div className="result-stat">
                          <div className="result-stat-label">Transições</div>
                          <div className="result-stat-value">{automatoResult.transicoes?.length || 0}</div>
                        </div>
                        <div className="result-stat">
                          <div className="result-stat-label">Finais</div>
                          <div className="result-stat-value">{automatoResult.estados_finais?.length || 0}</div>
                        </div>
                      </div>

                      <div className="result-transitions">
                        <table className="result-trans-table">
                          <thead>
                            <tr>
                              <th>Origem</th>
                              <th>Lê</th>
                              <th>Destino</th>
                            </tr>
                          </thead>
                          <tbody>
                            {automatoResult.transicoes?.map((t: any, idx: number) => {
                              const isInit = t.origem === automatoResult.estado_inicial;
                              const isFin = automatoResult.estados_finais?.includes(t.destino);
                              return (
                                <tr key={idx}>
                                  <td>
                                    <span className={`state-pill ${isInit ? 'initial' : ''}`}>{t.origem}</span>
                                  </td>
                                  <td>{t.simbolo}</td>
                                  <td>
                                    <span className={`state-pill ${isFin ? 'final' : ''}`}>{t.destino}</span>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>

                      {lastAutomatonId && (
                        <div className="sim-row">
                          <input
                            className="field-input"
                            placeholder="Digite uma palavra para simular..."
                            value={simularPalavraInput}
                            onChange={(e) => setSimularPalavraInput(e.target.value)}
                          />
                          <button className="btn btn-secondary btn-sm" onClick={handleSimulateWord} disabled={loading}>
                            Simular Entrada
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {grammarResult && (
                  <div className="result-panel">
                    <div className="result-panel-header">
                      <span className="result-panel-title">Gramática Regular Gerada</span>
                      <span className="meta-badge success">Equivalente</span>
                    </div>
                    <div className="result-panel-body">
                      <div className="result-stat-grid" style={{ gridTemplateColumns: '1fr 2fr' }}>
                        <div className="result-stat">
                          <div className="result-stat-label">Inicial</div>
                          <div className="result-stat-value">{grammarResult.simbolo_inicial}</div>
                        </div>
                        <div className="result-stat">
                          <div className="result-stat-label">Terminais</div>
                          <div className="result-stat-value">{grammarResult.terminais?.join(', ') || '∅'}</div>
                        </div>
                      </div>
                      <div style={{ marginTop: '10px' }}>
                        <label className="field-label" style={{ marginBottom: '4px', display: 'block' }}>Produções</label>
                        <div className="trans-table-wrap">
                          <table className="trans-table">
                            <tbody>
                              {grammarResult.producoes?.map((p: any, idx: number) => (
                                <tr key={idx}>
                                  <td style={{ fontWeight: 600, color: '#ededed', width: '30%' }}>{p.esquerda}</td>
                                  <td>{p.direita?.join(' | ')}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Timeline containing steps */}
                {visibleSteps.length > 0 && (
                  <div className="timeline">
                    <div className="timeline-rail" />
                    {visibleSteps.map((step, idx) => (
                      <div key={idx} className="timeline-item">
                        <div className="timeline-node">{step.indice}</div>
                        <div className="timeline-card">
                          <div className="timeline-card-desc">{step.descricao}</div>
                          {step.dados_calculo && Object.keys(step.dados_calculo).length > 0 && (
                            <div className="timeline-math">
                              {Object.entries(step.dados_calculo).map(([key, val]) => (
                                <React.Fragment key={key}>
                                  <div className="math-key">{key}:</div>
                                  <div className="math-val">{renderMathValue(val)}</div>
                                </React.Fragment>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    {loading && (
                      <div className="loading-row">
                        <div className="loader-dots">
                          <span />
                          <span />
                          <span />
                        </div>
                        Computando passo didático...
                      </div>
                    )}
                  </div>
                )}

                {/* Empty state when no trace is available */}
                {visibleSteps.length === 0 && !automatoResult && !grammarResult && (
                  <div className="empty-state">
                    <span className="empty-state-icon"><BookOpenIcon size={32} /></span>
                    <div className="empty-state-title">Nenhum Rastreamento Ativo</div>
                    <div className="empty-state-desc">
                      Configure os parâmetros do autômato ou da gramática e inicie uma conversão.
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Editorial Documentation View */
        <div className="doc-view">
          <aside className="doc-sidebar">
            <div className="doc-sidebar-title">Especificações de Engenharia</div>
            {docList.map((doc) => (
              <button
                key={doc.id}
                className={`doc-nav-item ${selectedDocId === doc.id ? 'active' : ''}`}
                onClick={() => setSelectedDocId(doc.id)}
              >
                {doc.title}
              </button>
            ))}
          </aside>
          
          <div className="doc-content-wrapper">
            <div className="doc-content">
              {docLoading ? (
                <div className="loading-row">
                  <div className="loader-dots">
                    <span />
                    <span />
                    <span />
                  </div>
                  Carregando artigo técnico...
                </div>
              ) : (
                <>
                  <div className="doc-meta-header">
                    <span className="doc-meta-tag">Artigo Técnico Acadêmico</span>
                    <h1 className="doc-meta-title">
                      {docList.find((d) => d.id === selectedDocId)?.title || 'Documentação'}
                    </h1>
                     <div className="doc-meta-stats">
                      <span className="doc-meta-stat-item">
                        <ClockIcon /> {getReadingTime(selectedDocContent)} min de leitura
                      </span>
                      <span className="doc-meta-stat-item">
                        <PenIcon /> Comitê Editorial
                      </span>
                    </div>
                  </div>
                  
                  <div 
                    className="prose"
                    dangerouslySetInnerHTML={{
                      __html: parseMarkdownToHtml(selectedDocContent || '')
                    }}
                  />
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
