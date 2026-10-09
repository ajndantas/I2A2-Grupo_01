import { CONFIG } from "./config.js";
import { uploadDatasets, askQuestion, startNewSession } from "./api.js";

const $ = selector => document.querySelector(selector);
const elements = {
  uploadView: $("#uploadView"), processingView: $("#processingView"), workspaceView: $("#workspaceView"),
  dropzone: $("#dropzone"), fileInput: $("#fileInput"), selectFileButton: $("#selectFileButton"),
  fileListWrap: $("#fileListWrap"), fileList: $("#fileList"), fileCount: $("#fileCount"), clearAllButton: $("#clearAllButton"),
  processButton: $("#processButton"), processLabel: $("#processLabel"), uploadError: $("#uploadError"),
  processingMessage: $("#processingMessage"), progressBar: $("#progressBar"), newAnalysisButton: $("#newAnalysisButton"),
  datasetName: $("#datasetName"), datasetFiles: $("#datasetFiles"),
  suggestions: $("#suggestions"), messages: $("#messages"), questionForm: $("#questionForm"),
  questionInput: $("#questionInput"), sendButton: $("#sendButton")
};

let selectedFiles = [];   // arquivos escolhidos, ainda não enviados
let activeDataset = null; // { dataset_ids, filenames, status } devolvido por POST /uploads
const chartInstances = [];
const chartPalette = ["#0b6b64", "#35a08f", "#db9b41", "#7e918e", "#c8d5d2", "#5b7fa6", "#b4636b", "#8a6fb0"];
const suggestionTexts = ["Quem é o tomador dos serviços ?", "Quem é o fornecedor dos serviços ?", "Qual é o serviço oferecido ?", "Qual é o endereço do tomador de serviços ?"];
const acceptedExtensions = [".csv", ".txt", ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"];

/* ---------- eventos ---------- */
elements.selectFileButton.addEventListener("click", event => { event.stopPropagation(); elements.fileInput.click(); });
elements.dropzone.addEventListener("click", () => elements.fileInput.click());
elements.dropzone.addEventListener("keydown", event => { if (["Enter", " "].includes(event.key)) { event.preventDefault(); elements.fileInput.click(); } });
elements.fileInput.addEventListener("change", () => { addFiles(Array.from(elements.fileInput.files)); elements.fileInput.value = ""; });
elements.clearAllButton.addEventListener("click", clearFiles);
elements.processButton.addEventListener("click", processFiles);
elements.newAnalysisButton.addEventListener("click", resetApp);
elements.questionForm.addEventListener("submit", submitQuestion);
elements.questionInput.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); elements.questionForm.requestSubmit(); }
});
elements.questionInput.addEventListener("input", autoResize);

for (const eventName of ["dragenter", "dragover"]) elements.dropzone.addEventListener(eventName, event => { event.preventDefault(); elements.dropzone.classList.add("dragover"); });
for (const eventName of ["dragleave", "drop"]) elements.dropzone.addEventListener(eventName, event => { event.preventDefault(); elements.dropzone.classList.remove("dragover"); });
elements.dropzone.addEventListener("drop", event => addFiles(Array.from(event.dataTransfer.files)));

/* ---------- seleção e remoção de arquivos ---------- */
function addFiles(files) {
  hideError();
  const errors = [];
  for (const file of files) {
    const extension = file.name.includes(".") ? file.name.slice(file.name.lastIndexOf(".")).toLowerCase() : "";
    if (!acceptedExtensions.includes(extension)) { errors.push(`"${file.name}": selecione um arquivo CSV, TXT, PDF ou imagem.`); continue; }
    if (file.size > CONFIG.maxFileSize) { errors.push(`"${file.name}": ultrapassa o limite recomendado de ${formatBytes(CONFIG.maxFileSize)}.`); continue; }
    // O backend identifica cada documento pelo nome do arquivo, então nomes repetidos não são aceitos.
    if (selectedFiles.some(item => item.name === file.name)) { errors.push(`"${file.name}": já foi adicionado.`); continue; }
    if (selectedFiles.length >= CONFIG.maxFiles) { errors.push(`Limite de ${CONFIG.maxFiles} arquivos por análise atingido.`); break; }
    selectedFiles.push(file);
  }
  renderFileList();
  if (errors.length) showError(errors.join("\n"));
}

function removeFile(file) {
  selectedFiles = selectedFiles.filter(item => item !== file);
  hideError();
  renderFileList();
}

function clearFiles() {
  selectedFiles = [];
  elements.fileInput.value = "";
  hideError();
  renderFileList();
}

