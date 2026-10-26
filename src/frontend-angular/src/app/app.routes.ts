import { Routes } from '@angular/router';

import {
  authGuard,
  conviventeGuard,
  curadorGuard,
  termoAceitoGuard,
  termoPendenteGuard,
} from './core/role.guards';
import { podePostarGuard } from './core/comunidade.guards';

// As telas são carregadas sob demanda (loadComponent): o bundle inicial fica
// só com o shell, e cada página baixa o próprio código ao ser aberta.
export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./pages/login/login').then((m) => m.LoginComponent) },
  { path: 'cadastro', loadComponent: () => import('./pages/cadastro/cadastro').then((m) => m.CadastroComponent) },
  {
    path: 'termo-consentimento',
    loadComponent: () =>
      import('./pages/termo-consentimento/termo-consentimento.component').then((m) => m.TermoConsentimentoComponent),
    canActivate: [termoPendenteGuard],
  },

  {
    path: '',
    canActivateChild: [termoAceitoGuard],
    children: [
      // Conteúdo Educacional
      {
        path: 'conteudo-educacional',
        loadComponent: () =>
          import('./pages/conteudo-educacional/conteudo-educacional').then((m) => m.ConteudoEducacionalComponent),
      },
      {
        path: 'conteudo-educacional/:id',
        loadComponent: () =>
          import('./pages/detalhe-conteudo/detalhe-conteudo').then((m) => m.DetalheConteudoComponent),
      },
      {
        path: 'postar-conteudo',
        loadComponent: () =>
          import('./pages/postar-conteudo/postar-conteudo').then((m) => m.PostarConteudoComponent),
        canActivate: [curadorGuard],
      },

      // Comunidades
      {
        path: 'comunidades',
        loadComponent: () =>
          import('./pages/explorar-comunidades/explorar-comunidades').then((m) => m.ExplorarComunidadesComponent),
      },
      {
        path: 'criar-comunidade',
        loadComponent: () => import('./pages/criar-comunidade/criar-comunidade').then((m) => m.CriarComunidade),
        canActivate: [conviventeGuard],
      },
      {
        // CDU012 - Gerenciar comunidades (mesma tela da criação, em modo edição)
        path: 'comunidades/:id/editar',
        loadComponent: () => import('./pages/criar-comunidade/criar-comunidade').then((m) => m.CriarComunidade),
        canActivate: [conviventeGuard],
      },
      {
        path: 'comunidades/:id/moderacao',
        loadComponent: () =>
          import('./pages/moderacao-comunidade/moderacao-comunidade').then((m) => m.ModeracaoComunidadeComponent),
        canActivate: [conviventeGuard],
      },
      {
        path: 'comunidades/:id',
        loadComponent: () =>
          import('./pages/comunidade-detalhe/comunidade-detalhe').then((m) => m.ComunidadeDetalheComponent),
      },
      {
        path: 'comunidades/:id/postar',
        loadComponent: () =>
          import('./pages/postar-comunidade/postar-comunidade').then((m) => m.PostarComunidadeComponent),
        canActivate: [conviventeGuard, podePostarGuard],
      },
      {
        path: 'comunidades/:id/moderar',
        loadComponent: () =>
          import('./pages/moderar-comunidade/moderar-comunidade').then((m) => m.ModerarComunidadeComponent),
        canActivate: [conviventeGuard],
      },
      {
        path: 'comunidades/:id/encontros/criar',
        loadComponent: () =>
          import('./pages/criar-encontro/criar-encontro').then((m) => m.CriarEncontroComponent),
        canActivate: [conviventeGuard],
      },

      // Perfil
      {
        path: 'perfil',
        loadComponent: () => import('./pages/perfil/perfil').then((m) => m.PerfilComponent),
        canActivate: [authGuard],
      },

      // Páginas novas
      {
        path: 'discussoes',
        loadComponent: () => import('./pages/discussoes/discussoes').then((m) => m.DiscussoesComponent),
      },
      {
        path: 'encontros',
        loadComponent: () => import('./pages/encontros/encontros').then((m) => m.EncontrosComponent),
        canActivate: [authGuard],
      },
      {
        path: 'moderacao',
        loadComponent: () =>
          import('./pages/moderacao-picker/moderacao-picker').then((m) => m.ModeracaoPickerComponent),
        canActivate: [authGuard],
      },

      // CDU027 - Ajuda e perguntas frequentes (pública)
      {
        path: 'ajuda',
        loadComponent: () => import('./pages/ajuda/ajuda').then((m) => m.AjudaComponent),
      },

      // CDU028 - Página inicial (pública)
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () => import('./pages/inicio/inicio').then((m) => m.InicioComponent),
      },
    ],
  },

  // Catch-all
  { path: '**', redirectTo: '' },
];
