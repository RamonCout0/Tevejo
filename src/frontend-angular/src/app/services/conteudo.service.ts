import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { Tag } from './tags.service';

export interface Curador {
  id: number;
  nome: string;
  especialidade: string;
}

export type MotivoDenuncia = 'desatualizado' | 'incorreto' | 'link_quebrado' | 'outro';
export type StatusDenuncia = 'em_analise' | 'resolvida';

export interface MinhaDenuncia {
  id: number;
  motivo: MotivoDenuncia;
  motivo_display: string;
  status: StatusDenuncia;
  criado_em: string;
}

export interface ConteudoEducacional {
  id: number;
  titulo: string;
  fonte: string;
  descricao: string;
  tipos: Tag[];
  curador: Curador | null;
  minha_denuncia: MinhaDenuncia | null;
  criado_em: string;
}

export interface CriarConteudoPayload {
  titulo: string;
  fonte: string;
  descricao: string;
  tipos_ids: number[];
}

export interface DenunciaPayload {
  motivo: MotivoDenuncia;
  descricao?: string;
}

export interface Denuncia {
  id: number;
  conteudo: number;
  convivente: string;
  motivo: MotivoDenuncia;
  motivo_display: string;
  descricao: string;
  status: StatusDenuncia;
  status_display: string;
  criado_em: string;
}

@Injectable({ providedIn: 'root' })
export class ConteudoService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/conteudos/conteudo-educacional`;

  listar(): Observable<ConteudoEducacional[]> {
    return this.http.get<ConteudoEducacional[]>(`${this.base}/`);
  }

  criar(payload: CriarConteudoPayload): Observable<ConteudoEducacional> {
    return this.http.post<ConteudoEducacional>(`${this.base}/`, payload);
  }

  atualizar(id: number, payload: Partial<CriarConteudoPayload>): Observable<ConteudoEducacional> {
    return this.http.patch<ConteudoEducacional>(`${this.base}/${id}/`, payload);
  }

  remover(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }

  obterPorId(id: number): Observable<ConteudoEducacional> {
    return this.http.get<ConteudoEducacional>(`${this.base}/${id}/`);
  }

  denunciar(id: number, payload: DenunciaPayload): Observable<Denuncia> {
    return this.http.post<Denuncia>(`${this.base}/${id}/denunciar/`, payload);
  }
}
