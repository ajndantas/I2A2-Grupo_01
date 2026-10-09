import { CONFIG } from "./config.js";
import { createDemoDataset, answerDemoQuestion } from "./mock.js";

const datasetsUrl = () => `${CONFIG.apiBaseUrl}${CONFIG.apiDatasetsPath}`;

/**
 * Envia um ou mais arquivos para POST /api/datasets/uploads (campo multipart "files").
 * Retorno normalizado: { dataset_ids: string[], filenames: string[], status: string }
 */
export function uploadDatasets(files, onProgress = () => {}) {
  if (CONFIG.demoMode) return uploadDemo(files, onProgress);

  return new Promise((resolve, reject) => {
    const formData = new FormData();
    files.forEach(file => formData.append("files", file, file.name));

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${datasetsUrl()}/uploads`);
    xhr.withCredentials = true; // o backend guarda o contexto na sessão (cookie)

    // O envio vai até 90%; o restante é o processamento (OCR/leitura) no servidor.
    xhr.upload.onprogress = event => {
      if (event.lengthComputable) onProgress(Math.min(90, Math.round((event.loaded / event.total) * 90)));
    };
    xhr.onload = () => {
      const payload = safeJson(xhr.responseText);
      if (xhr.status < 200 || xhr.status >= 300) return reject(new Error(errorMessage(payload)));
      onProgress(100);
      try { resolve(normalizeUpload(payload, files)); } catch (error) { reject(error); }
    };
    xhr.onerror = () => reject(new Error("Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente."));
    xhr.onabort = () => reject(new Error("O envio foi cancelado."));
    xhr.send(formData);
  });
}

/**
 * Consulta os datasets: POST /api/datasets/{ds_1,ds_2,...}/query  body: { question }
 * Retorno normalizado conforme OutputSchema: { answer, type, table|null, chart|null }
 */
export async function askQuestion(datasetIds, question) {
  if (CONFIG.demoMode) {
    await delay(900);
    return normalizeAnswer(answerDemoQuestion(question));
  }

  const ids = (Array.isArray(datasetIds) ? datasetIds : [datasetIds]).map(encodeURIComponent).join(",");
  const response = await fetch(`${datasetsUrl()}/${ids}/query`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(errorMessage(payload));
  return normalizeAnswer(payload);
}

/**
 * Encerra a sessão atual no backend: GET /api/datasets/sessions/new
 * O backend descarta o contexto/datasets da sessão, limpa o cookie de sessão e
 * responde com um redirecionamento (303) para "/". Como o redirecionamento não
 * interessa ao frontend, ele não é seguido (redirect: "manual").
 */
export async function startNewSession() {
  if (CONFIG.demoMode) return;

  const response = await fetch(`${datasetsUrl()}/sessions/new`, {
    method: "GET",
    credentials: "include", // envia/atualiza o cookie de sessão
    redirect: "manual"      // não segue o 303 para "/"
  });
  // Com redirect "manual" a resposta chega como "opaqueredirect" (ok = false); isso é sucesso.
  if (response.type !== "opaqueredirect" && !response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(errorMessage(payload));
  }
}

/* ---------- normalização das respostas ---------- */

function normalizeUpload(payload, files) {
  const dataset_ids = Array.isArray(payload.dataset_ids) ? payload.dataset_ids : [];
  if (!dataset_ids.length) throw new Error("O servidor não retornou nenhum dataset para os arquivos enviados.");
  const filenames = Array.isArray(payload.filenames) && payload.filenames.length ? payload.filenames : files.map(file => file.name);
  return { dataset_ids, filenames, status: payload.status || "ready" };
}

function normalizeAnswer(payload) {
  const answer = typeof payload.answer === "string" ? payload.answer : "";
  const table = isValidTable(payload.table) ? payload.table : null;
  const chart = isValidChart(payload.chart) ? payload.chart : null;
  let type = payload.type;
  if (!["text", "table", "chart", "mixed"].includes(type)) type = table && chart ? "mixed" : table ? "table" : chart ? "chart" : "text";
  return { answer, type, table, chart };
}

const isValidTable = table => Boolean(table) && Array.isArray(table.columns) && table.columns.length > 0 && Array.isArray(table.rows);
const isValidChart = chart => Boolean(chart) && Array.isArray(chart.labels) && Array.isArray(chart.datasets) && chart.datasets.length > 0;

/* ---------- utilitários ---------- */

function errorMessage(payload) {
  const detail = payload?.detail;
  if (typeof detail === "string" && detail) return detail;
  if (Array.isArray(detail) && detail.length) return detail.map(item => item.msg || String(item)).join("; ");
  return payload?.message || "Não foi possível concluir a solicitação. Tente novamente.";
}

const safeJson = text => { try { return JSON.parse(text); } catch { return {}; } };

async function uploadDemo(files, onProgress) {
  for (const value of [12, 28, 49, 72, 91, 100]) {
    await delay(420);
    onProgress(value);
  }
  return createDemoDataset(files);
}

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
