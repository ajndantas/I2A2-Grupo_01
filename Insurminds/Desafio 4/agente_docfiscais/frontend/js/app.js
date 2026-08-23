import { CONFIG } from "./config.js";
import { uploadDataset, askQuestion } from "./api.js";

const $ = selector => document.querySelector(selector);
const elements = {
  uploadView: $("#uploadView"), processingView: $("#processingView"), workspaceView: $("#workspaceView"),
  dropzone: $("#dropzone"), fileInput: $("#fileInput"), selectFileButton: $("#selectFileButton"),
  filePreview: $("#filePreview"), fileType: $("#fileType"), fileName: $("#fileName"), fileSize: $("#fileSize"),
  removeFileButton: $("#removeFileButton"), processButton: $("#processButton"), uploadError: $("#uploadError"),
  processingMessage: $("#processingMessage"), progressBar: $("#progressBar"), newAnalysisButton: $("#newAnalysisButton"),
  datasetName: $("#datasetName"), invoiceCount: $("#invoiceCount"), itemCount: $("#itemCount"),
  csvCount: $("#csvCount"), datasetPeriod: $("#datasetPeriod"), qualityScore: $("#qualityScore"),
  qualityBar: $("#qualityBar"), qualityMessage: $("#qualityMessage"), detectedFiles: $("#detectedFiles"),
  suggestions: $("#suggestions"), messages: $("#messages"), questionForm: $("#questionForm"),
  questionInput: $("#questionInput"), sendButton: $("#sendButton")
};

let selectedFile = null;
let activeDataset = null;
const chartInstances = [];
const suggestionTexts = ["Quais foram os cinco maiores fornecedores?", "Qual produto teve o maior valor?", "Qual UF concentrou mais compras?", "Quais são os principais CFOPs?"];
const acceptedExtensions = [".csv", ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"];

elements.selectFileButton.addEventListener("click", event => { event.stopPropagation(); elements.fileInput.click(); });
elements.dropzone.addEventListener("click", () => elements.fileInput.click());
elements.dropzone.addEventListener("keydown", event => { if (["Enter", " "].includes(event.key)) elements.fileInput.click(); });
elements.fileInput.addEventListener("change", () => setFile(elements.fileInput.files[0]));
elements.removeFileButton.addEventListener("click", clearFile);
elements.processButton.addEventListener("click", processFile);
elements.newAnalysisButton.addEventListener("click", resetApp);
elements.questionForm.addEventListener("submit", submitQuestion);
elements.questionInput.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); elements.questionForm.requestSubmit(); }
});
elements.questionInput.addEventListener("input", autoResize);

for (const eventName of ["dragenter", "dragover"]) elements.dropzone.addEventListener(eventName, event => { event.preventDefault(); elements.dropzone.classList.add("dragover"); });
for (const eventName of ["dragleave", "drop"]) elements.dropzone.addEventListener(eventName, event => { event.preventDefault(); elements.dropzone.classList.remove("dragover"); });
elements.dropzone.addEventListener("drop", event => setFile(event.dataTransfer.files[0]));

function setFile(file) {
  hideError();
  if (!file) return;
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  if (!acceptedExtensions.includes(extension)) return showError("Selecione um arquivo CSV, PDF ou imagem.");
  if (file.size > CONFIG.maxFileSize) return showError("O arquivo ultrapassa o limite recomendado de 500 MB.");
  selectedFile = file;
  elements.fileType.textContent = extension.slice(1).toUpperCase();
  elements.fileName.textContent = file.name;
  elements.fileSize.textContent = formatBytes(file.size);
  elements.filePreview.classList.remove("hidden");
  elements.processButton.disabled = false;
}

function clearFile(event) {
  event?.stopPropagation();
  selectedFile = null;
  elements.fileInput.value = "";
  elements.filePreview.classList.add("hidden");
  elements.processButton.disabled = true;
  hideError();
}