function renderFileList() {
  const total = selectedFiles.length;
  const totalBytes = selectedFiles.reduce((sum, file) => sum + file.size, 0);
  elements.fileListWrap.classList.toggle("hidden", total === 0);
  elements.fileCount.textContent = `${total} ${total === 1 ? "arquivo selecionado" : "arquivos selecionados"} · ${formatBytes(totalBytes)}`;
  elements.fileList.replaceChildren(...selectedFiles.map(buildFileItem));
  elements.processButton.disabled = total === 0;
  elements.processLabel.textContent = total > 1 ? `Processar ${total} arquivos` : "Processar arquivos";
}

function buildFileItem(file) {
  const item = document.createElement("li");
  item.className = "file-preview";

  const type = document.createElement("div");
  type.className = "file-type";
  type.textContent = extensionOf(file.name).toUpperCase() || "ARQ";

  const info = document.createElement("div");
  const name = document.createElement("strong");
  name.textContent = file.name;
  name.title = file.name;
  const size = document.createElement("small");
  size.textContent = formatBytes(file.size);
  info.append(name, size);

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "icon-button";
  remove.textContent = "×";
  remove.setAttribute("aria-label", `Remover ${file.name}`);
  remove.addEventListener("click", event => { event.stopPropagation(); removeFile(file); });

  item.append(type, info, remove);
  return item;
}

/* ---------- upload ---------- */
async function processFiles() {
  if (!selectedFiles.length) return;
  hideError();
  updateProgress(0);
  showView("processing");
  try {
    activeDataset = await uploadDatasets(selectedFiles, updateProgress);
    renderDataset(activeDataset);
    showView("workspace");
    addAssistantMessage({ answer: "Sua base foi processada. Escolha uma sugestão ou faça sua própria pergunta para começar.", type: "text" });
  } catch (error) {
    activeDataset = null;
    showView("upload");
    showError(error.message);
  }
}

function updateProgress(value) {
  elements.progressBar.style.width = `${Math.max(value, 8)}%`;
  const index = Math.min(Math.floor(value / 22), CONFIG.processingMessages.length - 1);
  elements.processingMessage.textContent = CONFIG.processingMessages[index];
}

function renderDataset(dataset) {
  const count = dataset.dataset_ids.length;
  elements.datasetName.textContent = count === 1 ? (dataset.filenames[0] || "1 arquivo") : `${count} arquivos`;
  // dataset_ids e filenames são devolvidos na mesma ordem do envio
  elements.datasetFiles.replaceChildren(...dataset.dataset_ids.map((id, index) => {
    const li = document.createElement("li");
    const badge = document.createElement("span");
    badge.textContent = extensionOf(dataset.filenames[index] || "").toUpperCase() || "ARQ";
    const name = document.createTextNode(dataset.filenames[index] || id);
    const small = document.createElement("small");
    small.textContent = id;
    li.append(badge, name, small);
    return li;
  }));
  renderSuggestions();
}

function renderSuggestions() {
  elements.suggestions.replaceChildren(...suggestionTexts.map(text => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "suggestion-chip";
    button.textContent = text;
    button.addEventListener("click", () => { elements.questionInput.value = text; elements.questionForm.requestSubmit(); });
    return button;
  }));
}

/* ---------- perguntas e respostas ---------- */
async function submitQuestion(event) {
  event.preventDefault();
  const question = elements.questionInput.value.trim();
  if (!question || !activeDataset) return;
  addUserMessage(question);
  elements.questionInput.value = "";
  autoResize();
  setComposerState(false);
  const typing = addTypingIndicator();
  try {
    // Todos os dataset_ids recebidos no upload seguem juntos em /{ds_1,ds_2,...}/query
    const response = await askQuestion(activeDataset.dataset_ids, question);
    typing.remove();
    addAssistantMessage(response);
  } catch (error) {
    typing.remove();
    addAssistantMessage({ answer: `Não consegui concluir a análise: ${error.message}`, type: "text" });
  } finally {
    setComposerState(true);
  }
}

function addUserMessage(text) {
  const article = document.createElement("article");
  article.className = "message user-message";
  const bubble = document.createElement("div");
  bubble.className = "user-bubble";
  bubble.textContent = text;
  article.append(bubble);
  elements.messages.append(article);
  scrollMessages();
}

