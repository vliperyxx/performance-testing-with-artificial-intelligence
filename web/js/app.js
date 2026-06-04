const sessionState = {
  targetType: null,
  targetName: null,
  testType: null,
  loadSetup: null,
  model: null,
  tools: [],
  customParams: null,
  paramsGenerationModel: null,
  paramsReason: "",
  isEditing: false,
  lastTestTempFolder: null,
  lastResultFolder: null,
  lastAnalysis: null,
  analystProvider: null
};

const STEPS = {
  "screen-choose-target": 1,
  "screen-choose-endpoint": 2,
  "screen-choose-flow": 2,
  "screen-choose-test-type": 3,
  "screen-choose-load-setup": 4,
  "screen-manual-params": 4,
  "screen-choose-params-model": 4,
  "screen-generating-params": 4,
  "screen-show-params": 4,
  "screen-choose-model": 5,
  "screen-choose-tools": 6
};

const TOTAL_STEPS = 6;

let CONFIG = null;
let selectedSavedScript = null;
let selectedSavedResult = null;

function injectStepper() {
  Object.keys(STEPS).forEach(screenId => {
    const screen = document.getElementById(screenId);
    if (!screen)
      return;
    const content = screen.querySelector(".screen-content");
    if (!content)
      return;

    const stepper = document.createElement("div");
    stepper.className = "stepper";

    for (let i = 1; i <= TOTAL_STEPS; i++) {
      if (i > 1) {
        const line = document.createElement("div");
        line.className = "stepper-line";
        line.dataset.lineFor = i - 1;
        stepper.appendChild(line);
      }
      const circle = document.createElement("div");
      circle.className = "stepper-circle";
      circle.dataset.step = i;
      circle.textContent = i;
      stepper.appendChild(circle);
    }

    content.insertBefore(stepper, content.firstChild);
  });
}

function updateStepper(screenId) {
  const currentStep = STEPS[screenId];
  if (!currentStep)
    return;

  const stepper = document.getElementById(screenId).querySelector(".stepper");
  if (!stepper)
    return;

  stepper.querySelectorAll(".stepper-circle").forEach(circle => {
    const step = parseInt(circle.dataset.step);
    circle.classList.remove("completed", "active", "pending");
    if (step < currentStep) {
      circle.classList.add("completed");
      circle.innerHTML = "&#10003;";
    }
    else if (step === currentStep) {
      circle.classList.add("active");
      circle.textContent = step;
    }
    else {
      circle.classList.add("pending");
      circle.textContent = step;
    }
  });

  stepper.querySelectorAll(".stepper-line").forEach(line => {
    const lineFor = parseInt(line.dataset.lineFor);
    line.classList.toggle("filled", lineFor < currentStep);
  });
}

function formatDuration(value) {
  const match = String(value).match(/^(\d+)(s|m|h)$/);
  if (!match)
    return value;
  const number = match[1];
  const unit = match[2];
  if (unit === "s")
    return `${number} с.`;
  if (unit === "m")
    return `${number} хв.`;
  if (unit === "h")
    return `${number} год.`;
  return value;
}

function findLabel(list, key) {
  const found = list.find(item => item.key === key);
  if (found) {
    return found.label;
  }
  return key;
}

function showScreen(screenId) {
  const current = document.querySelector(".screen.active");
  const target = document.getElementById(screenId);

  if (!target || current === target)
    return;

  if (current) {
    current.classList.remove("active");
    current.classList.add("exiting-left");

    const onEnd = () => {
      current.removeEventListener("transitionend", onEnd);
      current.style.transition = "none";
      current.classList.remove("exiting-left");
      void current.offsetWidth;
      current.style.transition = "";
    };
    current.addEventListener("transitionend", onEnd);
  }

  target.classList.add("active");

  if (screenId === "screen-choose-tools")
    restoreSelectedTools();
  if (screenId === "screen-choose-load-setup")
    refreshDefaultParamsLabel();
  if (STEPS[screenId])
    updateStepper(screenId);
}

