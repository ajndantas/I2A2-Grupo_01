export const CONFIG = {
  apiBaseUrl: "http://127.0.0.1:8000",
  //apiBaseUrl: "https://agente-nfs-574973424283.us-central1.run.app",
  apiDatasetsPath: "/api/datasets", // prefixo do router em app/rotas/datasets.py
  demoMode: false,
  maxFileSize: 500 * 1024 * 1024,   // limite por arquivo
  maxFiles: 10,                     // limite de arquivos por análise
  processingMessages: [
    "Enviando os arquivos com segurança...",
    "Lendo o conteúdo dos documentos...",
    "Extraindo texto de PDFs e imagens (OCR)...",
    "Organizando os dados para a análise...",
    "Preparando o agente para suas perguntas..."
  ]
};