// Renderiza o OutputSchema: { answer, type, table, chart }
function addAssistantMessage(response) {
  const article = $("#assistantMessageTemplate").content.firstElementChild.cloneNode(true);
  const answerText = article.querySelector(".answer-text");
  const paragraph = document.createElement("p");
  paragraph.textContent = response.answer || "Não recebi uma resposta em texto para esta pergunta.";
  answerText.append(paragraph);

  const visual = article.querySelector(".answer-visual");
  const showTable = response.table && ["table", "mixed", undefined].includes(response.type);
  const showChart = response.chart && ["chart", "mixed", undefined].includes(response.type);
  if (showTable) visual.append(buildTable(response.table));
  if (showChart) visual.append(buildChart(response.chart));
  if (!visual.children.length) visual.remove();

  elements.messages.append(article);
  scrollMessages();
}

function buildTable(data) {
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  const table = document.createElement("table");
  table.className = "result-table";
  const thead = table.createTHead();
  const headerRow = thead.insertRow();
  data.columns.forEach(column => { const th = document.createElement("th"); th.textContent = column; headerRow.append(th); });
  const tbody = table.createTBody();
  data.rows.forEach(row => {
    const tr = tbody.insertRow();
    row.forEach(value => { const td = tr.insertCell(); td.textContent = value ?? ""; });
  });
  wrap.append(table);
  return wrap;
}

function buildChart(data) {
  const wrap = document.createElement("div");
  wrap.className = "chart-wrap";
  if (typeof Chart === "undefined") {
    wrap.textContent = "Não foi possível carregar a biblioteca de gráficos.";
    return wrap;
  }
  const canvas = document.createElement("canvas");
  wrap.append(canvas);
  const isBar = data.type !== "doughnut";
  const datasets = data.datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data,
    // barras: uma cor por série; rosca: uma cor por fatia
    backgroundColor: isBar ? chartPalette[index % chartPalette.length] : data.labels.map((_, i) => chartPalette[i % chartPalette.length]),
    borderWidth: 0,
    borderRadius: isBar ? 7 : 0
  }));
  requestAnimationFrame(() => {
    const chart = new Chart(canvas, {
      type: isBar ? "bar" : "doughnut",
      data: { labels: data.labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: !isBar || datasets.length > 1, position: isBar ? "top" : "bottom" } },
        scales: isBar ? {
          y: { beginAtZero: true, grid: { color: "#edf1ef" }, ticks: { callback: value => formatNumber(value) } },
          x: { grid: { display: false } }
        } : {}
      }
    });
    chartInstances.push(chart);
  });
  return wrap;
}

function addTypingIndicator() {
  const article = document.createElement("article");
  article.className = "message assistant-message";
  article.innerHTML = '<span class="message-avatar">F</span><span class="typing"><i></i><i></i><i></i></span>';
  elements.messages.append(article);
  scrollMessages();
  return article;
}

/* ---------- navegação e utilitários ---------- */
async function resetApp() {
  // Chama GET /api/datasets/sessions/new para o backend descartar a sessão atual.
  // Se a chamada falhar, a tela ainda é reiniciada: o próximo upload cria um novo contexto.
  elements.newAnalysisButton.disabled = true;
  try {
    await startNewSession();
  } catch (error) {
    console.warn("Não foi possível encerrar a sessão no servidor:", error);
  } finally {
    elements.newAnalysisButton.disabled = false;
  }

  chartInstances.splice(0).forEach(chart => chart.destroy());
  activeDataset = null;
  elements.messages.replaceChildren();
  elements.suggestions.replaceChildren();
  elements.datasetFiles.replaceChildren();
  elements.progressBar.style.width = "8%";
  clearFiles();
  showView("upload");
}

function showView(view) {
  elements.uploadView.classList.toggle("hidden", view !== "upload");
  elements.processingView.classList.toggle("hidden", view !== "processing");
  elements.workspaceView.classList.toggle("hidden", view !== "workspace");
}
function showError(message) { elements.uploadError.textContent = message; elements.uploadError.style.whiteSpace = "pre-line"; elements.uploadError.classList.remove("hidden"); }
function hideError() { elements.uploadError.classList.add("hidden"); }
function setComposerState(enabled) { elements.questionInput.disabled = !enabled; elements.sendButton.disabled = !enabled; if (enabled) elements.questionInput.focus(); }
function autoResize() { elements.questionInput.style.height = "auto"; elements.questionInput.style.height = `${elements.questionInput.scrollHeight}px`; }
function scrollMessages() { requestAnimationFrame(() => elements.messages.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "nearest" })); }
function extensionOf(name) { return name.includes(".") ? name.slice(name.lastIndexOf(".") + 1) : ""; }
function formatNumber(value) { return Number(value).toLocaleString("pt-BR"); }
function formatBytes(bytes) { if (!bytes) return "0 B"; const units = ["B", "KB", "MB", "GB"]; const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1); return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`; }