function showErrorPopup(message) {
  const popup = document.getElementById("error-popup");
  const popupText = document.getElementById("error-popup-text");

  popupText.textContent = message;
  popup.classList.remove("hidden");
}

function hideErrorPopup() {
  const popup = document.getElementById("error-popup");
  popup.classList.add("hidden");
}

async function initApp() {
  try {
    CONFIG = await fetchConfig();
    renderEndpointList();
    renderScenarioList();
    renderTestTypeList();
    renderLoadSetupList();
    renderParamsModelList();
    renderModelList();
    renderToolList();
    renderAnalystModelList();
    injectStepper();
  }
  catch (error) {
    showErrorPopup("Не вдалося завантажити конфігурацію з сервера. Переконайтесь, що Flask запущено");
    console.error(error);
  }
}

function renderEndpointList() {
  const container = document.getElementById("endpoint-list");
  container.innerHTML = "";
  CONFIG.endpoints.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn";
    button.textContent = item.label;
    button.onclick = () => {
      sessionState.targetType = "endpoint";
      sessionState.targetName = item.key;
      showScreen("screen-choose-test-type");
    };
    container.appendChild(button);
  });
}

function renderScenarioList() {
  const container = document.getElementById("scenario-list");
  container.innerHTML = "";
  CONFIG.scenarios.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn";
    button.style.width = "580px";
    button.textContent = item.label;
    button.onclick = () => {
      sessionState.targetType = "flow";
      sessionState.targetName = item.key;
      showScreen("screen-choose-test-type");
    };
    container.appendChild(button);
  });
}

function renderTestTypeList() {
  const container = document.getElementById("test-type-list");
  container.innerHTML = "";
  CONFIG.test_types.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn";
    button.textContent = item.label;
    button.onclick = () => {
      sessionState.testType = item.key;
      updateDefaultParamsLabel(item);
      nextOrConfirm("screen-choose-load-setup");
    };
    container.appendChild(button);
  });
}

function updateDefaultParamsLabel(testType) {
  const label = document.getElementById("default-params-label");
  if (!label)
    return;
  label.textContent = `Використати стандартні параметри ` + `(${testType.virtual_users} користувачів, ` + `${formatDuration(testType.duration)} тривалість, ` + `${formatDuration(testType.ramp_up)} розгін)`;
}

function renderLoadSetupList() {
  const container = document.getElementById("load-setup-list");
  container.innerHTML = "";
  CONFIG.load_setup_options.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn";
    button.style.width = "520px";

    if (item.key === "default") {
      button.style.height = "auto";
      button.style.minHeight = "93px";
      button.style.padding = "16px 32px";
      button.style.whiteSpace = "normal";
      const span = document.createElement("span");
      span.id = "default-params-label";
      span.textContent = item.label;
      button.appendChild(span);
    }
    else {
      button.textContent = item.label;
    }

    button.onclick = () => {
      sessionState.loadSetup = item.key;
      if (item.key === "manual") {
        showScreen("screen-manual-params");
      }
      else if (item.key === "ai") {
        showScreen("screen-choose-params-model");
      }
      else {
        sessionState.customParams = null;
        nextOrConfirm("screen-choose-model");
      }
    };
    container.appendChild(button);
  });
}

function renderParamsModelList() {
  const container = document.getElementById("params-model-list");
  container.innerHTML = "";
  CONFIG.models.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn";
    button.textContent = item.label;
    button.onclick = () => generateParams(item.key);
    container.appendChild(button);
  });
}

function saveManualParams() {
  const vu = document.getElementById("manual-vu").value.trim();
  const duration = document.getElementById("manual-duration").value.trim();
  const rampUp = document.getElementById("manual-ramp-up").value.trim();

  if (!vu || !duration || !rampUp) {
    showErrorPopup("Будь ласка, заповніть всі поля.");
    return;
  }

  const virtualUsers = parseInt(vu);
  if (isNaN(virtualUsers) || virtualUsers <= 0) {
    showErrorPopup("Кількість користувачів має бути додатнім цілим числом.");
    return;
  }

  sessionState.customParams = {virtual_users: virtualUsers, duration: duration, ramp_up: rampUp};
  nextOrConfirm("screen-choose-model");
}

