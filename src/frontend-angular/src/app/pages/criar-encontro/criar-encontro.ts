import { Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';

import { ComunidadeService } from '../../services/comunidade.service';
import { EditorTextoComponent } from '../../shared/editor-texto/editor-texto';
import { LIMITES } from '../../shared/limites';
import { RecortarImagemComponent } from '../../shared/recortar-imagem/recortar-imagem';

/** CDU010 - Criar Encontro. */
@Component({
  selector: 'app-criar-encontro',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, EditorTextoComponent, RecortarImagemComponent],
  templateUrl: './criar-encontro.html',
})
export class CriarEncontroComponent implements OnInit {
  private fb = inject(FormBuilder);
  private comunidadeService = inject(ComunidadeService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  readonly limites = LIMITES;

  encontroForm!: FormGroup;
  comunidadeId!: number;
  arquivoImagem: File | null = null;

  // Signals: o app roda sem zone.js, então campos comuns alterados dentro
  // de um subscribe não redesenhariam a tela.
  readonly mensagemErro = signal('');
  readonly mensagemSucesso = signal('');
  readonly enviando = signal(false);
  readonly previaImagem = signal<string | null>(null);
  readonly imagemParaRecortar = signal<File | null>(null);

  /** Valor mínimo do campo de data: agora (sem segundos), no fuso local. */
  readonly agoraLocal = (() => {
    const agora = new Date();
    agora.setMinutes(agora.getMinutes() - agora.getTimezoneOffset());
    return agora.toISOString().slice(0, 16);
  })();

  ngOnInit(): void {
    this.comunidadeId = Number(this.route.snapshot.paramMap.get('id'));

    this.encontroForm = this.fb.group({
      titulo: ['', [Validators.required, Validators.maxLength(LIMITES.encontroTitulo)]],
      descricao: ['', [Validators.required, Validators.maxLength(LIMITES.encontroDescricao)]],
      data_hr_encontro: ['', Validators.required],
      endereco: ['', [Validators.required, Validators.maxLength(LIMITES.encontroEndereco)]],
      tags: ['', Validators.maxLength(LIMITES.encontroTags)],
    });
  }

  invalido(campo: string): boolean {
    const controle = this.encontroForm.get(campo);
    return !!controle && controle.invalid && controle.touched;
  }

  tamanho(campo: string): number {
    return (this.encontroForm.get(campo)?.value ?? '').length;
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      this.mensagemErro.set('Selecione um arquivo de imagem.');
      return;
    }
    this.mensagemErro.set('');
    this.imagemParaRecortar.set(file);
  }

  aoRecortar(file: File): void {
    this.imagemParaRecortar.set(null);
    this.arquivoImagem = file;
    const reader = new FileReader();
    reader.onload = () => this.previaImagem.set(reader.result as string);
    reader.readAsDataURL(file);
  }

  removerImagem(): void {
    this.arquivoImagem = null;
    this.previaImagem.set(null);
  }

  salvarEncontro(): void {
    // Fluxo de Exceção I - Campos obrigatórios não preenchidos
    if (this.encontroForm.invalid) {
      this.mensagemErro.set('Preencha todos os campos obrigatórios antes de continuar.');
      this.encontroForm.markAllAsTouched();
      return;
    }
    if (this.encontroForm.value.data_hr_encontro < this.agoraLocal) {
      this.mensagemErro.set('Escolha uma data e horário no futuro.');
      return;
    }

    this.mensagemErro.set('');
    this.enviando.set(true);

    const payload = {
      ...this.encontroForm.value,
      img: this.arquivoImagem,
    };

    // Fluxo Principal
    this.comunidadeService.criarEncontro(this.comunidadeId, payload).subscribe({
      next: () => {
        this.mensagemSucesso.set('Encontro criado com sucesso.');
        this.enviando.set(false);
        setTimeout(() => this.voltar(), 1500);
      },
      error: (err) => {
        // Fluxo de Exceção II - Erro ao salvar
        // 403: só o moderador cria encontros; 400: dados inválidos (ex.: data).
        const erroApi = err?.error?.erro;
        if (err?.status === 403 && typeof erroApi === 'string') {
          this.mensagemErro.set(erroApi);
        } else if (err?.status === 400 && err?.error && typeof err.error === 'object') {
          this.mensagemErro.set(Object.values(err.error).flat().join(' '));
        } else {
          this.mensagemErro.set('Erro ao salvar o encontro. Tente novamente mais tarde.');
        }
        this.enviando.set(false);
      },
    });
  }

  // Fluxo Alternativo I - Cancelamento
  voltar(): void {
    // Retorna para o detalhe da comunidade
    this.router.navigate(['/comunidades', this.comunidadeId]);
  }
}
