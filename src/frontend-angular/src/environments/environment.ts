export const environment = {
  production: true,
  // Em produção o nginx (Dockerfile) serve o front e encaminha /api e /media
  // para o backend na mesma origem.
  apiUrl: '/api',
  googleClientId: '737343454700-4t7lpkk0ofccmf21bc4s9nnkj56rkels.apps.googleusercontent.com',
};