async function generateParams(modelKey) {
  sessionState.paramsGenerationModel = modelKey;
  showScreen("screen-generating-params");

  try {
    const result = await fetchGeneratedParams({test_type: sessionState.testType, target_type: sessionState.targetType, target_name: sessionState.targetName, model: modelKey});

    sessionState.customParams = {virtual_users: result.params.virtual_users, duration: result.params.duration, ramp_up: result.params.ramp_up};
    sessionState.paramsReason = result.params.reason || "";

    displayGeneratedParams();
    showScreen("screen-show-params");
  }
  catch (error) {
    showErrorPopup("Помилка генерації параметрів: " + error.message);
    showScreen("screen-choose-params-model");
    console.error(error);
  }
}

function regenerateParams() {
  generateParams(sessionState.paramsGenerationModel);
}

function displayGeneratedParams() {
  const testTypeLabel = findLabel(CONFIG.test_types, sessionState.testType);
  const modelLabel = findLabel(CONFIG.models, sessionState.paramsGenerationModel);
  let targetWord;
  if (sessionState.targetType === "endpoint") {
    targetWord = "ендпоінту";
  }
  else {
    targetWord = "сценарію";
  }

  document.getElementById("params-label").innerHTML = `Параметри навантаження для ${testTypeLabel.toLowerCase()}<br>` + `${targetWord} ${sessionState.targetName}<br>` + `згенеровані моделлю ${modelLabel}`;

  const params = sessionState.customParams;
  const lines = [`Кількість віртуальних користувачів: ${params.virtual_users}`, `Тривалість: ${params.duration}`, `Час нарощування: ${params.ramp_up}`];
  if (sessionState.paramsReason) {
    lines.push("");
    lines.push(`Обґрунтування: ${sessionState.paramsReason}`);
  }
  document.getElementById("params-content").textContent = lines.join("\n");
}

function renderModelList() {
  const container = document.getElementById("model-list");
  container.innerHTML = "";
  CONFIG.models.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn";
    button.textContent = item.label;
    button.onclick = () => {
      sessionState.model = item.key;
      nextOrConfirm("screen-choose-tools");
    };
    container.appendChild(button);
  });
}

function renderToolList() {
  const container = document.getElementById("tool-list");
  container.innerHTML = "";
  CONFIG.tools.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn tool-btn";
    button.dataset.tool = item.key;
    button.textContent = item.label;
    button.onclick = () => toggleTool(button);
    container.appendChild(button);
  });
}

function toggleTool(button) {
  button.classList.toggle("selected");
}

function confirmTools() {
  const selected = document.querySelectorAll(".tool-btn.selected");
  sessionState.tools = Array.from(selected).map(button => button.dataset.tool);

  if (sessionState.tools.length === 0) {
    showErrorPopup("Будь ласка, оберіть хоча б один інструмент.");
    return;
  }

  sessionState.isEditing = false;
  updateConfigSummary();
  showScreen("screen-confirm-config");
}

function getTargetLabel() {
  if (sessionState.targetType === "endpoint") {
    return findLabel(CONFIG.endpoints, sessionState.targetName);
  }
  if (sessionState.targetType === "flow") {
    return findLabel(CONFIG.scenarios, sessionState.targetName);
  }
  return "Ціль тестування не обрано";
}

function updateConfigSummary() {
  const targetTypeLabel = findLabel(CONFIG.target_types, sessionState.targetType);
  const loadSetupLabel = findLabel(CONFIG.load_setup_options, sessionState.loadSetup);
  const params = getCurrentTestParams();

  const lines = [
    `Об'єкт: ${getTargetLabel()}`,
    `Тип об'єкта: ${targetTypeLabel}`,
    "",
    `Тестування: ${findLabel(CONFIG.test_types, sessionState.testType)}`,
    `Параметри: ${loadSetupLabel}`,
    `   - Користувачів: ${params.virtual_users}`,
    `   - Тривалість: ${formatDuration(params.duration)}`,
    `   - Розгін: ${formatDuration(params.ramp_up)}`,
    "",
    `Модель ШІ: ${findLabel(CONFIG.models, sessionState.model)}`,
    `Інструменти: ${sessionState.tools.map(t => findLabel(CONFIG.tools, t)).join(", ")}`
  ];

  document.getElementById("config-summary").textContent = lines.join("\n");
}

