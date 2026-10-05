import { CONFIG } from "./config.js";
import { uploadDatasets, askQuestion, validatePolicyFiles } from "./api.js";

const $ = selector => document.querySelector(selector);
const elements = {
  uploadView: $("#uploadView"), processingView: $("#processingView"), workspaceView: $("#workspaceView"),
  dropzone: $("#dropzone"), fileInput: $("#fileInput"), selectFileButton: $("#selectFileButton"),
  filePreview: $("#filePreview"), fileCount: $("#fileCount"), selectedFilesList: $("#selectedFilesList"), fileRequirement: $("#fileRequirement"),
  removeFileButton: $("#removeFileButton"), processButton: $("#processButton"), uploadError: $("#uploadError"),
  processingMessage: $("#processingMessage"), progressBar: $("#progressBar"), newAnalysisButton: $("#newAnalysisButton"),
  datasetName: $("#datasetName"), activeDatasets: $("#activeDatasets"),
  suggestions: $("#suggestions"), messages: $("#messages"), questionForm: $("#questionForm"),
  questionInput: $("#questionInput"), sendButton: $("#sendButton")
};

let selectedFiles = [];
let activeDataset = null;
const chartInstances = [];
const suggestionTexts = ["Quais são as coberturas de cada apólice?", "Qual é a vigência de cada apólice?", "Quantas exclusões cada uma lista, por categoria (ambiental, tributária, multas, geográfica)? Monte um gráfico", "Quais são as principais diferenças entre elas?"];
const acceptedExtensions = [".csv", ".txt", ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"];

elements.selectFileButton.addEventListener("click", event => { event.stopPropagation(); elements.fileInput.click(); });
elements.dropzone.addEventListener("click", event => {
  if (event.target.closest("button")) return;
  elements.fileInput.click();
});
elements.dropzone.addEventListener("keydown", event => {
  if (event.target !== elements.dropzone) return; // evita abrir o seletor duas vezes quando o foco está no botão
  if (["Enter", " "].includes(event.key)) { event.preventDefault(); elements.fileInput.click(); }
});
elements.fileInput.addEventListener("change", () => {
  addFiles([...elements.fileInput.files]);
  elements.fileInput.value = ""; // permite selecionar de novo o mesmo arquivo após removê-lo
});
elements.removeFileButton.addEventListener("click", clearFile);
elements.processButton.addEventListener("click", processFiles);
// "Nova análise" limpa a sessão no backend antes de voltar à tela inicial.
elements.newAnalysisButton.addEventListener("click", startNewAnalysis);
elements.questionForm.addEventListener("submit", submitQuestion);
elements.questionInput.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); elements.questionForm.requestSubmit(); }
});
elements.questionInput.addEventListener("input", autoResize);

// Evita que o navegador abra/baixe o arquivo quando ele é solto fora da área de upload.
for (const eventName of ["dragover", "drop"]) {
  window.addEventListener(eventName, event => {
    if (!event.dataTransfer || ![...event.dataTransfer.types].includes("Files")) return;
    event.preventDefault();
    if (!elements.dropzone.contains(event.target)) event.dataTransfer.dropEffect = "none";
  });
}

let dragDepth = 0; // contador para o dragenter/dragleave não "piscar" ao passar por elementos filhos
elements.dropzone.addEventListener("dragenter", event => {
  event.preventDefault();
  dragDepth++;
  elements.dropzone.classList.add("dragover");
});
elements.dropzone.addEventListener("dragover", event => {
  event.preventDefault();
  if (event.dataTransfer) event.dataTransfer.dropEffect = "copy";
  elements.dropzone.classList.add("dragover");
});
elements.dropzone.addEventListener("dragleave", event => {
  event.preventDefault();
  dragDepth = Math.max(0, dragDepth - 1);
  if (!dragDepth) elements.dropzone.classList.remove("dragover");
});
elements.dropzone.addEventListener("drop", event => {
  event.preventDefault();
  dragDepth = 0;
  elements.dropzone.classList.remove("dragover");
  addFiles([...(event.dataTransfer?.files || [])]);
});

function addFiles(files) {
  hideError();
  if (!files.length) return;

  const errors = [];
  const validFiles = [];
  for (const file of files) {
    const extension = getExtension(file.name);
    if (!acceptedExtensions.includes(extension)) {
      errors.push(`"${file.name}" não é um tipo de arquivo aceito.`);
      continue;
    }
    if (file.size > CONFIG.maxFileSize) {
      errors.push(`"${file.name}" ultrapassa o limite recomendado de 500 MB.`);
      continue;
    }
    if (selectedFiles.some(existing => isSameFile(existing, file)) || validFiles.some(existing => isSameFile(existing, file))) {
      errors.push(`"${file.name}" já foi selecionado. Envie apólices diferentes.`);
      continue;
    }
    validFiles.push(file);
  }

  selectedFiles.push(...validFiles);
  renderSelectedFiles();
  if (errors.length) showError(errors.join(" "));
}

function getExtension(fileName) {
  const dot = fileName.lastIndexOf(".");
  return dot < 0 ? "" : fileName.slice(dot).toLowerCase();
}

function isSameFile(a, b) {
  return a.name === b.name && a.size === b.size && a.lastModified === b.lastModified;
}

function removeFile(index) {
  selectedFiles.splice(index, 1);
  hideError();
  renderSelectedFiles();
}

