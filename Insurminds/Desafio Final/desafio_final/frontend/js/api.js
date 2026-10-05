import { CONFIG } from "./config.js";
// O modo demonstração (CONFIG.demoMode) usa ./mock.js, carregado sob demanda.
// Importar o arquivo de forma estática quebrava todo o front-end quando ele não existia.
async function loadMock() {
  try {
    return await import("./mock.js");
  } catch {
    throw new Error("O modo de demonstração está ativo, mas o arquivo js/mock.js não foi encontrado. Defina demoMode: false em js/config.js.");
  }
}

// Valida se foi disponibilizada a quantidade mínima de apólices exigida.
// Retorna a mensagem de erro (string) ou null quando está tudo certo.
export function validatePolicyFiles(files = []) {
  const minimum = CONFIG.minFiles;
  const count = files.length;
  if (count >= minimum) return null;

  const policies = quantity => `${quantity} apólice${quantity === 1 ? "" : "s"}`;
  if (count === 0) return `Envie pelo menos ${policies(minimum)} para iniciar a análise.`;
  const missing = minimum - count;
  return `Envie pelo menos ${policies(minimum)} para a análise. Falta${missing === 1 ? "" : "m"} ${policies(missing)}.`;
}

export async function uploadDatasets(files, onProgress = () => {}) {
  const validationError = validatePolicyFiles(files);
  if (validationError) throw new Error(validationError);

  if (CONFIG.demoMode) {
    for (const value of [12, 28, 49, 72, 91, 100]) {
      await delay(300);
      onProgress(value);
    }
    const { createDemoDatasets } = await loadMock();
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
    const { answerDemoQuestion } = await loadMock();
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
