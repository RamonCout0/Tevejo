import { Pipe, PipeTransform } from '@angular/core';

/** Cores da logo, na ordem da palavra "tevejo" + o amarelo do girassol. */
export const CORES_DA_MARCA = ['#5EE0CD', '#5ACEE1', '#59A1E0', '#A5C4E0', '#5979E1', '#635AE0', '#F5D170'];

/** Índice estável (0–6) para um texto: a mesma categoria sempre ganha a mesma cor. */
export function indiceDaMarca(texto: string | null | undefined): number {
  const base = (texto ?? '').trim().toLowerCase();
  let hash = 0;
  for (let i = 0; i < base.length; i++) {
    hash = (hash * 31 + base.charCodeAt(i)) | 0;
  }
  return Math.abs(hash) % CORES_DA_MARCA.length;
}

export function iniciaisDe(nome: string | null | undefined): string {
  // Só letras e números contam (ex.: "[visual] Pais" -> "VP").
  const partes = (nome ?? '')
    .split(/\s+/)
    .map((p) => p.replace(/[^\p{L}\p{N}]/gu, ''))
    .filter(Boolean);
  if (partes.length === 0) return '?';
  const letras = partes.length === 1 ? partes[0].slice(0, 2) : partes[0][0] + partes[partes.length - 1][0];
  return letras.toUpperCase();
}

/** Classe `tv-tom-N` (fundo claro + texto escuro da mesma cor) para badges e avatares. */
@Pipe({ name: 'tomDaMarca', standalone: true })
export class TomDaMarcaPipe implements PipeTransform {
  transform(texto: string | null | undefined): string {
    return `tv-tom-${indiceDaMarca(texto)}`;
  }
}

/** Cor sólida da marca para um texto (ex.: bolinha da comunidade na sidebar). */
@Pipe({ name: 'corDaMarca', standalone: true })
export class CorDaMarcaPipe implements PipeTransform {
  transform(texto: string | null | undefined): string {
    return CORES_DA_MARCA[indiceDaMarca(texto)];
  }
}

@Pipe({ name: 'iniciais', standalone: true })
export class IniciaisPipe implements PipeTransform {
  transform(nome: string | null | undefined): string {
    return iniciaisDe(nome);
  }
}