function startEditing() {
  sessionState.isEditing = true;
  showScreen("screen-change-settings");
}

function nextOrConfirm(nextScreen) {
  if (sessionState.isEditing) {
    sessionState.isEditing = false;
    updateConfigSummary();
    showScreen("screen-confirm-config");
  }
  else {
    showScreen(nextScreen);
  }
}

function acceptGeneratedParams() {
  nextOrConfirm("screen-choose-model");
}

function restoreSelectedTools() {
  document.querySelectorAll(".tool-btn").forEach(button => {
    button.classList.toggle("selected", sessionState.tools.includes(button.dataset.tool));
  });
}

function refreshDefaultParamsLabel() {
  if (!sessionState.testType)
    return;
  const testTypeInfo = CONFIG.test_types.find(type => type.key === sessionState.testType);
  if (testTypeInfo)
    updateDefaultParamsLabel(testTypeInfo);
}

async function startGeneration() {
  showScreen("screen-generating");

  try {
    const result = await generateScript({target_type: sessionState.targetType, target_name: sessionState.targetName, test_type: sessionState.testType, load_setup: sessionState.loadSetup, model: sessionState.model, tools: sessionState.tools, custom_params: sessionState.customParams});

    sessionState.generatedScripts = result.scripts;
    sessionState.currentScriptIndex = 0;
    showCurrentScript();
  }
  catch (error) {
    showErrorPopup("Помилка генерації: " + error.message);
    showScreen("screen-confirm-config");
    console.error(error);
  }
}

function showCurrentScript() {
  const scripts = sessionState.generatedScripts;
  const index = sessionState.currentScriptIndex;

  if (index >= scripts.length) {
    showScreen("screen-main-menu");
    return;
  }

  const script = scripts[index];
  const toolLabel = findLabel(CONFIG.tools, script.tool);
  const modelLabel = findLabel(CONFIG.models, script.model);

  document.getElementById("script-label").innerHTML = `Згенерований скрипт для<br>інструмента ${toolLabel} за допомогою моделі ${modelLabel}:`;
  document.getElementById("script-content").textContent = script.code;

  showScreen("screen-show-script");
}

function getCurrentTestParams() {
  if (sessionState.customParams) {
    return sessionState.customParams;
  }
  const testTypeInfo = CONFIG.test_types.find(type => type.key === sessionState.testType);
  return {virtual_users: testTypeInfo.virtual_users, duration: testTypeInfo.duration, ramp_up: testTypeInfo.ramp_up};
}

async function saveCurrentScript() {
  const script = sessionState.generatedScripts[sessionState.currentScriptIndex];

  try {
    const result = await saveScript({code: script.code, tool: script.tool, provider: script.model, target_type: sessionState.targetType, target_name: sessionState.targetName, test_type: sessionState.testType, test_params: getCurrentTestParams()});
    script.savedPath = result.script_path;

    showScreen("screen-script-saved");
  }
  catch (error) {
    showErrorPopup("Помилка збереження: " + error.message);
    console.error(error);
  }
}

async function startTestRun() {
  const script = sessionState.generatedScripts[sessionState.currentScriptIndex];

  const label = document.getElementById("running-target-name");
  if (label)
    label.textContent = sessionState.targetName;
  showScreen("screen-test-running");

  try {
    const result = await runTest({script_path: script.savedPath, tool: script.tool, provider: script.model, target_type: sessionState.targetType, target_name: sessionState.targetName, test_type: sessionState.testType, test_params: getCurrentTestParams()});
    sessionState.lastTestTempFolder = result.temp_folder;

    displayMetrics(result.metrics);
    updateTestCompletedTitle();
    showScreen("screen-test-completed");
  }
  catch (error) {
    showErrorPopup("Помилка запуску тесту: " + error.message);
    showScreen("screen-main-menu");
    console.error(error);
  }
}

