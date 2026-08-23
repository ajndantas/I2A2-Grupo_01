import { CONFIG } from "./config.js";
import { createDemoDataset, answerDemoQuestion } from "./mock.js";

export async function uploadDataset(file, onProgress = () => {}) {
  if (CONFIG.demoMode) {
    for (const value of [12, 28, 49, 72, 91, 100]) {
      await delay(420);
      onProgress(value);
    }
    return createDemoDataset(file);
  }

  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${CONFIG.apiBaseUrl}/api/datasets/upload`, {
    method: "POST",
    body: formData
  });
  return parseResponse(response);
}

export async function askQuestion(datasetId, question) {
  if (CONFIG.demoMode) {
    await delay(900);
    return answerDemoQuestion(question);
  }

  const response = await fetch(`${CONFIG.apiBaseUrl}/api/datasets/${datasetId}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  return parseResponse(response);
}

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || payload.message || "Não foi possível concluir a solicitação.");
  return payload;
}

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
