import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

import { ComunidadeService } from '../../services/comunidade.service';
import { IniciaisPipe, TomDaMarcaPipe } from '../../shared/marca';

@Component({
  selector: 'app-moderacao-picker',
  standalone: true,
  imports: [CommonModule, RouterLink, IniciaisPipe, TomDaMarcaPipe],
  templateUrl: './moderacao-picker.html',
})
export class ModeracaoPickerComponent {
  private comunidades = inject(ComunidadeService);

  readonly comunidadesModeradas = computed(() =>
    this.comunidades.minhas().filter((c) => c.is_moderador),
  );
}
