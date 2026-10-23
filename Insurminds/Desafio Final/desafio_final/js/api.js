import { CONFIG } from "./config.js";
// O modo demonstração (CONFIG.demoMode) usa ./mock.js, carregado sob demanda.
// Importar o arquivo de forma estática quebrava todo o front-end quando ele não existia.

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

  const formData = new FormData();
  for (const file of files) {
    // O backend espera o campo "files" e aceita múltiplos UploadFile.
    formData.append("files", file);
  }

  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", `${CONFIG.apiBaseUrl}/api/datasets/uploads`);
    request.upload.addEventListener("progress", event => {
      if (event.lengthComputable) {
        onProgress(Math.min(95, (event.loaded / event.total) * 95));
      }
    });
    request.addEventListener("load", () => {
      try {
        const response = new Response(request.responseText, { status: request.status });
        parseResponse(response)
          .then(result => {
            onProgress(100);
            resolve(result);
          })
          .catch(reject);
      } catch (error) {
        reject(error);
      }
    });
    request.addEventListener("error", () => {
      reject(new Error("Não foi possível enviar os arquivos. Verifique sua conexão e tente novamente."));
    });
    request.addEventListener("abort", () => {
      reject(new Error("O envio dos arquivos foi cancelado."));
    });
    request.send(formData);
  });
}

export async function askQuestion(datasetIds, question) {
  if (!Array.isArray(datasetIds) || !datasetIds.length) {
    throw new Error("Nenhum dataset foi associado aos arquivos.");
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
      "Não foi possível concluir a solicitação. Atualize a pagina e Tente novamente."
    );
  }
  return payload;
}

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
