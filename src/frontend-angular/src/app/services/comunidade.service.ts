import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../environments/environment';

export interface Comunidade {
  id: number;
  nome: string;
  descricao: string;
  categoria: string;
  regras: string;
  icone: string | null;
  banner: string | null;  
  moderador: string;
  criado_em: string;
  membros_count: number;
  is_membro: boolean;
  is_moderador: boolean;
  minha_restricao: RestricaoAtivaComunidade | null;
  fui_banido: boolean;
}

export interface RestricaoAtivaComunidade {
  expira_em: string;
  duracao_dias: number;
  justificativa: string;
}

export interface ComentarioPostagem {
  id: number;
  postagem: number;
  parent: number | null;
  /** Nome de exibição do autor. */
  autor: string;
  autor_username: string;
  conteudo: string;
  criado_em: string;
  curtidas_count: number;
  curtido_por_mim: boolean;
  respostas_count: number;
  respostas: ComentarioPostagem[];
}

export interface PostagemComunidade {
  id: number;
  comunidade: number;
  /** Nome de exibição do autor. */
  autor: string;
  autor_username: string;
  titulo: string;
  conteudo: string;
  criado_em: string;
  curtidas_count: number;
  comentarios_count: number;
  curtido_por_mim: boolean;
  comentarios: ComentarioPostagem[];
}



export interface CriarComentarioPayload {
  conteudo: string;
  parent?: number;
}

export interface DenunciarPostagemPayload {
  motivo: string;
  detalhe?: string;  
}

export interface CurtirPostagemResponse {
  curtido: boolean;
  postagem: PostagemComunidade;
}

export interface DenunciarPostagemResponse {
  mensagem: string;
  denuncia: DenunciaPostagem;
}

export interface DenunciaPostagem {
  id: number;
  comunidade: number;
  alvo_tipo: 'postagem' | 'comentario';
  postagem: number | null;
  postagem_titulo: string;
  postagem_conteudo: string;
  postagem_autor: string;
  postagem_criado_em: string | null;
  comentario: number | null;
  comentario_conteudo: string;
  comentario_autor: string;
  denunciante: string;
  motivo: string;
  detalhe: string;
  status: 'pendente' | 'aprovada' | 'reprovada';
  criado_em: string;
  analisado_por: number | null;
  analisado_em: string | null;
  acao_registrada: string;
}

export interface ModeracaoComunidade {
  pendentes: DenunciaPostagem[];
  pendentes_count: number;
  analisadas_count: number;
}

export interface AnaliseDenunciaResponse {
  mensagem: string;
  denuncia: DenunciaPostagem;
}

export interface CriarPostagemPayload {
  titulo: string;
  conteudo: string;
}

export interface CriarComunidadePayload {
  nome: string;
  descricao: string;
  categoria: string;
  regras?: string;
  icone?: File | null;
  banner?: File | null;  
}

/** CDU012 - edição: só os campos enviados são alterados. */
export interface EditarComunidadePayload {
  nome?: string;
  descricao?: string;
  categoria?: string;
  regras?: string;
  icone?: File | null;
  banner?: File | null;
  removerIcone?: boolean;
  removerBanner?: boolean;
}

export interface Encontro {
  id: number;
  /** Nome da comunidade. */
  comunidade: string;
  comunidade_id: number;
  titulo: string;
  descricao: string;
  data_hr_encontro: string;
  endereco: string;
  tags: string;
  img: string | null;
  criado_por: string;
  criado_em: string;
}

export interface CriarEncontroPayload {
  titulo: string;
  descricao: string;
  data_hr_encontro: string;
  endereco: string;
  tags?: string;
  img?: File | null;
}

export interface RestricaoAtiva {
  expira_em: string;
  duracao_dias: number;
  justificativa: string;
}

export interface MembroComunidade {
  id: number;
  username: string;
  nome: string;
  is_moderador: boolean;
  restricao_ativa: RestricaoAtiva | null;
  acoes_count: number;
}

export type TipoAcaoModeracao = 'restringir' | 'banir';