function renderSelectedFiles() {
  elements.selectedFilesList.replaceChildren();

  if (!selectedFiles.length) {
    elements.filePreview.classList.add("hidden");
    elements.processButton.disabled = true;
    elements.fileInput.value = "";
    return;
  }

  elements.fileCount.textContent = `${selectedFiles.length} arquivo${selectedFiles.length === 1 ? "" : "s"} (mínimo ${CONFIG.minFiles})`;
  const requirementMessage = validatePolicyFiles(selectedFiles);
  elements.fileRequirement.textContent = requirementMessage || `✓ ${selectedFiles.length} apólices selecionadas. Tudo pronto para analisar.`;
  elements.fileRequirement.classList.toggle("is-valid", !requirementMessage);
  selectedFiles.forEach((file, index) => {
    const extension = getExtension(file.name) || ".?";
    const item = document.createElement("div");
    item.className = "selected-file";

    const type = document.createElement("span");
    type.className = "file-type";
    type.textContent = extension.slice(1).toUpperCase();

    const info = document.createElement("div");
    const name = document.createElement("strong");
    name.textContent = file.name;
    const size = document.createElement("small");
    size.textContent = formatBytes(file.size);
    info.append(name, size);

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "icon-button";
    remove.setAttribute("aria-label", `Remover ${file.name}`);
    remove.textContent = "×";
    remove.addEventListener("click", event => {
      event.stopPropagation();
      removeFile(index);
    });

    item.append(type, info, remove);
    elements.selectedFilesList.append(item);
  });

  elements.filePreview.classList.remove("hidden");
  elements.processButton.disabled = Boolean(requirementMessage);
}

function clearFile(event) {
  event?.stopPropagation();
  selectedFiles = [];
  elements.fileInput.value = "";
  elements.filePreview.classList.add("hidden");
  elements.selectedFilesList.replaceChildren();
  elements.processButton.disabled = true;
  hideError();
}

async function processFiles() {
  const validationError = validatePolicyFiles(selectedFiles);
  if (validationError) {
    showError(validationError);
    return;
  }

  showView("processing");
  try {
    activeDataset = await uploadDatasets(selectedFiles, updateProgress);

    // Garante a associação arquivo -> dataset_id pela ordem retornada pelo backend.
    activeDataset.files = selectedFiles.map((file, index) => ({
      name: file.name,
      size: file.size,
      dataset_id: activeDataset.dataset_ids[index]
    }));

    renderDataset(activeDataset);
    showView("workspace");
    addAssistantMessage({
      answer: `${activeDataset.dataset_ids.length} dataset${activeDataset.dataset_ids.length === 1 ? "" : "s"} associado${activeDataset.dataset_ids.length === 1 ? "" : "s"} aos arquivos enviados. Faça uma pergunta para começar.`,
      type: "text"
    });
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
  const files = dataset.files || [];
  elements.datasetName.textContent = files.length === 1
    ? files[0].name
    : `${files.length} arquivos`;

  elements.activeDatasets.replaceChildren(
    ...files.map(file => {
      const li = document.createElement("li");
      const name = document.createElement("strong");
      name.textContent = file.name;
      const id = document.createElement("small");
      id.textContent = file.dataset_id;
      li.append(name, id);
      return li;
    })
  );

  renderSuggestions();
}

function renderSuggestions() {
  elements.suggestions.replaceChildren(...suggestionTexts.map(text => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "suggestion-chip";
    button.textContent = text;
    button.addEventListener("click", () => {
      elements.questionInput.value = text;
      elements.questionForm.requestSubmit();
    });
    return button;
  }));
}

async function submitQuestion(event) {
  event.preventDefault();
  const question = elements.questionInput.value.trim();
  if (!question || !activeDataset?.dataset_ids?.length) return;

  addUserMessage(question);
  elements.questionInput.value = "";
  autoResize();
  setComposerState(false);
  const typing = addTypingIndicator();

  try {
    // Todos os dataset_ids associados aos uploads são enviados na mesma consulta.
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
    Chart.defaults.font.family = "Figtree, system-ui, sans-serif";
    Chart.defaults.color = "#5d6779";
    const chart = new Chart(canvas, {
      type: data.type,
      data: { labels: data.labels, datasets: data.datasets.map(dataset => ({ ...dataset, backgroundColor: data.type === "bar" ? "#1a2e57" : ["#1a2e57", "#b88a3e", "#4f6aa3", "#d6b36a", "#a9b4cc"], borderWidth: 0, borderRadius: data.type === "bar" ? 7 : 0 })) },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: data.type !== "bar" } }, scales: data.type === "bar" ? { y: { beginAtZero: true, grid: { color: "#f0ebde" } }, x: { grid: { display: false } } } : {} }
    });
    chartInstances.push(chart);
  });
  return wrap;
}

function addTypingIndicator() {
  const article = document.createElement("article");
  article.className = "message assistant-message";
  article.innerHTML = '<span class="message-avatar">C</span><span class="typing"><i></i><i></i><i></i></span>';
  elements.messages.append(article);
  scrollMessages();
  return article;
}

function startNewAnalysis() {
  // O backend limpa a sessão em /sessions/new e redireciona (303) para a tela inicial.
  window.location.assign(`${CONFIG.apiBaseUrl}/api/datasets/sessions/new`);
}

/*async function startNewAnalysis() {
  try {
    const response = await fetch(`${CONFIG.apiBaseUrl}/api/datasets/sessions/new`, { method: "POST" });
    if (!response.ok) throw new Error("Não foi possível limpar a sessão atual.");
    window.location.assign(`${CONFIG.apiBaseUrl}/`);
  } catch (error) {
    addAssistantMessage({ answer: `Não foi possível iniciar uma nova análise: ${error.message}`, type: "text" });
  }
}*/

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
function formatBytes(bytes) { if (!bytes) return "0 B"; const units = ["B", "KB", "MB", "GB"]; const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1); return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`; }
