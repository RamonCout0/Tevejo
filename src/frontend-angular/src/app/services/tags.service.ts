import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';

export interface Tag {
  id: number;
  nome: string;
}

@Injectable({ providedIn: 'root' })
export class TagsService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/conteudos/tags`;

  listar(): Observable<Tag[]> {
    return this.http.get<Tag[]>(`${this.base}/`);
  }

  criar(nome: string): Observable<Tag> {
    return this.http.post<Tag>(`${this.base}/`, { nome });
  }
}