function updateTestCompletedTitle() {
  document.getElementById("test-completed-title").textContent = `Виконання тестового сценарію ${sessionState.targetName} завершено`;
}

function displayMetrics(metrics) {
  const element = document.getElementById("metrics-summary");
  if (!element)
    return;

  if (!metrics || !metrics.aggregated) {
    element.textContent = "Метрики недоступні";
    return;
  }

  const aggregatedMetrics = metrics.aggregated;
  const responseTime = aggregatedMetrics.response_time || {};

  const lines = [
    `Всього запитів: ${aggregatedMetrics.total_requests}`,
    `Невдалих: ${aggregatedMetrics.failed_requests} (${aggregatedMetrics.error_rate_percent}%)`,
    `Пропускна здатність: ${aggregatedMetrics.throughput_rps} зап/с`,
    "",
    "Час відгуку (мс):",
    `   - Середній: ${responseTime.avg_ms}`,
    `   - Мінімальний: ${responseTime.min_ms}`,
    `   - Максимальний: ${responseTime.max_ms}`,
    `   - Медіана: ${responseTime.median_ms}`,
    `   - p90 (90-й перцентиль): ${responseTime.p90_ms}`,
    `   - p95 (95-й перцентиль): ${responseTime.p95_ms}`,
    `   - p99 (99-й перцентиль): ${responseTime.p99_ms}`,
  ];

  element.textContent = lines.join("\n");
}

async function saveTestResults() {
  const script = sessionState.generatedScripts[sessionState.currentScriptIndex];
  try {
    const result = await saveResults({temp_folder: sessionState.lastTestTempFolder, tool: script.tool, provider: script.model, target_type: sessionState.targetType, target_name: sessionState.targetName, test_type: sessionState.testType, test_params: getCurrentTestParams()});
    sessionState.lastResultFolder = result.result_folder;
    showScreen("screen-results-saved");
  }
  catch (error) {
    showErrorPopup("Помилка збереження: " + error.message);
    console.error(error);
  }
}

async function discardTestResults() {
  try {
    await deleteResults({ temp_folder: sessionState.lastTestTempFolder });
    showScreen("screen-results-not-saved");
  }
  catch (error) {
    showErrorPopup("Помилка видалення: " + error.message);
    console.error(error);
  }
}

function renderAnalystModelList() {
  const container = document.getElementById("analyst-model-list");
  container.innerHTML = "";
  CONFIG.models.forEach(item => {
    const button = document.createElement("button");
    button.className = "btn";
    button.textContent = item.label;
    button.onclick = () => startAnalysis(item.key);
    container.appendChild(button);
  });
}

async function startAnalysis(modelKey) {
  sessionState.analystProvider = modelKey;
  showScreen("screen-analyzing");

  const script = sessionState.generatedScripts[sessionState.currentScriptIndex];

  try {
    const result = await analyzeResults({result_folder: sessionState.lastResultFolder, tool: script.tool, target_type: sessionState.targetType, target_name: sessionState.targetName, test_type: sessionState.testType, test_params: getCurrentTestParams(), analyst_provider: modelKey});

    sessionState.lastAnalysis = result.report;
    updateAnalysisTitle();
    document.getElementById("analysis-content").textContent = result.report_clean;
    showScreen("screen-show-analysis");
  }
  catch (error) {
    showErrorPopup("Помилка аналізу: " + error.message);
    showScreen("screen-results-saved");
    console.error(error);
  }
}

function updateAnalysisTitle() {
  const modelLabel = findLabel(CONFIG.models, sessionState.analystProvider);
  let targetWord;
  if (sessionState.targetType === "endpoint") {
    targetWord = "ендпоінту";
  }
  else {
    targetWord = "сценарію";
  }

  document.getElementById("analysis-label").innerHTML = `Аналіз результатів тестування<br>` + `${targetWord} ${sessionState.targetName} за<br>` + `допомогою моделі ${modelLabel}`;
}

