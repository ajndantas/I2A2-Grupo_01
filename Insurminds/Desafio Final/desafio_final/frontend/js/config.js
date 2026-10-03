export const CONFIG = {
  apiBaseUrl: "http://127.0.0.1:8000", // Para testes
  //apiBaseUrl: "https://agente-nfs-574973424283.us-central1.run.app",
  demoMode: false,
  maxFileSize: 500 * 1024 * 1024,
  processingMessages: [
    "Enviando as apólices com segurança...",
    "Identificando os documentos...",
    "Lendo coberturas e condições...",
    "Relacionando as duas apólices...",
    "Preparando o assistente para suas perguntas..."
  ]
};
