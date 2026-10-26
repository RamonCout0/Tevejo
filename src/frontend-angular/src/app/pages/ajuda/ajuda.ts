import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { GuiaService } from '../../core/guia.service';
import { CenaAjuda, IlustracaoAjudaComponent } from './ilustracao-ajuda';

interface Pergunta {
  id: string;
  grupo: string;
  pergunta: string;
  /** Parágrafos da resposta (texto simples). */
  resposta: string[];
  cena: CenaAjuda;
  link?: { texto: string; rota: string };
}

const PERGUNTAS: Pergunta[] = [
  {
    id: 'o-que-e',
    grupo: 'Primeiros passos',
    pergunta: 'O que é o TeVejo?',
    cena: 'comunidade',
    resposta: [
      'O TeVejo é um espaço para acolher, informar e conectar pessoas que convivem com o autismo: famílias, cuidadores, educadores e pessoas autistas.',
      'Aqui você encontra conteúdos confiáveis, conversa em comunidades sobre assuntos do seu interesse e participa de encontros.',
    ],
  },
  {
    id: 'participar',
    grupo: 'Primeiros passos',
    pergunta: 'Como participo de uma comunidade?',
    cena: 'comunidade',
    resposta: [
      'Abra "Comunidades" no menu, procure pelo nome ou toque em uma categoria.',
      'Ao abrir a comunidade, toque no botão "Participar". Pronto: você já pode postar, comentar e curtir.',
      'Para sair, toque em "Participando" na página da comunidade.',
    ],
    link: { texto: 'Ver comunidades', rota: '/comunidades' },
  },
  {
    id: 'criar',
    grupo: 'Primeiros passos',
    pergunta: 'Como crio a minha própria comunidade?',
    cena: 'criar',
    resposta: [
      'No menu, toque em "Criar comunidade". Dê um nome, escreva sobre o que vocês vão conversar e escolha uma categoria.',
      'Se quiser, coloque um ícone e um banner: depois de escolher a foto, dá para arrastar e dar zoom para ajustar.',
      'Quem cria a comunidade vira moderador(a) e pode editar as informações, criar encontros e cuidar da convivência.',
    ],
    link: { texto: 'Criar comunidade', rota: '/criar-comunidade' },
  },
  {
    id: 'conteudos',
    grupo: 'Conteúdos e encontros',
    pergunta: 'Os conteúdos educacionais são confiáveis?',
    cena: 'conteudo',
    resposta: [
      'Sim. Eles são publicados por curadores (profissionais da área) e sempre mostram a fonte original.',
      'Se encontrar algo desatualizado ou incorreto, abra o conteúdo e toque em "Denunciar" para avisar a curadoria.',
    ],
    link: { texto: 'Ver conteúdos', rota: '/conteudo-educacional' },
  },
  {
    id: 'encontros',
    grupo: 'Conteúdos e encontros',
    pergunta: 'Como encontro os encontros marcados?',
    cena: 'encontro',
    resposta: [
      'Toque em "Encontros" no menu para ver os próximos encontros de todas as comunidades. Use "Minhas comunidades" para ver só os seus.',
      'Toque em um encontro para ver a descrição completa, o endereço (ou link) e a comunidade que organiza.',
    ],
    link: { texto: 'Ver encontros', rota: '/encontros' },
  },
  {
    id: 'formatar',
    grupo: 'Escrevendo e perfil',
    pergunta: 'Como deixo um texto em negrito ou grifado?',
    cena: 'editor',
    resposta: [
      'Selecione o trecho e toque no botão da barra acima do texto: B para negrito, I para itálico, U para sublinhado e o marca-texto para grifar.',
      'Também dá para criar listas e citações. O texto já aparece formatado enquanto você escreve.',
    ],
  },
  {
    id: 'foto',
    grupo: 'Escrevendo e perfil',
    pergunta: 'Como troco minha foto de perfil?',
    cena: 'perfil',
    resposta: [
      'Abra "Meu perfil" (no menu ou na sua foto no topo da tela) e toque em "Editar perfil".',
      'Toque na câmera, escolha a foto, ajuste o recorte arrastando e com o zoom e salve.',
    ],
    link: { texto: 'Abrir meu perfil', rota: '/perfil' },
  },
  {
    id: 'dados',
    grupo: 'Segurança e convivência',
    pergunta: 'Meus dados estão seguros?',
    cena: 'privacidade',
    resposta: [
      'Seus dados de perfil são usados só para o funcionamento da plataforma, conforme o termo de consentimento que você aceitou ao entrar.',
      'Seu e-mail não aparece para outras pessoas: nas comunidades aparecem apenas seu nome e sua foto.',
    ],
  },
  {
    id: 'ofensivo',
    grupo: 'Segurança e convivência',
    pergunta: 'Vi algo ofensivo. O que faço?',
    cena: 'denuncia',
    resposta: [
      'Toque na bandeirinha ao lado da postagem ou do comentário e escolha o motivo. A denúncia vai para a moderação da comunidade.',
      'Quem denunciou não é identificado para o autor da publicação.',
    ],
  },
  {
    id: 'restricao',
    grupo: 'Segurança e convivência',
    pergunta: 'O que acontece se eu for restrito(a) ou banido(a)?',
    cena: 'denuncia',
    resposta: [
      'Na restrição, você continua vendo a comunidade, mas não pode postar nem comentar até a data informada.',
      'No banimento, você sai da comunidade e não pode entrar de novo. Em ambos os casos, a moderação registra o motivo.',
    ],
  },
];

/** CDU027 - Consultar ajuda e perguntas frequentes. */
@Component({
  selector: 'app-ajuda',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, IlustracaoAjudaComponent],
  templateUrl: './ajuda.html',
})
export class AjudaComponent {
  private auth = inject(AuthService);
  readonly guia = inject(GuiaService);

  readonly busca = signal('');
  readonly aberta = signal<string | null>(PERGUNTAS[0].id);

  readonly grupos = computed(() => {
    const termo = this.normalizar(this.busca());
    const filtradas = PERGUNTAS.filter((p) =>
      !termo || this.normalizar([p.pergunta, ...p.resposta].join(' ')).includes(termo),
    );
    const mapa = new Map<string, Pergunta[]>();
    for (const p of filtradas) mapa.set(p.grupo, [...(mapa.get(p.grupo) ?? []), p]);
    return [...mapa.entries()].map(([nome, perguntas]) => ({ nome, perguntas }));
  });

  readonly logado = computed(() => !!this.auth.token());

  alternar(id: string): void {
    this.aberta.update((atual) => (atual === id ? null : id));
  }

  /** Busca sem diferenciar acentos e maiúsculas ("duvida" acha "dúvida"). */
  private normalizar(texto: string): string {
    return texto.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
  }
}
