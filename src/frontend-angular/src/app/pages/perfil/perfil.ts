import { CommonModule } from '@angular/common';
import { Component, computed, effect, inject, signal, untracked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { AuthService } from '../../core/auth.service';
import { EditorTextoComponent } from '../../shared/editor-texto/editor-texto';
import { LIMITES } from '../../shared/limites';
import { CorDaMarcaPipe, IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';
import { RecortarImagemComponent } from '../../shared/recortar-imagem/recortar-imagem';
import { TextoRicoPipe } from '../../shared/texto-rico/texto-rico';
import { ConteudoEducacional, ConteudoService } from '../../services/conteudo.service';
import { Comunidade, ComunidadeService } from '../../services/comunidade.service';

const MAX_FOTO_BYTES = 5 * 1024 * 1024;
/** A foto é reduzida no recorte; o original pode ser maior (fotos de celular). */
const MAX_ORIGINAL_BYTES = 20 * 1024 * 1024;
const FORMATOS_PERMITIDOS = ['image/jpeg', 'image/png'];

interface PostagemMinha {
  id: number;
  titulo: string;
  data: string;
  curtidas: number;
  comunidadeId: number;
  comunidadeNome: string;
}

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterLink, RecortarImagemComponent, EditorTextoComponent,
    CorDaMarcaPipe, IniciaisPipe, TomDaMarcaPipe, TextoRicoPipe,
  ],
  templateUrl: './perfil.html',
  styleUrl: './perfil.css',
})
export class PerfilComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  private conteudoService = inject(ConteudoService);
  private comunidadeService = inject(ComunidadeService);

  readonly perfil = this.auth.perfil;
  readonly isCurador = this.auth.isCurador;
  readonly isConvivente = this.auth.isConvivente;
  readonly limites = LIMITES;

  /** Apenas dois rótulos visíveis: Convivente OU Curador (nunca Moderador) */
  readonly papelLabel = computed(() => {
    if (this.isCurador()) return 'Curador';
    return 'Convivente';
  });

  readonly minhasPostagens = signal<PostagemMinha[]>([]);
  readonly meusConteudos = signal<ConteudoEducacional[]>([]);
  readonly carregandoHistorico = signal(false);

  editando = signal(false);
  enviando = signal(false);
  erro = signal<string | null>(null);
  sucesso = signal<string | null>(null);

  nome = '';
  email = '';
  biografia = '';

  fotoPreview = signal<string | null>(null);
  /** Arquivo aguardando recorte (abre o modal enquanto não for null). */
  imagemParaRecortar = signal<File | null>(null);
  private arquivoFoto: File | null = null;
  removerFoto = false;

  readonly fotoAtual = computed(() => this.perfil()?.foto ?? null);
  private readonly perfilId = computed(() => this.perfil()?.id ?? null);

  constructor() {
    if (!this.perfil()) {
      this.auth.carregarPerfil().subscribe({ error: () => {} });
    }

    effect(() => {
      const p = this.perfil();
      if (p && !this.editando()) {
        this.nome = p.nome ?? '';
        this.email = p.email ?? '';
        this.biografia = p.biografia ?? '';
      }
    });

    // Carrega histórico conforme o papel — só quando o usuário muda, não a
    // cada atualização do perfil (ex.: salvar a foto).
    effect(() => {
      const id = this.perfilId();
      if (id === null) return;
      untracked(() => {
        const p = this.perfil()!;
        if (p.is_curador) {
          this.carregarMeusConteudos(p.id);
        } else {
          this.carregarMinhasPostagens(p.username);
        }
      });
    });
  }

  private carregarMeusConteudos(uid: number): void {
    this.carregandoHistorico.set(true);
    this.conteudoService.listar().subscribe({
      next: (lista) => {
        // Curador herda de Usuario: o id do curador é o mesmo do usuário.
        const meus = lista.filter((c) => c.curador?.id === uid);
        this.meusConteudos.set(meus.slice(0, 5));
        this.carregandoHistorico.set(false);
      },
      error: () => {
        this.meusConteudos.set([]);
        this.carregandoHistorico.set(false);
      },
    });
  }

  private carregarMinhasPostagens(username: string): void {
    this.carregandoHistorico.set(true);
    // Sempre busca a lista atualizada uma única vez (sem recursão: quem não
    // participa de nenhuma comunidade simplesmente fica com o histórico vazio).
    this.comunidadeService.carregarMinhas().subscribe({
      next: (minhas) => this.buscarPostagensDe(username, minhas),
      error: () => {
        this.minhasPostagens.set([]);
        this.carregandoHistorico.set(false);
      },
    });
  }

  private buscarPostagensDe(username: string, minhas: Comunidade[]): void {
    if (minhas.length === 0) {
      this.minhasPostagens.set([]);
      this.carregandoHistorico.set(false);
      return;
    }

    Promise.all(
      minhas.map((c) =>
        firstValueFrom(this.comunidadeService.listarPostagens(c.id))
          .then((postagens) => postagens.filter((p) => p.autor_username === username).map((p) => ({
            id: p.id,
            titulo: p.titulo,
            data: p.criado_em,
            curtidas: p.curtidas_count,
            comunidadeId: c.id,
            comunidadeNome: c.nome,
          })))
          .catch(() => [] as PostagemMinha[]),
      ),
    ).then((listas) => {
      const todas = listas.flat();
      todas.sort((a, b) => (a.data < b.data ? 1 : -1));
      this.minhasPostagens.set(todas.slice(0, 5));
      this.carregandoHistorico.set(false);
    });
  }

  iniciarEdicao(): void {
    const p = this.perfil();
    if (!p) return;
    this.nome = p.nome ?? '';
    this.email = p.email ?? '';
    this.biografia = p.biografia ?? '';
    this.fotoPreview.set(null);
    this.arquivoFoto = null;
    this.removerFoto = false;
    this.erro.set(null);
    this.sucesso.set(null);
    this.editando.set(true);
  }

  cancelar(): void {
    this.editando.set(false);
    this.erro.set(null);
    this.fotoPreview.set(null);
    this.arquivoFoto = null;
    this.removerFoto = false;
  }

  onFotoSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = ''; // permite escolher o mesmo arquivo de novo
    if (!file) return;

    if (!FORMATOS_PERMITIDOS.includes(file.type)) {
      this.erro.set('Arquivo de imagem inválido. Use JPG ou PNG.');
      return;
    }
    if (file.size > MAX_ORIGINAL_BYTES) {
      this.erro.set('A imagem deve ter no máximo 20 MB.');
      return;
    }

    this.erro.set(null);
    this.imagemParaRecortar.set(file);
  }

  /** Recebe a foto já recortada (quadrada, 512px) do modal de recorte. */
  aoRecortarFoto(file: File): void {
    this.imagemParaRecortar.set(null);
    if (file.size > MAX_FOTO_BYTES) {
      this.erro.set('A imagem deve ter no máximo 5 MB.');
      return;
    }
    this.arquivoFoto = file;
    this.removerFoto = false;
    const reader = new FileReader();
    reader.onload = () => this.fotoPreview.set(reader.result as string);
    reader.readAsDataURL(file);
  }

  /** Foto mostrada no topo: na edição considera a prévia nova ou a remoção. */
  fotoExibida(): string | null {
    if (!this.editando()) return this.fotoAtual();
    if (this.removerFoto) return null;
    return this.fotoPreview() || this.fotoAtual();
  }

  marcarRemoverFoto(): void {
    this.arquivoFoto = null;
    this.fotoPreview.set(null);
    this.removerFoto = true;
  }

  salvar(): void {
    if (this.enviando()) return;
    this.erro.set(null);
    this.sucesso.set(null);

    if (this.nome.trim().length < 3) {
      this.erro.set('O nome deve ter pelo menos 3 caracteres.');
      return;
    }

    const form = new FormData();
    form.append('nome', this.nome.trim());
    form.append('email', this.email.trim());
    form.append('biografia', this.biografia ?? '');
    if (this.arquivoFoto) {
      form.append('foto', this.arquivoFoto, this.arquivoFoto.name);
    } else if (this.removerFoto) {
      form.append('foto', '');
    }

    this.enviando.set(true);
    this.auth.atualizarPerfil(form).subscribe({
      next: () => {
        this.enviando.set(false);
        this.editando.set(false);
        this.fotoPreview.set(null);
        this.arquivoFoto = null;
        this.removerFoto = false;
        this.sucesso.set('Dados atualizados com sucesso.');
        // Recarrega o perfil pra garantir que a URL nova da foto chega em todos os signals
        this.auth.carregarPerfil().subscribe({ error: () => {} });
      },
      error: (err) => {
        this.enviando.set(false);
        if (err?.status === 401) {
          this.erro.set('Sessão expirada. Faça login novamente.');
        } else if (err?.error && typeof err.error === 'object') {
          this.erro.set(Object.values(err.error).flat().join(' '));
        } else {
          this.erro.set('Erro ao atualizar os dados. Tente novamente.');
        }
      },
    });
  }

  voltar(): void {
    this.router.navigate(['/']);
  }

  iniciais(): string {
    const nome = this.perfil()?.nome || this.perfil()?.username || '?';
    return nome.trim().split(/\s+/).map((p) => p[0]).join('').slice(0, 2).toUpperCase();
  }
}
