// ========== CONTADOR DE CARACTERES ==========

// Contador para o campo "Nome"
const nomeField = document.querySelector('input[name="nome"]');
const nomeCharCounter = document.querySelectorAll('.form-group .char-counter')[0];

if (nomeField && nomeCharCounter) {
  nomeField.addEventListener('input', () => {
    const charCurrent = nomeCharCounter.querySelector('.char-current');
    if (charCurrent) {
      charCurrent.textContent = nomeField.value.length;
    }
    // Atualizar preview
    updatePreviewName(nomeField.value);
  });
}

// Contador para o campo "Descrição"
const descricaoField = document.querySelector('textarea[name="descricao"]');
const descricaoCharCounter = document.querySelectorAll('.form-group .char-counter')[1];

if (descricaoField && descricaoCharCounter) {
  descricaoField.addEventListener('input', () => {
    const charCurrent = descricaoCharCounter.querySelector('.char-current');
    if (charCurrent) {
      charCurrent.textContent = descricaoField.value.length;
    }
    // Atualizar preview
    updatePreviewDesc(descricaoField.value);
  });
}

// ========== UPLOAD E PREVIEW DE IMAGEM ==========

const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const previewImage = document.getElementById('preview-image');
const imageName = document.getElementById('image-name');

if (uploadBtn && fileInput) {
  uploadBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validar tipo de arquivo
      if (!file.type.startsWith('image/')) {
        alert('Por favor, selecione uma imagem válida');
        return;
      }

      // Validar tamanho (máx 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('A imagem deve ter no máximo 5MB');
        return;
      }

      // Ler e exibir a imagem
      const reader = new FileReader();
      reader.onload = (event) => {
        previewImage.src = event.target.result;
        
        // Formatar tamanho do arquivo
        const sizeInKB = (file.size / 1024).toFixed(0);
        imageName.textContent = `${sizeInKB}kb`;
      };
      reader.readAsDataURL(file);
    }
  });
}

// ========== ATUALIZAR PREVIEW ==========

function updatePreviewName(name) {
  const previewNameText = document.getElementById('preview-name-text');
  if (previewNameText) {
    previewNameText.textContent = name || 'tevejonomedacomunidade';
  }
}

function updatePreviewDesc(desc) {
  const previewDescText = document.getElementById('preview-desc-text');
  if (previewDescText) {
    previewDescText.textContent = desc || 'Descrição da sua Comunidade';
  }
}

// ========== FORM SUBMISSION ==========

// Adicionar ID ao formulário para o botão submit
const form = document.querySelector('.comunidade-form');
if (form) {
  form.id = 'comunidade-form';
}
