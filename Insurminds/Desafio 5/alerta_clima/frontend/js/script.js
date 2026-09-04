  const messagesDiv = document.getElementById('messages');
  const cityInput = document.getElementById('cityInput');
  const weatherForm = document.getElementById('weatherForm');

  let isMenuVisible = false;

  // ==========================================================
  // Dicas do Dia (Painel Esquerdo) — obtidas via /api/v1/tips
  // ==========================================================

  // Metadados de exibição de cada tipo de dica (título/ícone).
  // A CHAVE "type" corresponde exatamente à chave homônima retornada
  // pelo endpoint /api/v1/tips (schema "Tips" do swagger).
  const weatherTipsMeta = [
    { type: 'uv', title: '☀️ Proteção Solar' },
    { type: 'rain', title: '🌧️ Prevenção de Chuva' },
    { type: 'wind', title: '💨 Rajadas de Vento' },
    { type: 'temp', title: '🌡️ Variação Térmica' },
    { type: 'humidity', title: '💧 Umidade Relativa' },
    { type: 'cold', title: '❄️ Frio Intenso' },
    { type: 'tempest', title: '⚡ Riscos de Tempestade' },
    { type: 'fog', title: '🚗 Visibilidade e Neblina' },
    { type: 'eye', title: '🕶️ Saúde Ocular' },
    { type: 'flood', title: '🏠 Cuidado com Alagamentos' }
  ];

  const TIPS_QUEUE_STORAGE_KEY = 'weatherApp_tipsQueues';
  const LAST_TIP_STORAGE_KEY = 'weatherApp_lastTipByType';
  const TIPS_DISPLAY_COUNT = 5;

  // Busca as dicas no endpoint /api/v1/tips
  // Formato de resposta: { temp: [...], tempest: [...], rain: [...], wind: [...],
  //                         humidity: [...], uv: [...], eye: [...], fog: [...],
  //                         cold: [...], flood: [...] }
  async function fetchTipsFromApi() {
    const res = await fetch('/api/v1/tips');
    if (!res.ok) {
      throw new Error('Falha ao obter dicas do endpoint.');
    }
    return res.json();
  }

  // Monta, a partir da resposta do endpoint, uma fila embaralhada de dicas
  // para cada um dos tipos conhecidos pelo front-end.
  function buildShuffledTipsQueues(tipsData) {
    const queues = {};
    weatherTipsMeta.forEach(meta => {
      const list = Array.isArray(tipsData[meta.type]) ? tipsData[meta.type] : [];
      queues[meta.type] = shuffleArray(list);
    });
    return queues;
  }

  function loadTipsQueues() {
    try {
      const raw = localStorage.getItem(TIPS_QUEUE_STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (err) {
      return {};
    }
  }

  function saveTipsQueues(queues) {
    try {
      localStorage.setItem(TIPS_QUEUE_STORAGE_KEY, JSON.stringify(queues));
    } catch (err) {
      // Armazenamento indisponível: a rotação de dicas simplesmente não persistirá entre execuções.
    }
  }

  function loadLastTipByType() {
    try {
      const raw = localStorage.getItem(LAST_TIP_STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (err) {
      return {};
    }
  }

  function saveLastTipByType(lastTipByType) {
    try {
      localStorage.setItem(LAST_TIP_STORAGE_KEY, JSON.stringify(lastTipByType));
    } catch (err) {
      // Armazenamento indisponível.
    }
  }

  // Retorna a próxima dica (aleatória, pois a fila já foi embaralhada) para um
  // tipo específico. Quando a fila desse tipo se esgota, o endpoint
  // /api/v1/tips é consultado novamente e as filas de TODOS os tipos são
  // recarregadas com novas dicas.
  async function getNextTipForType(type, queues, lastTipByType) {
    if (!queues[type] || queues[type].length === 0) {
      const freshTipsData = await fetchTipsFromApi();
      const freshQueues = buildShuffledTipsQueues(freshTipsData);
      Object.assign(queues, freshQueues);
    }

    let tip = queues[type].shift();

    // Evita repetir exatamente a mesma dica que já estava sendo exibida para
    // este tipo, garantindo que a dica realmente tenha sido trocada, quando
    // houver alternativa disponível na fila.
    if (tip === lastTipByType[type] && queues[type].length > 0) {
      queues[type].push(tip);
      tip = queues[type].shift();
    }

    return tip;
  }

  function renderTipCards(selectedMeta, tipsMap) {
    const tipsContainer = document.getElementById('tipsContainer');
    tipsContainer.innerHTML = '';

    selectedMeta.forEach(meta => {
      const card = document.createElement('div');
      card.className = `info-card ${meta.type}`;
      card.innerHTML = `
        <h3>${meta.title}</h3>
        <p>${escapeHtml(tipsMap[meta.type] || '')}</p>
      `;
      tipsContainer.appendChild(card);
    });
  }

  // Sorteia 5 tipos de dica dentre os 10 conhecidos e, para cada um, obtém
  // (de forma aleatória) uma dica da lista correspondente retornada pelo
  // endpoint /api/v1/tips.
  async function loadTips() {
    const tipsContainer = document.getElementById('tipsContainer');

    try {
      let queues = loadTipsQueues();

      // Se ainda não há nenhuma dica em cache para nenhum tipo, busca a
      // primeira leva de dicas no endpoint.
      const hasAnyQueue = weatherTipsMeta.some(
        meta => Array.isArray(queues[meta.type]) && queues[meta.type].length > 0
      );
      if (!hasAnyQueue) {
        const tipsData = await fetchTipsFromApi();
        queues = buildShuffledTipsQueues(tipsData);
      }

      const shuffledMeta = shuffleArray(weatherTipsMeta);
      const selectedMeta = shuffledMeta.slice(0, TIPS_DISPLAY_COUNT);

      const lastTipByType = loadLastTipByType();
      const newTipsMap = {};

      for (const meta of selectedMeta) {
        newTipsMap[meta.type] = await getNextTipForType(meta.type, queues, lastTipByType);
      }

      saveTipsQueues(queues);
      saveLastTipByType(Object.assign({}, lastTipByType, newTipsMap));
      renderTipCards(selectedMeta, newTipsMap);
    } catch (err) {
      tipsContainer.innerHTML = '<p style="font-size: 0.8rem; color: #94a3b8;">Não foi possível carregar as dicas. Tente recarregar a página.</p>';
    }
  }

  // ==========================================================
  // Cidades Rápidas (Painel Direito) — obtidas via /api/v1/cities
  // ==========================================================
  // Formato de resposta do endpoint (schema "City" do swagger):
  // [
  //   { "city": "Rio de Janeiro", "badge": "RJ", "type": "brasileira" },
  //   { "city": "Londres",        "badge": "GB", "type": "global" },
  //   ...
  // ]
  // "type" é "brasileira" para cidades do Brasil, ou "global" para cidades internacionais.
  const CITY_QUEUE_BR_KEY = 'weatherApp_cityQueue_brasileira';
  const CITY_QUEUE_GLOBAL_KEY = 'weatherApp_cityQueue_global';
  const CITY_BR_COUNT = 4;
  const CITY_GLOBAL_COUNT = 3;
  const CITY_SHORTCUTS_COUNT = CITY_BR_COUNT + CITY_GLOBAL_COUNT; // 7 cidades no painel
  const MAX_CITY_FETCH_ATTEMPTS = 5; // evita loop infinito caso o endpoint não traga cidades suficientes de algum tipo

  // Embaralha um array (Fisher-Yates), sem alterar o original
  function shuffleArray(array) {
    const result = [...array];
    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }

  // Escapa texto antes de inserir no innerHTML
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Busca a lista de cidades no endpoint /api/v1/cities e já separa o
  // resultado em duas listas, conforme o campo "type" de cada cidade:
  // brasileiras e globais (internacionais).
  async function fetchCitiesFromApi() {
    const res = await fetch('/api/v1/cities');
    if (!res.ok) {
      throw new Error('Falha ao obter cidades do endpoint.');
    }
    const data = await res.json();
    // CORRIGIDO: o endpoint /api/v1/cities retorna diretamente um ARRAY de
    // cidades (List[City]), e não um objeto { cities: [...] }. Além disso,
    // o schema "City" do backend usa a chave "city" (não "cidade").
    const cities = Array.isArray(data) ? data : [];

    const brazilian = [];
    const international = [];

    cities.forEach(entry => {
      const city = { name: entry.city, badge: entry.badge, type: entry.type };
      if ((entry.type || '').toLowerCase() === 'brasileira') {
        brazilian.push(city);
      } else {
        international.push(city);
      }
    });

    return { brazilian, international };
  }

  function loadCityQueues() {
    try {
      const rawBr = localStorage.getItem(CITY_QUEUE_BR_KEY);
      const rawGlobal = localStorage.getItem(CITY_QUEUE_GLOBAL_KEY);
      return {
        brazilian: rawBr ? JSON.parse(rawBr) : [],
        international: rawGlobal ? JSON.parse(rawGlobal) : []
      };
    } catch (err) {
      return { brazilian: [], international: [] };
    }
  }

  function saveCityQueues(queues) {
    try {
      localStorage.setItem(CITY_QUEUE_BR_KEY, JSON.stringify(queues.brazilian));
      localStorage.setItem(CITY_QUEUE_GLOBAL_KEY, JSON.stringify(queues.international));
    } catch (err) {
      // Armazenamento indisponível: a rotação de cidades simplesmente não persistirá entre execuções.
    }
  }

  // Retorna as CITY_BR_COUNT cidades brasileiras + CITY_GLOBAL_COUNT cidades
  // globais a exibir no painel (total de CITY_SHORTCUTS_COUNT = 7), consumindo-as
  // das filas locais embaralhadas — nunca cidades inventadas no front-end.
  //
  // A cada execução da aplicação, os itens já exibidos são removidos das filas,
  // então a próxima execução naturalmente exibe pelo menos uma cidade diferente
  // (desde que ainda restem cidades daquele tipo na fila).
  //
  // Sempre que uma das filas (brasileiras ou globais) não tiver cidades
  // suficientes para completar a próxima exibição, uma NOVA requisição é feita
  // ao endpoint /api/v1/cities para reabastecê-la com mais cidades vindas dele.
  async function getNextCities() {
    let queues = loadCityQueues();

    let attempts = 0;
    while (
      (queues.brazilian.length < CITY_BR_COUNT || queues.international.length < CITY_GLOBAL_COUNT) &&
      attempts < MAX_CITY_FETCH_ATTEMPTS
    ) {
      const fresh = await fetchCitiesFromApi();
      queues.brazilian = shuffleArray(queues.brazilian.concat(fresh.brazilian));
      queues.international = shuffleArray(queues.international.concat(fresh.international));
      attempts++;
    }

    const selectedBr = queues.brazilian.slice(0, CITY_BR_COUNT);
    const selectedGlobal = queues.international.slice(0, CITY_GLOBAL_COUNT);

    queues.brazilian = queues.brazilian.slice(CITY_BR_COUNT);
    queues.international = queues.international.slice(CITY_GLOBAL_COUNT);
    saveCityQueues(queues);

    return shuffleArray(selectedBr.concat(selectedGlobal));
  }

  function renderCityButtons(cities) {
    const container = document.getElementById('cityShortcuts');
    container.innerHTML = '';

    cities.forEach(city => {
      const isBrazilian = (city.type || '').toLowerCase() === 'brasileira';
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `city-btn ${isBrazilian ? 'type-brasileira' : 'type-global'}`;
      btn.innerHTML = `
        <span>📍 ${escapeHtml(city.name)}</span>
        <span class="city-btn-meta">
          <span class="badge">${escapeHtml(city.badge)}</span>
        </span>
      `;
      btn.addEventListener('click', () => quickSelectCity(city.name));
      container.appendChild(btn);
    });
  }

  async function loadCityShortcuts() {
    const container = document.getElementById('cityShortcuts');
    try {
      const cities = await getNextCities();
      if (cities.length === 0) {
        container.innerHTML = '<p style="font-size: 0.8rem; color: #94a3b8;">Nenhuma cidade disponível no momento.</p>';
        return;
      }
      renderCityButtons(cities);
    } catch (err) {
      container.innerHTML = '<p style="font-size: 0.8rem; color: #94a3b8;">Não foi possível carregar as cidades. Tente recarregar a página.</p>';
    }
  }

  window.onload = () => {
    loadTips();
    loadCityShortcuts();
    addBotMessage("Olá! 👋 Bem-vindo ao <b>Alerta de Clima</b>.<br>Por favor, informe o nome da cidade ou escolha uma das opções na barra lateral:");
  };

  weatherForm.addEventListener('submit', function(event) {
    event.preventDefault();
    handleCitySubmit();
  });

  document.addEventListener('keydown', function(event) {
    if (!isMenuVisible) return;

    switch (event.key) {
      case '1':
      case 'Numpad1':
        isMenuVisible = false;
        fetchCurrent();
        break;
      case '2':
      case 'Numpad2':
        isMenuVisible = false;
        fetchForecast();
        break;
      case '3':
      case 'Numpad3':
        isMenuVisible = false;
        changeCity();
        break;
      case '4':
      case 'Numpad4':
        isMenuVisible = false;
        exitApp();
        break;
    }
  });

  function quickSelectCity(cityName) {
    if (weatherForm.style.display === 'none') {
      weatherForm.style.display = 'flex';
    }
    cityInput.value = cityName;
    handleCitySubmit();
  }

  function addBotMessage(text, htmlContent = '') {
    const msg = document.createElement('div');
    msg.className = 'message bot';
    msg.innerHTML = text + (htmlContent ? `<br>${htmlContent}` : '');
    messagesDiv.appendChild(msg);
    scrollToBottom();
    return msg;
  }

  function addUserMessage(text) {
    const msg = document.createElement('div');
    msg.className = 'message user';
    msg.textContent = text;
    messagesDiv.appendChild(msg);
    scrollToBottom();
  }

  function showLoadingMessage(text = "Consultando informações...") {
    const msg = document.createElement('div');
    msg.className = 'message bot';
    msg.innerHTML = `
      <div class="loading-container">
        <span class="hourglass-icon">⌛</span>
        <span>${text}</span>
      </div>
    `;
    messagesDiv.appendChild(msg);
    scrollToBottom();
    return msg;
  }

  function scrollToBottom() {
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  async function handleCitySubmit() {
    const city = cityInput.value.trim();
    if (!city) return;

    addUserMessage(city);
    cityInput.value = '';

    const loadingMsg = showLoadingMessage("Registrando localização...");

    try {
      const response = await fetch('/api/v1/city', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: city
      });

      loadingMsg.remove();

      if (response.ok) {
        addBotMessage(`Cidade <b>${city}</b> selecionada com sucesso! ✨<br>O que você deseja fazer agora?`);
        showMenuOptions();
      } else {
        addBotMessage("Não foi possível registrar a cidade. Por favor, tente novamente.");
      }
    } catch (err) {
      loadingMsg.remove();
      addBotMessage("Erro ao se conectar ao servidor meteorológico.");
    }
  }

  function showMenuOptions() {
    weatherForm.style.display = 'none';
    isMenuVisible = true;

    const menuHtml = `
      <div class="options-container">
        <button class="option-btn" onclick="selectOption(fetchCurrent)">☀️ 1. Previsão atual</button>
        <button class="option-btn" onclick="selectOption(fetchForecast)">📅 2. Previsão dos próximos 7 dias</button>
        <button class="option-btn" onclick="selectOption(changeCity)">🏙️ 3. Trocar cidade</button>
        <button class="option-btn" onclick="selectOption(exitApp)">🚪 4. Sair</button>
      </div>
    `;
    addBotMessage("Escolha uma opção digitando o número (1-4) ou clicando abaixo:", menuHtml);
  }

  function selectOption(action) {
    isMenuVisible = false;
    action();
  }

  async function fetchCurrent() {
    addUserMessage("1. Previsão atual");
    const loadingMsg = showLoadingMessage("Buscando clima atual...");

    try {
      const res = await fetch('/api/v1/current');
      const data = await res.json();
      
      loadingMsg.remove();

      const alertMessage = data.alert && data.alert.message ? data.alert.message : '';

      const content = `
        <div class="weather-card">
          <p>🌡️ <b>Condição:</b> ${data.weather_icon || ''} ${data.description}</p>
          <p>📊 <b>Temp. Máx/Mín:</b> ${data.temp_max} / ${data.temp_min}</p>
          <p>🌧️ <b>Chuva:</b> ${data.precip} (Prob: ${data.precip_prob})</p>
          <p>💨 <b>Vento:</b> ${data.wind_gusts}</p>
          <p>🌅 <b>Sol:</b> Nascer ${data.sunrise} | Pôr ${data.sunset}</p>
          ${alertMessage ? `<div class="weather-alert">🚨 <b>Alerta:</b> ${escapeHtml(alertMessage)}</div>` : ''}
        </div>
      `;
      addBotMessage("Aqui estão as condições meteorológicas atuais:", content);
      showMenuOptions();
    } catch (err) {
      loadingMsg.remove();
      addBotMessage("Erro ao obter a previsão atual.");
      showMenuOptions();
    }
  }

  async function fetchForecast() {
    addUserMessage("2. Previsão dos próximos 7 dias");
    const loadingMsg = showLoadingMessage("Buscando previsão de 7 dias...");

    try {
      const res = await fetch('/api/v1/forecast');
      const dataList = await res.json();
      
      loadingMsg.remove();

      let content = '<div class="weather-card">';
      dataList.forEach(item => {
        const alertMessage = item.alert && item.alert.message ? item.alert.message : '';

        content += `
          <div class="forecast-item">
            <p>🗓️ <b>Data:</b> ${item.date}</p>
            <p>${item.weather_icon || ''} <b>${item.description}</b></p>
            <p>🌡️ Máx: ${item.temp_max} | Mín: ${item.temp_min}</p>
            <p>🌧️ Chuva: ${item.precip} (${item.precip_prob})</p>
            ${alertMessage ? `<div class="weather-alert">🚨 <b>Alerta:</b> ${escapeHtml(alertMessage)}</div>` : ''}
          </div>
        `;
      });
      content += '</div>';

      addBotMessage("Confira a previsão para os próximos 7 dias:", content);
      showMenuOptions();
    } catch (err) {
      loadingMsg.remove();
      addBotMessage("Erro ao obter a previsão de 7 dias.");
      showMenuOptions();
    }
  }

  function changeCity() {
    addUserMessage("3. Trocar cidade");
    weatherForm.style.display = 'flex';
    cityInput.focus();
    addBotMessage("Por favor, digite o nome da nova cidade:");
  }

  function exitApp() {
    messagesDiv.innerHTML = '';
    weatherForm.style.display = 'flex';
    location.reload();
  }