function regenerateAnalysis() {
  startAnalysis(sessionState.analystProvider);
}

async function saveAnalysis() {
  try {
    await saveAnalysisReport({result_folder: sessionState.lastResultFolder, analyst_provider: sessionState.analystProvider, report: sessionState.lastAnalysis});
    showScreen("screen-analysis-saved");
  }
  catch (error) {
    showErrorPopup("Помилка збереження аналізу: " + error.message);
    console.error(error);
  }
}

function discardAnalysis() {
  showScreen("screen-analysis-not-saved");
}

async function loadSavedScriptsList() {
  try {
    const result = await fetchSavedScripts();
    renderSavedScriptsList(result.scripts);
    showScreen("screen-choose-saved-script");
  }
  catch (error) {
    showErrorPopup("Помилка завантаження: " + error.message);
    console.error(error);
  }
}

function renderSavedScriptsList(scripts) {
  const container = document.getElementById("saved-scripts-list");
  container.innerHTML = "";
  selectedSavedScript = null;

  if (scripts.length === 0) {
    container.innerHTML = '<p style="font-size:20px; color:#666; text-align:center; padding:60px 20px;">Немає збережених скриптів</p>';
    return;
  }

  scripts.forEach(script => {
    const scriptConfig = script.config;
    let targetLabel;
    if (scriptConfig.target_type === "endpoint") {
      targetLabel = findLabel(CONFIG.endpoints, scriptConfig.target_name);
    }
    else {
      targetLabel = findLabel(CONFIG.scenarios, scriptConfig.target_name);
    }
    const testTypeLabel = findLabel(CONFIG.test_types, scriptConfig.test_type);
    const toolLabel = findLabel(CONFIG.tools, script.tool);
    const modelLabel = findLabel(CONFIG.models, script.provider);

    const button = document.createElement("button");
    button.className = "saved-script-item";
    button.textContent = `${targetLabel} - ${testTypeLabel} - ${toolLabel} - ${modelLabel}`;
    button.onclick = () => {
      document.querySelectorAll("#saved-scripts-list .saved-script-item")
        .forEach(savedScriptButton => savedScriptButton.classList.remove("selected"));
      button.classList.add("selected");
      selectedSavedScript = script;
    };
    container.appendChild(button);
  });
}

function selectSavedScript(scriptInfo) {
  const scriptConfig = scriptInfo.config;

  sessionState.targetType = scriptConfig.target_type;
  sessionState.targetName = scriptConfig.target_name;
  sessionState.testType = scriptConfig.test_type;
  sessionState.customParams = scriptConfig.test_params;
  sessionState.loadSetup = "default";
  sessionState.model = scriptInfo.provider;
  sessionState.tools = [scriptInfo.tool];
  sessionState.generatedScripts = [{tool: scriptInfo.tool, model: scriptInfo.provider, savedPath: scriptInfo.script_path, code: null}];
  sessionState.currentScriptIndex = 0;

  updateSavedConfigSummary(scriptInfo);
  showScreen("screen-saved-config");
}

function updateSavedConfigSummary(scriptInfo) {
  const scriptConfig = scriptInfo.config;
  let targetLabel;
  let targetTypeLabel;

  if (scriptConfig.target_type === "endpoint") {
    targetLabel = findLabel(CONFIG.endpoints, scriptConfig.target_name);
    targetTypeLabel = "Кінцева точка";
  }
  else {
    targetLabel = findLabel(CONFIG.scenarios, scriptConfig.target_name);
    targetTypeLabel = "Сценарій";
  }

  const lines = [
    `Об'єкт: ${targetLabel}`,
    `Тип об'єкта: ${targetTypeLabel}`,
    "",
    `Тестування: ${findLabel(CONFIG.test_types, scriptConfig.test_type)}`,
    `   - Користувачів: ${scriptConfig.test_params.virtual_users}`,
    `   - Тривалість: ${formatDuration(scriptConfig.test_params.duration)}`,
    `   - Розгін: ${formatDuration(scriptConfig.test_params.ramp_up)}`,
    "",
      `Модель ШІ: ${findLabel(CONFIG.models, scriptInfo.provider)}`,
      `Інструмент: ${findLabel(CONFIG.tools, scriptInfo.tool)}`
  ];
  document.getElementById("saved-config-summary").textContent = lines.join("\n");
}

