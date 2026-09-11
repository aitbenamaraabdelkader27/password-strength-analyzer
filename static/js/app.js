"use strict";

const select = (selector) => document.querySelector(selector);
const selectAll = (selector) => [...document.querySelectorAll(selector)];

const mainTabs = selectAll("[data-tab]");
const mainPanels = selectAll("[data-panel]");
const form = select("#password-form");
const passwordInput = select("#password");
const analyzeButton = select("#analyze-button");
const results = select("#results");
const errorMessage = select("#form-error");
const personalizedForm = select("#personalized-form");
const personalPassword = select("#personal-password");
const personalizedButton = select("#personalized-button");
const personalizedError = select("#personalized-error");
const generatorForm = select("#generator-form");
const generateButton = select("#generate-button");
const generatorError = select("#generator-error");
let generatorMode = "random";
let generatedValue = "";

const strengthClasses = {
  "Very Weak": "very-weak",
  Weak: "weak",
  Medium: "medium",
  Strong: "strong",
  "Very Strong": "very-strong",
};

function activateMainTab(name, focusTab = false) {
  mainTabs.forEach((tab) => {
    const active = tab.dataset.tab === name;
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && focusTab) tab.focus();
  });
  mainPanels.forEach((panel) => {
    panel.hidden = panel.dataset.panel !== name;
  });
}

mainTabs.forEach((tab, index) => {
  tab.addEventListener("click", () => activateMainTab(tab.dataset.tab));
  tab.addEventListener("keydown", (event) => {
    let nextIndex;
    if (event.key === "ArrowRight") nextIndex = (index + 1) % mainTabs.length;
    if (event.key === "ArrowLeft") nextIndex = (index - 1 + mainTabs.length) % mainTabs.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = mainTabs.length - 1;
    if (nextIndex !== undefined) {
      event.preventDefault();
      activateMainTab(mainTabs[nextIndex].dataset.tab, true);
    }
  });
});

selectAll(".password-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.dataset.target);
    const willShow = input.type === "password";
    input.type = willShow ? "text" : "password";
    button.setAttribute("aria-pressed", String(willShow));
    button.setAttribute("aria-label", willShow ? "Hide password" : "Show password");
    button.title = willShow ? "Hide password" : "Show password";
    input.focus();
  });
});

function resetPasswordVisibility(input) {
  input.type = "password";
  const button = select(`.password-toggle[data-target="${input.id}"]`);
  button.setAttribute("aria-pressed", "false");
  button.setAttribute("aria-label", "Show password");
  button.title = "Show password";
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The request could not be completed.");
  return data;
}

function setButtonLoading(button, loading) {
  button.classList.toggle("is-loading", loading);
  button.disabled = loading;
  button.setAttribute("aria-busy", String(loading));
}

passwordInput.addEventListener("input", () => {
  analyzeButton.disabled = passwordInput.value.length === 0;
  errorMessage.textContent = "";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!passwordInput.value) {
    errorMessage.textContent = "Enter a password to run the analysis.";
    passwordInput.focus();
    return;
  }
  const password = passwordInput.value;
  setButtonLoading(analyzeButton, true);
  passwordInput.disabled = true;
  errorMessage.textContent = "";
  try {
    renderTechnicalResults(await postJson("/api/analyze", { password }));
  } catch (error) {
    errorMessage.textContent = error instanceof Error ? error.message : "The server could not be reached.";
  } finally {
    passwordInput.value = "";
    passwordInput.disabled = false;
    resetPasswordVisibility(passwordInput);
    setButtonLoading(analyzeButton, false);
    analyzeButton.disabled = true;
  }
});

function renderTechnicalResults(data) {
  const score = Math.max(0, Math.min(100, Number(data.score)));
  results.hidden = false;
  results.dataset.tone = strengthClasses[data.strength] || "very-weak";
  select("#score-value").textContent = String(score);
  select("#strength-value").textContent = data.strength;
  select("#entropy-value").textContent = `Estimated entropy: ${Number(data.entropy).toFixed(1)} bits`;
  select("#score-ring").style.setProperty("--score", score);
  select("#score-ring").setAttribute("aria-label", `Password score: ${score} out of 100`);
  select("#score-bar").style.width = `${score}%`;
  selectAll("#results [data-check]").forEach((item) => {
    const passed = Boolean(data.checks[item.dataset.check]);
    item.classList.toggle("passed", passed);
    item.classList.toggle("failed", !passed);
    item.querySelector(".status-icon").textContent = passed ? "✓" : "×";
  });
  renderList(select("#issues-list"), data.issues.length ? data.issues : ["No obvious predictable patterns detected."], data.issues.length ? "warning" : "clear");
  renderList(select("#recommendations-list"), data.recommendations, "advice");
  results.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

personalPassword.addEventListener("input", () => {
  personalizedButton.disabled = personalPassword.value.length === 0;
  personalizedError.textContent = "";
});

personalizedForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!personalPassword.value) {
    personalizedError.textContent = "Enter a password to assess.";
    personalPassword.focus();
    return;
  }
  const birthYear = select("#birth-year").value.trim();
  if (birthYear && !/^(?:19|20)\d{2}$/.test(birthYear)) {
    personalizedError.textContent = "Enter a birth year between 1900 and 2099.";
    select("#birth-year").focus();
    return;
  }
  const keywords = select("#personal-keywords").value.split(",").map((item) => item.trim()).filter(Boolean);
  if (keywords.length > 5 || keywords.some((item) => item.length > 32)) {
    personalizedError.textContent = "Use no more than 5 keywords of 32 characters or fewer.";
    select("#personal-keywords").focus();
    return;
  }
  const payload = {
    password: personalPassword.value,
    profile: {
      first_name: select("#first-name").value,
      last_name: select("#last-name").value,
      username: select("#username").value,
      birth_year: birthYear,
      keywords,
    },
  };
  setButtonLoading(personalizedButton, true);
  personalizedError.textContent = "";
  try {
    renderPersonalizedResults(await postJson("/api/analyze/personalized", payload));
  } catch (error) {
    personalizedError.textContent = error instanceof Error ? error.message : "The server could not be reached.";
  } finally {
    personalizedForm.reset();
    resetPasswordVisibility(personalPassword);
    setButtonLoading(personalizedButton, false);
    personalizedButton.disabled = true;
  }
});

