# Frontend Angular — TeVejo

Projeto frontend da plataforma TeVejo, construído com **Angular 21** e **Tailwind CSS v4**.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

| Ferramenta | Versão mínima | Como verificar         |
| ---------- | ------------- | ---------------------- |
| Node.js    | 22.x ou 24.x  | `node --version`       |
| npm        | 10+           | `npm --version`        |
| Git        | qualquer      | `git --version`        |

> Angular 21 **exige** Node.js 22+. Se estiver em uma versão antiga, baixe em [nodejs.org](https://nodejs.org/) ou use [nvm](https://github.com/nvm-sh/nvm) (Linux/macOS) / [nvm-windows](https://github.com/coreybutler/nvm-windows) (Windows).

## Passo a passo

### 1. Clonar o repositório

```bash
git clone https://github.com/tads-cnat/tevejo.git
cd tevejo/src/frontend-angular
```

### 2. Instalar as dependências

Na pasta `src/frontend-angular/`, rode:

```bash
npm install
```

Isso instala todas as dependências listadas no `package.json`, incluindo Angular, Tailwind v4 (`tailwindcss`, `@tailwindcss/postcss`), PostCSS e Vitest.

### 3. (Opcional) Instalar o Angular CLI globalmente

Para usar o comando `ng` em qualquer lugar:

```bash
npm install -g @angular/cli@21
```

Se preferir não instalar globalmente, use `npx ng` no lugar de `ng` em todos os comandos abaixo.

### 4. Rodar o servidor de desenvolvimento

```bash
npm start
```

ou diretamente:

```bash
ng serve
```

Abra o navegador em [http://localhost:4200](http://localhost:4200). A aplicação recarrega automaticamente a cada alteração nos arquivos-fonte.

## Outros comandos úteis

### Build de produção

```bash
npm run build
```

Gera os artefatos otimizados em `dist/frontend-angular/`.

### Build em modo watch (desenvolvimento)

```bash
npm run watch
```

### Rodar os testes unitários

```bash
npm test
```

Executa os testes com [Vitest](https://vitest.dev/).

### Gerar componente, serviço, etc.

```bash
ng generate component nome-do-componente
ng generate service nome-do-servico
ng generate --help   # lista todos os schematics
```

## Stack

- **Angular 21** com componentes standalone
- **Tailwind CSS v4** (configurado via `@import "tailwindcss"` e bloco `@theme` em `src/styles.css`)
- **PostCSS** com o plugin `@tailwindcss/postcss` (config em `.postcssrc.json`)
- **Font Awesome 6** carregado via CDN no `index.html`
- **Vitest** para testes unitários

As cores e gradientes da marca (`tevejo-azul`, `tevejo-escuro`, `tevejo-gradiente`, etc.) são definidos no bloco `@theme` em `src/styles.css` e ficam disponíveis como utilities do Tailwind (`text-tevejo-azul`, `bg-tevejo-gradiente`, …).

## Troubleshooting

**`Cannot apply unknown utility class 'text-tevejo-*'` no build**
Verifique se o `src/styles.css` começa com `@import "tailwindcss";` seguido do bloco `@theme { ... }` com as variáveis `--color-tevejo-*`. As diretivas v3 (`@tailwind base/components/utilities`) **não** devem estar presentes.

**Estilos do Tailwind sendo sobrescritos**
Se classes como `h-14` não aplicam visualmente apesar de aparecerem no `styles.css` compilado, verifique se nenhum CSS externo não-layered (ex.: Bulma, Bootstrap via CDN) está sendo carregado no `index.html` — ele venceria as utilities do Tailwind v4 na cascata.

**Erro de versão do Node**
Se o `npm install` falhar com mensagens sobre `engines`, atualize o Node para 22+ ou use `nvm use 22`.

**Cache do dev server**
Após mudanças em configurações do Tailwind/PostCSS, pode ser necessário parar o `ng serve`, apagar `.angular/cache/` e reiniciar.
