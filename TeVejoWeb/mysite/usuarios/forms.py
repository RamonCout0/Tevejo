from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


# ============================================================
# LOGIN
# ============================================================

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Usuário",
        widget=forms.TextInput(attrs={
            "placeholder": "Digite seu usuário",
            "class": "form-control",
            "autocomplete": "username",
        }),
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Digite sua senha",
            "class": "form-control",
            "autocomplete": "current-password",
        }),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if " " in username:
            raise forms.ValidationError(
                "O nome de usuário não pode conter espaços."
            )

        return username


# ============================================================
# CADASTRO
# ============================================================

class CadastroForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Usuário",
        widget=forms.TextInput(attrs={
            "placeholder": "Escolha um nome de usuário",
            "class": "form-control",
            "autocomplete": "username",
        }),
    )

    nome = forms.CharField(
        max_length=100,
        label="Nome completo",
        widget=forms.TextInput(attrs={
            "placeholder": "Digite seu nome completo",
            "class": "form-control",
        }),
    )

    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            "placeholder": "Digite seu e-mail",
            "class": "form-control",
            "autocomplete": "email",
        }),
    )

    foto = forms.ImageField(
        label="Foto de perfil",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
        }),
    )

    biografia = forms.CharField(
        label="Biografia",
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "Fale um pouco sobre você (opcional)",
            "class": "form-control",
            "rows": 4,
        }),
    )

    password = forms.CharField(
        label="Senha",
        min_length=6,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Crie uma senha",
            "class": "form-control",
            "autocomplete": "new-password",
        }),
    )

    password_confirm = forms.CharField(
        label="Confirmar senha",
        min_length=6,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirme sua senha",
            "class": "form-control",
            "autocomplete": "new-password",
        }),
    )

    # ============================================================
    # VALIDAÇÕES
    # ============================================================

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if " " in username:
            raise forms.ValidationError(
                "O nome de usuário não pode conter espaços."
            )

        return username

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        if len(nome) < 3:
            raise forms.ValidationError(
                "O nome deve ter pelo menos 3 caracteres."
            )

        return nome

    def clean(self):
        cleaned = super().clean()

        password = cleaned.get("password")
        password_confirm = cleaned.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error(
                "password_confirm",
                "As senhas não coincidem."
            )

        return cleaned