async function processFile() {
  if (!selectedFile) return;
  showView("processing");
  try {
    activeDataset = await uploadDataset(selectedFile, updateProgress);
    renderDataset(activeDataset);
    showView("workspace");
    addAssistantMessage({ answer: "Sua base foi processada. Escolha uma sugestão ou faça sua própria pergunta para começar.", type: "text" });
  } catch (error) {
    showView("upload");
    showError(error.message);
  }
}

function updateProgress(value) {
  elements.progressBar.style.width = `${value}%`;
  const index = Math.min(Math.floor(value / 22), CONFIG.processingMessages.length - 1);
  elements.processingMessage.textContent = CONFIG.processingMessages[index];
}

function renderDataset(dataset) {
  const summary = dataset.summary;
  elements.datasetName.textContent = dataset.name;
  /*elements.invoiceCount.textContent = formatNumber(summary.invoices);
  elements.itemCount.textContent = formatNumber(summary.items);
  elements.csvCount.textContent = summary.files;
  elements.datasetPeriod.textContent = summary.period;
  elements.qualityScore.textContent = `${summary.quality_score}%`;
  elements.qualityBar.style.width = `${summary.quality_score}%`;
  elements.qualityMessage.textContent = summary.quality_message;
  elements.detectedFiles.replaceChildren(...summary.detected_files.map(name => Object.assign(document.createElement("li"), { textContent: name })));*/
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
    const response = await askQuestion(activeDataset.dataset_id, question);
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

function addAssistantMessage(response) {
  const article = $("#assistantMessageTemplate").content.firstElementChild.cloneNode(true);
  const answerText = article.querySelector(".answer-text");
  const paragraph = document.createElement("p");
  paragraph.textContent = response.answer;
  answerText.append(paragraph);
  const visual = article.querySelector(".answer-visual");
  if (response.table) visual.append(buildTable(response.table));
  if (response.chart) visual.append(buildChart(response.chart));
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
  data.rows.forEach(row => { const tr = tbody.insertRow(); row.forEach(value => { const td = tr.insertCell(); td.textContent = value; }); });
  wrap.append(table);
  return wrap;
}

function buildChart(data) {
  const wrap = document.createElement("div");
  wrap.className = "chart-wrap";
  const canvas = document.createElement("canvas");
  wrap.append(canvas);
  requestAnimationFrame(() => {
    const chart = new Chart(canvas, {
      type: data.type,
      data: { labels: data.labels, datasets: data.datasets.map(dataset => ({ ...dataset, backgroundColor: data.type === "bar" ? "#0b6b64" : ["#0b6b64", "#35a08f", "#db9b41", "#7e918e", "#c8d5d2"], borderWidth: 0, borderRadius: data.type === "bar" ? 7 : 0 })) },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: data.type !== "bar" } }, scales: data.type === "bar" ? { y: { beginAtZero: true, grid: { color: "#edf1ef" } }, x: { grid: { display: false } } } : {} }
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

function resetApp() {
  chartInstances.splice(0).forEach(chart => chart.destroy());
  activeDataset = null;
  elements.messages.replaceChildren();
  elements.suggestions.replaceChildren();
  elements.progressBar.style.width = "8%";
  clearFile();
  showView("upload");
}

function showView(view) {
  elements.uploadView.classList.toggle("hidden", view !== "upload");
  elements.processingView.classList.toggle("hidden", view !== "processing");
  elements.workspaceView.classList.toggle("hidden", view !== "workspace");
}
function showError(message) { elements.uploadError.textContent = message; elements.uploadError.classList.remove("hidden"); }
function hideError() { elements.uploadError.classList.add("hidden"); }
function setComposerState(enabled) { elements.questionInput.disabled = !enabled; elements.sendButton.disabled = !enabled; if (enabled) elements.questionInput.focus(); }
function autoResize() { elements.questionInput.style.height = "auto"; elements.questionInput.style.height = `${elements.questionInput.scrollHeight}px`; }
function scrollMessages() { requestAnimationFrame(() => elements.messages.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "nearest" })); }
function formatNumber(value) { return Number(value).toLocaleString("pt-BR"); }
function formatBytes(bytes) { if (!bytes) return "0 B"; const units = ["B", "KB", "MB", "GB"]; const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1); return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`; }
