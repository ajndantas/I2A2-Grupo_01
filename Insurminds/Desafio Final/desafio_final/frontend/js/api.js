import { CONFIG } from "./config.js";
import { createDemoDatasets, answerDemoQuestion } from "./mock.js";

export async function uploadDatasets(files, onProgress = () => {}) {
  if (!files?.length) throw new Error("Selecione pelo menos um arquivo.");

  if (CONFIG.demoMode) {
    for (const value of [12, 28, 49, 72, 91, 100]) {
      await delay(300);
      onProgress(value);
    }
    return createDemoDatasets(files);
  }

  const formData = new FormData();
  for (const file of files) {
    // O backend espera o campo "files" e aceita múltiplos UploadFile.
    formData.append("files", file);
  }

  const response = await fetch(`${CONFIG.apiBaseUrl}/api/datasets/uploads`, {
    method: "POST",
    body: formData
  });

  return parseResponse(response);
}

export async function askQuestion(datasetIds, question) {
  if (!Array.isArray(datasetIds) || !datasetIds.length) {
    throw new Error("Nenhum dataset foi associado aos arquivos.");
  }

  if (CONFIG.demoMode) {
    await delay(900);
    return answerDemoQuestion(question);
  }

  // O backend recebe os IDs no path separados por vírgula.
  const datasetIdsPath = datasetIds.join(",");
  const response = await fetch(
    `${CONFIG.apiBaseUrl}/api/datasets/${datasetIdsPath}/query`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    }
  );

  return parseResponse(response);
}

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      payload.detail ||
      payload.message ||
      "Não foi possível concluir a solicitação. Tente novamente."
    );
  }
  return payload;
}

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