export interface AplicarAcaoPayload {
  convivente_id: number;
  tipo: TipoAcaoModeracao;
  justificativa?: string;
  duracao_dias?: number;
}

export interface AcaoModeracao {
  id: number;
  tipo: TipoAcaoModeracao;
  tipo_display: string;
  justificativa: string;
  duracao_dias: number | null;
  expira_em: string | null;
  criado_em: string;
  moderador: string | null;
  convivente: string;
}

@Injectable({ providedIn: 'root' })
export class ComunidadeService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/comunidades`;

  readonly minhas = signal<Comunidade[]>([]);

  listar(): Observable<Comunidade[]> {
    return this.http.get<Comunidade[]>(`${this.base}/`);
  }

  carregarMinhas(): Observable<Comunidade[]> {
    return this.http
      .get<Comunidade[]>(`${this.base}/minhas/`)
      .pipe(tap((lista) => this.minhas.set(lista)));
  }

  limparMinhas(): void {
    this.minhas.set([]);
  }

  criar(payload: CriarComunidadePayload): Observable<Comunidade> {
    const form = new FormData();
    form.append('nome', payload.nome);
    form.append('descricao', payload.descricao);
    form.append('categoria', payload.categoria);
    form.append('regras', payload.regras ?? '');

    this.anexarArquivo(form, 'icone', payload.icone);
    this.anexarArquivo(form, 'banner', payload.banner);

    return this.http
      .post<Comunidade>(`${this.base}/criar/`, form)
      .pipe(tap(() => this.carregarMinhas().subscribe()));
  }

  /** CDU012 - Fluxo Principal: o moderador altera as informações da comunidade. */
  atualizar(id: number, payload: EditarComunidadePayload): Observable<Comunidade> {
    const form = new FormData();
    for (const campo of ['nome', 'descricao', 'categoria', 'regras'] as const) {
      const valor = payload[campo];
      if (valor !== undefined) form.append(campo, valor);
    }
    this.anexarArquivo(form, 'icone', payload.icone);
    this.anexarArquivo(form, 'banner', payload.banner);
    if (payload.removerIcone) form.append('remover_icone', 'true');
    if (payload.removerBanner) form.append('remover_banner', 'true');

    return this.http
      .patch<Comunidade>(`${this.base}/${id}/`, form)
      .pipe(tap(() => this.carregarMinhas().subscribe()));
  }

  /** CDU012 - Fluxo Alternativo I: o moderador exclui a comunidade. */
  excluir(id: number): Observable<void> {
    return this.http
      .delete<void>(`${this.base}/${id}/`)
      .pipe(tap(() => this.carregarMinhas().subscribe()));
  }

  private anexarArquivo(form: FormData, campo: string, arquivo?: File | null): void {
    if (!arquivo) {
      return;
    }

    form.append(campo, arquivo, arquivo.name);
  }

  detalhe(id: number): Observable<Comunidade> {
    return this.http.get<Comunidade>(`${this.base}/${id}/`);
  }

  participar(id: number): Observable<Comunidade> {
    return this.http
      .post<Comunidade>(`${this.base}/${id}/participar/`, {})
      .pipe(tap(() => this.carregarMinhas().subscribe()));
  }

  sair(id: number): Observable<Comunidade> {
    return this.http
      .post<Comunidade>(`${this.base}/${id}/sair/`, {})
      .pipe(tap(() => this.carregarMinhas().subscribe()));
  }

  // ----- Postagens -----

  listarPostagens(id: number): Observable<PostagemComunidade[]> {
    return this.http.get<PostagemComunidade[]>(`${this.base}/${id}/postagens/`);
  }

  criarPostagem(id: number, payload: CriarPostagemPayload): Observable<PostagemComunidade> {
    return this.http.post<PostagemComunidade>(`${this.base}/${id}/postagens/`, payload);
  }

  curtirPostagem(comunidadeId: number, postagemId: number): Observable<CurtirPostagemResponse> {
    return this.http.post<CurtirPostagemResponse>(`${this.base}/${comunidadeId}/postagens/${postagemId}/curtir/`, {});
  }

  comentarPostagem(comunidadeId: number, postagemId: number, payload: CriarComentarioPayload): Observable<PostagemComunidade> {
    return this.http.post<PostagemComunidade>(`${this.base}/${comunidadeId}/postagens/${postagemId}/comentarios/`, payload);
  }

  denunciarPostagem(comunidadeId: number, postagemId: number, payload: DenunciarPostagemPayload): Observable<DenunciarPostagemResponse> {
    return this.http.post<DenunciarPostagemResponse>(`${this.base}/${comunidadeId}/postagens/${postagemId}/denunciar/`, payload);
  }

  curtirComentario(comunidadeId: number, postagemId: number, comentarioId: number): Observable<CurtirPostagemResponse> {
    return this.http.post<CurtirPostagemResponse>(
      `${this.base}/${comunidadeId}/postagens/${postagemId}/comentarios/${comentarioId}/curtir/`, {},
    );
  }

  denunciarComentario(comunidadeId: number, postagemId: number, comentarioId: number, payload: DenunciarPostagemPayload): Observable<DenunciarPostagemResponse> {
    return this.http.post<DenunciarPostagemResponse>(
      `${this.base}/${comunidadeId}/postagens/${postagemId}/comentarios/${comentarioId}/denunciar/`, payload,
    );
  }
  
  carregarModeracao(id: number): Observable<ModeracaoComunidade> {
    return this.http.get<ModeracaoComunidade>(`${this.base}/${id}/moderacao/`);
  }

  aprovarDenuncia(id: number, denunciaId: number): Observable<AnaliseDenunciaResponse> {
    return this.http.post<AnaliseDenunciaResponse>(`${this.base}/${id}/moderacao/${denunciaId}/aprovar/`, {});
  }

  reprovarDenuncia(id: number, denunciaId: number): Observable<AnaliseDenunciaResponse> {
    return this.http.post<AnaliseDenunciaResponse>(`${this.base}/${id}/moderacao/${denunciaId}/reprovar/`, {});
  }  

  // ----- Encontros -----

  /** CDU005: próximos encontros de todas as comunidades (ou só das minhas). */
  listarEncontrosPublicos(apenasMinhas = false): Observable<Encontro[]> {
    const params = apenasMinhas ? { minhas: '1' } : undefined;
    return this.http.get<Encontro[]>(`${this.base}/encontros/`, { params });
  }

  listarEncontros(comunidadeId: number): Observable<Encontro[]> {
    return this.http.get<Encontro[]>(`${this.base}/${comunidadeId}/encontros/`);
  }

  criarEncontro(comunidadeId: number, payload: CriarEncontroPayload): Observable<Encontro> {
    const url = `${this.base}/${comunidadeId}/encontros/criar/`;

    if (payload.img) {
      const form = new FormData();
      form.append('titulo', payload.titulo);
      form.append('descricao', payload.descricao);
      form.append('data_hr_encontro', payload.data_hr_encontro);
      form.append('endereco', payload.endereco);
      if (payload.tags) form.append('tags', payload.tags);
      form.append('img', payload.img);
      return this.http.post<Encontro>(url, form);
    }
    return this.http.post<Encontro>(url, {
      titulo: payload.titulo,
      descricao: payload.descricao,
      data_hr_encontro: payload.data_hr_encontro,
      endereco: payload.endereco,
      tags: payload.tags ?? '',
    });
  }

  // ----- CDU024: Moderar Conviventes -----

  listarMembros(id: number): Observable<MembroComunidade[]> {
    return this.http.get<MembroComunidade[]>(`${this.base}/${id}/membros/`);
  }

  moderar(id: number, payload: AplicarAcaoPayload): Observable<AcaoModeracao> {
    return this.http.post<AcaoModeracao>(`${this.base}/${id}/moderar/`, payload);
  }

  historicoConvivente(id: number, conviventeId: number): Observable<AcaoModeracao[]> {
    return this.http.get<AcaoModeracao[]>(
      `${this.base}/${id}/membros/${conviventeId}/historico/`,
    );
  }
}