function renderPersonalizedResults(data) {
  const personal = data.personal_predictability;
  select("#personal-technical-score").textContent = `${data.technical.score} / 100`;
  select("#personal-technical-label").textContent = data.technical.strength;
  select("#personal-risk").textContent = personal.risk;
  select("#personal-risk").dataset.risk = personal.risk.toLowerCase();
  select("#personal-penalty").textContent = personal.penalty ? `−${personal.penalty} personal-risk points` : "No personal-risk penalty";
  select("#personalized-score").textContent = `${data.personalized_score} / 100`;
  renderList(select("#personal-patterns"), personal.detected_patterns.length ? personal.detected_patterns : ["No obvious matches to the supplied profile."], personal.detected_patterns.length ? "warning" : "clear");
  renderList(select("#personal-penalties"), personal.penalty_explanations.length ? personal.penalty_explanations : ["No score adjustment applied."], personal.penalty_explanations.length ? "warning" : "clear");
  renderList(select("#personal-recommendations"), personal.recommendations, "advice");
  select("#personalized-results").hidden = false;
  select("#personalized-results").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

const generatorTabs = selectAll("[data-generator-mode]");
generatorTabs.forEach((button) => {
  button.addEventListener("click", () => setGeneratorMode(button.dataset.generatorMode));
  button.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
    event.preventDefault();
    setGeneratorMode(generatorMode === "random" ? "passphrase" : "random", true);
  });
});

function setGeneratorMode(mode, focusTab = false) {
  generatorMode = mode;
  generatorTabs.forEach((button) => {
    const active = button.dataset.generatorMode === mode;
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
    if (active && focusTab) button.focus();
  });
  select("#random-options").hidden = mode !== "random";
  select("#passphrase-options").hidden = mode !== "passphrase";
  select("#generate-button .button-label").textContent = mode === "random" ? "Generate secure password" : "Generate memorable passphrase";
  generatorError.textContent = "";
}

select("#random-length").addEventListener("input", (event) => {
  select("#random-length-value").textContent = event.target.value;
});

generatorForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const isRandom = generatorMode === "random";
  const payload = isRandom ? {
    length: Number(select("#random-length").value),
    uppercase: select("#use-uppercase").checked,
    lowercase: select("#use-lowercase").checked,
    digits: select("#use-digits").checked,
    symbols: select("#use-symbols").checked,
  } : {
    word_count: Number(select("#word-count").value),
    separator: select("#separator").value,
    capitalize: select("#capitalize").checked,
    include_number: select("#include-number").checked,
    include_symbol: select("#include-symbol").checked,
  };
  setButtonLoading(generateButton, true);
  generatorError.textContent = "";
  try {
    renderGenerated(await postJson(isRandom ? "/api/generate/random" : "/api/generate/passphrase", payload), isRandom);
  } catch (error) {
    generatorError.textContent = error instanceof Error ? error.message : "The server could not be reached.";
  } finally {
    setButtonLoading(generateButton, false);
  }
});

function renderGenerated(data, isRandom) {
  generatedValue = data.password;
  select("#generated-password").textContent = generatedValue;
  select("#generated-score").textContent = data.analysis.score;
  select("#generated-strength").textContent = data.analysis.strength;
  select("#generated-entropy").textContent = `${Number(data.analysis.entropy).toFixed(1)} bits`;
  select("#generation-entropy").textContent = isRandom
    ? `Generation estimate: ${Number(data.selection_entropy).toFixed(1)} bits from secure random character selection.`
    : `Generation estimate: ${Number(data.selection_entropy).toFixed(1)} bits from a ${data.word_pool_size}-word pool and enabled random additions.`;
  renderList(select("#generated-issues"), data.analysis.issues.length ? data.analysis.issues : ["No obvious predictable patterns detected."], data.analysis.issues.length ? "warning" : "clear");
  select("#generated-results").hidden = false;
  select("#generated-results").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

select("#regenerate").addEventListener("click", () => generatorForm.requestSubmit());
select("#copy-generated").addEventListener("click", async () => {
  const status = select("#copy-status");
  try {
    await navigator.clipboard.writeText(generatedValue);
    status.textContent = "Generated password copied to the clipboard.";
    select("#copy-generated").textContent = "Copied";
    window.setTimeout(() => { select("#copy-generated").textContent = "Copy"; }, 1600);
  } catch {
    status.textContent = "Clipboard access was unavailable. Select and copy the generated password manually.";
    generatorError.textContent = status.textContent;
  }
});
select("#analyze-generated").addEventListener("click", () => {
  passwordInput.value = generatedValue;
  analyzeButton.disabled = false;
  activateMainTab("analyze");
  form.requestSubmit();
});

function renderList(container, items, variant) {
  container.replaceChildren();
  items.forEach((item) => {
    const listItem = document.createElement("li");
    const icon = document.createElement("span");
    icon.className = `finding-icon ${variant}`;
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = variant === "warning" ? "!" : variant === "clear" ? "✓" : "→";
    listItem.append(icon, document.createTextNode(item));
    container.append(listItem);
  });
}
