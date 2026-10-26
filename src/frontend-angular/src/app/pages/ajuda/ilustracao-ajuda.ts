import { Component, input } from '@angular/core';

export type CenaAjuda =
  | 'comunidade' | 'criar' | 'conteudo' | 'encontro'
  | 'editor' | 'perfil' | 'privacidade' | 'denuncia';

/**
 * Ilustrações vetoriais do FAQ (CDU027), desenhadas com a paleta e os
 * personagens da marca. Puramente decorativas: o texto da resposta explica tudo.
 */
@Component({
  selector: 'app-ilustracao-ajuda',
  standalone: true,
  host: { class: 'block', 'aria-hidden': 'true' },
  template: `
    <svg viewBox="0 0 240 160" class="w-full h-auto" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="240" height="160" rx="22" fill="#F7F3EC"/>
      <circle cx="205" cy="28" r="34" fill="#5EE0CD" opacity=".18"/>
      <circle cx="30" cy="140" r="40" fill="#635AE0" opacity=".10"/>

      @switch (cena()) {
        @case ('comunidade') {
          <!-- Balão de conversa no centro e três pessoas ao redor -->
          <rect x="78" y="22" width="84" height="46" rx="14" fill="#FFFFFF"/>
          <path d="M110 68 l10 12 l6 -12z" fill="#FFFFFF"/>
          <circle cx="100" cy="45" r="5" fill="#5EE0CD"/><circle cx="120" cy="45" r="5" fill="#59A1E0"/><circle cx="140" cy="45" r="5" fill="#635AE0"/>
          <image href="/assets/personagens/azul.svg" x="44" y="76" width="44" height="66"/>
          <image href="/assets/personagens/amarelo.svg" x="98" y="84" width="44" height="60"/>
          <image href="/assets/personagens/azul.svg" x="152" y="76" width="44" height="66" opacity=".85"/>
        }
        @case ('criar') {
          <!-- Cartão de comunidade sendo montado -->
          <rect x="52" y="26" width="136" height="110" rx="16" fill="#FFFFFF"/>
          <rect x="52" y="26" width="136" height="34" rx="16" fill="#59A1E0"/>
          <rect x="52" y="44" width="136" height="16" fill="#59A1E0"/>
          <circle cx="82" cy="62" r="17" fill="#FFFFFF"/><circle cx="82" cy="62" r="13" fill="#635AE0"/>
          <rect x="72" y="90" width="80" height="8" rx="4" fill="#121214" opacity=".75"/>
          <rect x="72" y="106" width="96" height="6" rx="3" fill="#A5C4E0"/>
          <rect x="72" y="118" width="64" height="6" rx="3" fill="#A5C4E0"/>
          <circle cx="186" cy="124" r="20" fill="#635AE0"/>
          <path d="M186 114v20M176 124h20" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
          <image href="/assets/girassol.svg" x="160" y="14" width="36" height="30"/>
        }
        @case ('conteudo') {
          <!-- Livro aberto com selo de verificado -->
          <path d="M120 46 C100 34 74 34 56 40 L56 126 C74 120 100 120 120 132z" fill="#FFFFFF"/>
          <path d="M120 46 C140 34 166 34 184 40 L184 126 C166 120 140 120 120 132z" fill="#FFFFFF"/>
          <path d="M120 46 L120 132" stroke="#A5C4E0" stroke-width="3"/>
          <rect x="68" y="58" width="40" height="5" rx="2.5" fill="#59A1E0"/><rect x="68" y="72" width="36" height="5" rx="2.5" fill="#A5C4E0"/>
          <rect x="68" y="86" width="40" height="5" rx="2.5" fill="#A5C4E0"/><rect x="132" y="58" width="40" height="5" rx="2.5" fill="#5EE0CD"/>
          <rect x="132" y="72" width="34" height="5" rx="2.5" fill="#A5C4E0"/><rect x="132" y="86" width="40" height="5" rx="2.5" fill="#A5C4E0"/>
          <circle cx="178" cy="118" r="18" fill="#1F8A6E"/>
          <path d="M170 118l6 6l11 -12" stroke="#FFFFFF" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        }
        @case ('encontro') {
          <!-- Calendário com pino de local -->
          <rect x="54" y="38" width="104" height="98" rx="14" fill="#FFFFFF"/>
          <rect x="54" y="38" width="104" height="26" rx="14" fill="#5979E1"/><rect x="54" y="52" width="104" height="12" fill="#5979E1"/>
          <rect x="74" y="28" width="8" height="20" rx="4" fill="#121214" opacity=".7"/><rect x="130" y="28" width="8" height="20" rx="4" fill="#121214" opacity=".7"/>
          @for (l of [0, 1, 2]; track l) {
            @for (c of [0, 1, 2, 3]; track c) {
              <rect [attr.x]="68 + c * 21" [attr.y]="74 + l * 20" width="14" height="12" rx="3"
                    [attr.fill]="l === 1 && c === 2 ? '#635AE0' : '#E7E2F5'"/>
            }
          }
          <path d="M184 66c-13 0-22 10-22 22c0 17 22 38 22 38s22-21 22-38c0-12-9-22-22-22z" fill="#F5D170"/>
          <circle cx="184" cy="88" r="8" fill="#594822"/>
        }
        @case ('editor') {
          <!-- Caixa de texto com barra de formatação e marca-texto -->
          <rect x="40" y="30" width="160" height="104" rx="14" fill="#FFFFFF"/>
          <rect x="40" y="30" width="160" height="26" rx="14" fill="#F1ECE3"/><rect x="40" y="44" width="160" height="12" fill="#F1ECE3"/>
          <text x="56" y="49" font-family="Fredoka, sans-serif" font-weight="700" font-size="14" fill="#121214">B</text>
          <text x="76" y="49" font-family="Georgia, serif" font-style="italic" font-size="14" fill="#121214">I</text>
          <text x="92" y="49" font-family="Fredoka, sans-serif" font-size="14" fill="#121214" text-decoration="underline">U</text>
          <rect x="110" y="38" width="16" height="12" rx="3" fill="#F5D170"/>
          <rect x="56" y="70" width="70" height="7" rx="3.5" fill="#121214" opacity=".8"/>
          <rect x="132" y="70" width="52" height="7" rx="3.5" fill="#A5C4E0"/>
          <rect x="54" y="86" width="96" height="12" rx="3" fill="#F5D170" opacity=".85"/>
          <rect x="58" y="89" width="88" height="6" rx="3" fill="#594822" opacity=".55"/>
          <circle cx="60" cy="112" r="3" fill="#635AE0"/><rect x="70" y="109" width="70" height="6" rx="3" fill="#A5C4E0"/>
          <circle cx="60" cy="124" r="3" fill="#635AE0"/><rect x="70" y="121" width="56" height="6" rx="3" fill="#A5C4E0"/>
          <image href="/assets/personagens/gui.svg" x="168" y="86" width="40" height="60"/>
        }
        @case ('perfil') {
          <!-- Cartão de perfil com foto e câmera -->
          <rect x="50" y="30" width="140" height="104" rx="16" fill="#FFFFFF"/>
          <rect x="50" y="30" width="140" height="34" rx="16" fill="#5EE0CD"/><rect x="50" y="48" width="140" height="16" fill="#5EE0CD"/>
          <circle cx="90" cy="68" r="22" fill="#FFFFFF"/>
          <image href="/assets/personagens/amarelo.svg" x="76" y="50" width="28" height="38"/>
          <circle cx="106" cy="84" r="9" fill="#635AE0"/>
          <rect x="101" y="81" width="10" height="7" rx="2" fill="#FFFFFF"/><circle cx="106" cy="84.5" r="2" fill="#635AE0"/>
          <rect x="70" y="100" width="70" height="8" rx="4" fill="#121214" opacity=".75"/>
          <rect x="70" y="114" width="100" height="6" rx="3" fill="#A5C4E0"/>
        }
        @case ('privacidade') {
          <!-- Escudo com coração e cadeado -->
          <path d="M120 24 L170 42 L170 82 C170 112 148 130 120 140 C92 130 70 112 70 82 L70 42z" fill="#635AE0"/>
          <path d="M120 34 L160 48 L160 82 C160 106 143 121 120 130 C97 121 80 106 80 82 L80 48z" fill="#FFFFFF" opacity=".15"/>
          <path d="M120 106 C100 92 96 80 102 72 C108 64 118 68 120 74 C122 68 132 64 138 72 C144 80 140 92 120 106z" fill="#FFFFFF"/>
          <rect x="176" y="96" width="34" height="28" rx="6" fill="#F5D170"/>
          <path d="M183 96v-8a10 10 0 0 1 20 0v8" stroke="#594822" stroke-width="4" fill="none"/>
          <circle cx="193" cy="110" r="4" fill="#594822"/>
        }
        @case ('denuncia') {
          <!-- Bandeira de denúncia e escudo de moderação -->
          <rect x="70" y="30" width="6" height="104" rx="3" fill="#121214" opacity=".7"/>
          <path d="M76 34 L150 34 L134 56 L150 78 L76 78z" fill="#C2413A"/>
          <path d="M168 70 L200 82 L200 104 C200 122 186 132 168 138 C150 132 136 122 136 104 L136 82z" fill="#5979E1"/>
          <path d="M156 104l9 9l17 -18" stroke="#FFFFFF" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        }
      }
    </svg>
  `,
})
export class IlustracaoAjudaComponent {
  readonly cena = input.required<CenaAjuda>();
}