async function loadSavedResultsList() {
  try {
    const data = await fetchSavedResults();
    renderSavedResultsList(data.results);
    showScreen("screen-choose-saved-result");
  }
  catch (error) {
    showErrorPopup("Помилка завантаження: " + error.message);
    console.error(error);
  }
}

function renderSavedResultsList(results) {
  const container = document.getElementById("saved-results-list");
  container.innerHTML = "";
  selectedSavedResult = null;

  if (results.length === 0) {
    container.innerHTML = '<p style="font-size:20px; color:#666; text-align:center; padding:60px 20px;">Немає збережених результатів</p>';
    return;
  }

  results.forEach(result => {
    let targetLabel;
    if (result.target_type === "endpoint") {
      targetLabel = findLabel(CONFIG.endpoints, result.target_name);
    }
    else {
      targetLabel = findLabel(CONFIG.scenarios, result.target_name);
    }
    const testTypeLabel = findLabel(CONFIG.test_types, result.test_type);
    const toolLabel = findLabel(CONFIG.tools, result.tool);
    const modelLabel = findLabel(CONFIG.models, result.provider);
    const dateLabel = formatTimestamp(result.timestamp);

    let analyzedText = "";
    if (result.analyzed_by.length > 0) {
      const analyzedModels = result.analyzed_by
        .map(provider => findLabel(CONFIG.models, provider))
        .join(", ");

      analyzedText = ` - проаналізовано: ${analyzedModels}`;
    }

    const button = document.createElement("button");
    button.className = "saved-script-item";
    button.textContent = `${dateLabel} - ${targetLabel} - ${testTypeLabel} - ${toolLabel} - ${modelLabel}${analyzedText}`;
    button.onclick = () => {
      document.querySelectorAll("#saved-results-list .saved-script-item")
        .forEach(savedResultButton => savedResultButton.classList.remove("selected"));
      button.classList.add("selected");
      selectedSavedResult = result;
    };
    container.appendChild(button);
  });
}

function formatTimestamp(timestamp) {
  if (!timestamp || timestamp.length < 13)
    return timestamp;

  return `${timestamp.slice(0, 4)}-${timestamp.slice(4, 6)}-${timestamp.slice(6, 8)} ` + `${timestamp.slice(9, 11)}:${timestamp.slice(11, 13)}`;
}

function selectSavedResult(result) {
  sessionState.targetType = result.target_type;
  sessionState.targetName = result.target_name;
  sessionState.testType = result.test_type;
  sessionState.customParams = result.test_params;
  sessionState.model = result.provider;
  sessionState.tools = [result.tool];
  sessionState.lastResultFolder = result.result_folder;
  sessionState.generatedScripts = [{tool: result.tool, model: result.provider, savedPath: null, code: null}];
  sessionState.currentScriptIndex = 0;

  showScreen("screen-choose-analyst-model");
}

function confirmSavedScriptSelection() {
  if (!selectedSavedScript) {
    showErrorPopup("Будь ласка, оберіть тестовий сценарій зі списку.");
    return;
  }
  selectSavedScript(selectedSavedScript);
}

function confirmSavedResultSelection() {
  if (!selectedSavedResult) {
    showErrorPopup("Будь ласка, оберіть результати тестування зі списку.");
    return;
  }
  selectSavedResult(selectedSavedResult);
}

const styleEl = document.createElement("style");
styleEl.textContent =
  `.tool-btn.selected {
    background: rgba(67, 109, 4, 0.12);
    border-color: #436D04;
    font-weight: 700;
    color: #2B4802;
  }`;
document.head.appendChild(styleEl);

document.addEventListener("DOMContentLoaded", initApp);