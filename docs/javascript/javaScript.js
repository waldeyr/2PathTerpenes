// Dynamic Rule Definitions containing values compatible with simulation.py and MØD
const RULES = [
  { id: 'r00', value: "r00 = ruleGML('sesqui_deltaCadinene_OxyReduction.gml')", name: "delta Cadinene Oxy Reduction", type: "Sesqui" },
  { id: 'r01', value: "r01 = ruleGML('sesqui_Cope01')", name: "Cope Rearrangement", type: "Sesqui" },
  { id: 'r02', value: "r02 = ruleGML('sesqui_Cope02')", name: "Cope Rearrangement 2", type: "Sesqui" },
  { id: 'r03', value: "r03 = ruleGML('sesqui_C7_protonation.gml')", name: "C7 Protonation", type: "Sesqui" },
  { id: 'r04', value: "r04 = ruleGML('sesqui_C2_protonation.gml')", name: "C2 Protonation", type: "Sesqui" },
  { id: 'r05', value: "r05 = ruleGML('sesqui_BicycloGermacrenes_C3_Oxidation.gml')", name: "BicycloGermacrenes C3 Oxidation", type: "Sesqui" },
  { id: 'r06', value: "r06 = ruleGML('sesqui_7_11_Cyc.gml')", name: "7,11 Cyclization", type: "Sesqui" },
  { id: 'r07', value: "r07 = ruleGML('sesqui_6_2_Cyc_For_Germacrenoids.gml')", name: "6,2 Cyclization for Germacrenoids", type: "Sesqui" },
  { id: 'r08', value: "r08 = ruleGML('sesqui_6_1_Cyc.gml')", name: "6,1 Cyclization", type: "Sesqui" },
  { id: 'r09', value: "r09 = ruleGML('sesqui_2_10_Cyc.gml')", name: "2,10 Cyclization", type: "Sesqui" },
  { id: 'r10', value: "r10 = ruleGML('sesqui_2_7_Cyc.gml')", name: "2,7 Cyclization", type: "Sesqui" },
  { id: 'r11', value: "r11 = ruleGML('sesqui_2_6_Cyc.gml')", name: "2,6 Cyclization", type: "Sesqui" },
  { id: 'r12', value: "r12 = ruleGML('sesqui_1_11_Cyc.gml')", name: "1,11 Cyclization", type: "Sesqui" },
  { id: 'r13', value: "r13 = ruleGML('sesqui_1_10_Cyc.gml')", name: "1,10 Cyclization", type: "Sesqui" },
  { id: 'r14', value: "r14 = ruleGML('mono_penchyl_cation_fechon.gml')", name: "Penchyl cation fechon", type: "Mono" },
  { id: 'r15', value: "r15 = ruleGML('mono_opp_loss_for_lpp_c3_alternative.gml')", name: "OPP loss for lpp C3 alternative", type: "Mono" },
  { id: 'r16', value: "r16 = ruleGML ('mono_opp_loss_for_lpp_c3.gml')", name: "OPP loss for lpp C3", type: "Mono" },
  { id: 'r17', value: "r17 = ruleGML ('mono_opp_gain_by_bornyl_cation.gml')", name: "OPP gain by bornyl cation", type: "Mono" },
  { id: 'r18', value: "r18 = ruleGML ('mono_bornyl_cation_bornyl_diphosphate.gml')", name: "Bornyl cation bornyl diphosphate", type: "Mono" },
  { id: 'r19', value: "r19 = ruleGML ('common_Wagner_Meervein.gml')", name: "Wagner Meervein", type: "Common" },
  { id: 'r20', value: "r20 = ruleGML ('mono_3_7_Cyc.gml')", name: "3,7 Cyclization", type: "Mono" },
  { id: 'r21', value: "r21 = ruleGML ('mono_2_7_Cyc.gml')", name: "2,7 Cyclization", type: "Mono" },
  { id: 'r22', value: "r22 = ruleGML ('mono_2_6_Cyc.gml')", name: "2,6 Cyclization", type: "Mono" },
  { id: 'r23', value: "r23 = ruleGML ('mono_1_8_Cyc.gml')", name: "1,8 Cyclization", type: "Mono" },
  { id: 'r24', value: "r24 = ruleGML ('common_opp_loss_alternative.gml')", name: "OPP loss alternative", type: "Common" },
  { id: 'r25', value: "r25 = ruleGML ('common_opp_loss.gml')", name: "OPP loss", type: "Common" },
  { id: 'r26', value: "r26 = ruleGML ('common_opp_gain_by_cation_alternative.gml')", name: "OPP gain by cation alternative", type: "Common" },
  { id: 'r27', value: "r27 = ruleGML ('common_opp_gain_by_cation.gml')", name: "OPP gain by cation", type: "Common" },
  { id: 'r28', value: "r28 = ruleGML ('common_h_loss.gml')", name: "H loss", type: "Common" },
  { id: 'r29', value: "r29 = ruleGML ('common_h2o_gain.gml')", name: "H2O gain", type: "Common" },
  { id: 'r30', value: "r30 = ruleGML ('common_allyls_shift.gml')", name: "Allyl shift", type: "Common" },
  { id: 'r31', value: "r31 = ruleGML ('common_1-3_H_shift.gml')", name: "1,3 H Shift", type: "Common" },
  { id: 'r32', value: "r32 = ruleGML ('common_1-2_H_shift.gml')", name: "1,2 H Shift", type: "Common" },
  { id: 'r33', value: "r33 = ruleGML ('common_1_6_Cyc.gml')", name: "1,6 Cyclization", type: "Common" }
];

// App State
let state = {
  available: RULES.map(r => r.id),
  selected: [],
  selectedAvailableIds: new Set(),
  selectedSelectedIds: new Set(),
  iterations: 1,
  searchLeft: '',
  searchRight: ''
};

// Undo/Redo History Stack
const historyStack = [];
let historyIndex = -1;

function saveHistory() {
  // Truncate future states if we performed an action after undoing
  if (historyIndex < historyStack.length - 1) {
    historyStack.splice(historyIndex + 1);
  }
  
  historyStack.push({
    available: [...state.available],
    selected: [...state.selected]
  });
  historyIndex++;
  
  updateHistoryButtons();
}

function undo() {
  if (historyIndex > 0) {
    historyIndex--;
    const prevState = historyStack[historyIndex];
    state.available = [...prevState.available];
    state.selected = [...prevState.selected];
    state.selectedAvailableIds.clear();
    state.selectedSelectedIds.clear();
    renderLists();
    updateHistoryButtons();
  }
}

function redo() {
  if (historyIndex < historyStack.length - 1) {
    historyIndex++;
    const nextState = historyStack[historyIndex];
    state.available = [...nextState.available];
    state.selected = [...nextState.selected];
    state.selectedAvailableIds.clear();
    state.selectedSelectedIds.clear();
    renderLists();
    updateHistoryButtons();
  }
}

function updateHistoryButtons() {
  const btnUndo = document.getElementById('lstview_undo');
  const btnRedo = document.getElementById('lstview_redo');
  
  if (btnUndo) {
    btnUndo.disabled = historyIndex <= 0;
    btnUndo.style.opacity = historyIndex <= 0 ? '0.4' : '1';
  }
  if (btnRedo) {
    btnRedo.disabled = historyIndex >= historyStack.length - 1;
    btnRedo.style.opacity = historyIndex >= historyStack.length - 1 ? '0.4' : '1';
  }
}

// Rendering Lists
function renderLists() {
  const listLeft = document.getElementById('available_list');
  const listRight = document.getElementById('selected_list');
  const leftCount = document.getElementById('left_counter');
  const rightCount = document.getElementById('right_counter');
  
  listLeft.innerHTML = '';
  listRight.innerHTML = '';
  
  // Left List (Available)
  const filteredAvailable = state.available.filter(id => {
    const rule = RULES.find(r => r.id === id);
    const search = state.searchLeft.toLowerCase();
    return rule.name.toLowerCase().includes(search) || rule.type.toLowerCase().includes(search);
  });
  
  filteredAvailable.forEach(id => {
    const rule = RULES.find(r => r.id === id);
    const card = createRuleCard(rule, 'available');
    if (state.selectedAvailableIds.has(id)) {
      card.classList.add('selected');
    }
    listLeft.appendChild(card);
  });
  
  leftCount.innerText = `${filteredAvailable.length} rules`;
  
  // Right List (Selected)
  const filteredSelected = state.selected.filter(id => {
    const rule = RULES.find(r => r.id === id);
    const search = state.searchRight.toLowerCase();
    return rule.name.toLowerCase().includes(search) || rule.type.toLowerCase().includes(search);
  });
  
  filteredSelected.forEach(id => {
    const rule = RULES.find(r => r.id === id);
    const card = createRuleCard(rule, 'selected');
    if (state.selectedSelectedIds.has(id)) {
      card.classList.add('selected');
    }
    listRight.appendChild(card);
  });
  
  rightCount.innerText = `${filteredSelected.length} rules`;
}

function createRuleCard(rule, listType) {
  const card = document.createElement('div');
  card.className = 'rule-card';
  card.dataset.id = rule.id;
  
  const info = document.createElement('div');
  info.className = 'rule-info';
  
  const name = document.createElement('div');
  name.className = 'rule-name';
  name.innerText = rule.name;
  
  const meta = document.createElement('div');
  meta.className = 'rule-meta';
  // Extract file name from option value
  const fileMatch = rule.value.match(/'([^']+)'/);
  const fileName = fileMatch ? fileMatch[1] : '';
  meta.innerText = fileName;
  
  info.appendChild(name);
  info.appendChild(meta);
  
  const badge = document.createElement('span');
  badge.className = `badge ${rule.type.toLowerCase()}`;
  badge.innerText = rule.type;
  
  card.appendChild(info);
  card.appendChild(badge);
  
  // Interaction Events
  card.addEventListener('click', (e) => {
    const id = rule.id;
    if (listType === 'available') {
      if (state.selectedAvailableIds.has(id)) {
        state.selectedAvailableIds.delete(id);
      } else {
        state.selectedAvailableIds.add(id);
      }
    } else {
      if (state.selectedSelectedIds.has(id)) {
        state.selectedSelectedIds.delete(id);
      } else {
        state.selectedSelectedIds.add(id);
      }
    }
    card.classList.toggle('selected');
  });
  
  card.addEventListener('dblclick', () => {
    const id = rule.id;
    if (listType === 'available') {
      state.available = state.available.filter(item => item !== id);
      state.selected.push(id);
      state.selectedAvailableIds.delete(id);
    } else {
      state.selected = state.selected.filter(item => item !== id);
      state.available.push(id);
      state.selectedSelectedIds.delete(id);
      // Keep available sorted by original order
      state.available.sort((a, b) => {
        return RULES.findIndex(r => r.id === a) - RULES.findIndex(r => r.id === b);
      });
    }
    saveHistory();
    renderLists();
  });
  
  // Hover to update preview pane
  card.addEventListener('mouseenter', () => {
    updatePreview(rule);
  });
  
  return card;
}

// Rule Details Preview
function updatePreview(rule) {
  const previewPane = document.getElementById('preview_pane');
  
  // Find rule index in RULES to compute original MØD name dynamically
  const ruleIndex = RULES.findIndex(r => r.id === rule.id);
  const fileMatch = rule.value.match(/'([^']+)'/);
  let gmlFileName = fileMatch ? fileMatch[1] : '';
  if (gmlFileName && !gmlFileName.endsWith('.gml')) {
    gmlFileName = gmlFileName + '.gml';
  }
  
  if (ruleIndex !== -1) {
    const prefix = String(5 * ruleIndex + 1).padStart(3, '0');
    // MØD name sequence pattern: prefix_r_{index}_10300000
    const fileName = `${prefix}_r_${ruleIndex}_10300000`;
    
    previewPane.innerHTML = `
      <div class="preview-content">
        <div class="preview-title">${rule.name}</div>
        <div class="preview-dpo-container">
          <div class="dpo-box">
            <span class="dpo-label">Left (Reactant)</span>
            <div class="dpo-img-wrapper">
              <img class="preview-img" src="img/${fileName}_L.svg" alt="Left" onerror="this.onerror=null; this.src='img/img2.png';">
            </div>
          </div>
          <div class="dpo-arrow" title="Context relation">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
          </div>
          <div class="dpo-box">
            <span class="dpo-label">Context</span>
            <div class="dpo-img-wrapper">
              <img class="preview-img" src="img/${fileName}_K.svg" alt="Context" onerror="this.onerror=null; this.src='img/img2.png';">
            </div>
          </div>
          <div class="dpo-arrow" title="Context relation">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </div>
          <div class="dpo-box">
            <span class="dpo-label">Right (Product)</span>
            <div class="dpo-img-wrapper">
              <img class="preview-img" src="img/${fileName}_R.svg" alt="Right" onerror="this.onerror=null; this.src='img/img2.png';">
            </div>
          </div>
        </div>
        <div class="preview-file">${gmlFileName}</div>
      </div>
    `;
  } else {
    // Show details without image as fallback
    previewPane.innerHTML = `
      <div class="preview-content">
        <div class="preview-title">${rule.name}</div>
        <div style="flex: 1; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 0.85rem; padding: 1rem;">
          No GML diagram preview available for this rule.
        </div>
      </div>
    `;
  }
}

// Reset Preview Pane
function resetPreview() {
  const previewPane = document.getElementById('preview_pane');
  previewPane.innerHTML = `
    <div class="preview-placeholder">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
      <span>Hover over any rule card to preview its details and GML reaction template structure.</span>
    </div>
  `;
}

// Transfer controls
function transferRight() {
  if (state.selectedAvailableIds.size === 0) return;
  
  state.available = state.available.filter(id => {
    if (state.selectedAvailableIds.has(id)) {
      state.selected.push(id);
      return false;
    }
    return true;
  });
  
  state.selectedAvailableIds.clear();
  saveHistory();
  renderLists();
}

function transferAllRight() {
  if (state.available.length === 0) return;
  
  state.selected = [...state.selected, ...state.available];
  state.available = [];
  state.selectedAvailableIds.clear();
  saveHistory();
  renderLists();
}

function transferLeft() {
  if (state.selectedSelectedIds.size === 0) return;
  
  state.selected = state.selected.filter(id => {
    if (state.selectedSelectedIds.has(id)) {
      state.available.push(id);
      return false;
    }
    return true;
  });
  
  // Keep available sorted by original order
  state.available.sort((a, b) => {
    return RULES.findIndex(r => r.id === a) - RULES.findIndex(r => r.id === b);
  });
  
  state.selectedSelectedIds.clear();
  saveHistory();
  renderLists();
}

function transferAllLeft() {
  if (state.selected.length === 0) return;
  
  state.available = [...RULES.map(r => r.id)];
  state.selected = [];
  state.selectedSelectedIds.clear();
  saveHistory();
  renderLists();
}

// Code compilation
function generateSimulationCode() {
  // Filter active rules in right list
  const activeRules = state.selected.map(id => RULES.find(r => r.id === id));
  
  // Format rules block
  let rulesBlock = '';
  activeRules.forEach(rule => {
    // Standardize to use Rule.fromGMLFile instead of ruleGML directly for MØD compatibility
    const fileMatch = rule.value.match(/'([^']+)'/);
    const fileName = fileMatch ? fileMatch[1] : '';
    // Format rule declaration, checking if original had .gml inside
    const hasGml = fileName.endsWith('.gml');
    const nameWithExt = hasGml ? fileName : `${fileName}.gml`;
    rulesBlock += `${rule.id} = Rule.fromGMLFile('${nameWithExt}')\n`;
  });
  
  // Compile the entire python script content
  const pythonScript = `# Helper para compatibilidade com versões antigas (0.8.0) e novas (1.0+) de MØD
try:
    from mod import Rule, LabelSettings, LabelType, LabelRelation, DG
except ImportError:
    pass

# Garantir que Rule exista e possua os métodos adequados
if 'Rule' not in globals():
    class RuleCompat:
        @staticmethod
        def fromGMLFile(*args, **kwargs):
            return ruleGML(*args, **kwargs)
    Rule = RuleCompat
else:
    if not hasattr(Rule, 'fromGMLFile') and 'ruleGML' in globals():
        Rule.fromGMLFile = staticmethod(ruleGML)

######################################
# RULES
######################################
pushFilePrefix("rules/")

${rulesBlock ? rulesBlock : '# Nenhuma regra selecionada'}
popFilePrefix()
######################################
# DEFINE LIST OF INITIAL INPUTS
######################################
eductMols = [gpp,fpp,H2O]

######################################
# ITERATIONS
######################################

strat = (addSubset(eductMols) >> repeat[${state.iterations}](inputRules))

######################################
# NETWORK GENERATION
######################################
# Compatibilidade com a restrição de LabelRelation.Unification do MØD v1.0
try:
    ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
except Exception:
    ls = LabelSettings(LabelType.Term, LabelRelation.Identity)

def overallCharge(a): return sum(int(v.charge) for v in a.vertices)
def countCycs(a): return a.numEdges - a.numVertices + 1

# Instancia o Derivation Graph com o novo build interface do MØD
try:
    # Novo build interface do MØD (v1.0.0+)
    dg = DG(graphDatabase=inputGraphs, labelSettings=ls)
    dg.build().execute(strat)
except (TypeError, AttributeError, Exception):
    # Compatibilidade com versões antigas do MØD (e.g. 0.8.0)
    if 'dgRuleComp' in globals():
        dg = dgRuleComp(inputGraphs, strat, ls)
    elif 'DG' in globals():
        dg = DG(inputGraphs, strat, ls)
    else:
        try:
            dg = DG(inputGraphs, strat, ls)
        except Exception:
            dg = dgRuleComp(inputGraphs, strat, ls)
    dg.calc()
`;
  
  return pythonScript;
}

// Download function
function downloadFile(filename, text) {
  const element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);
  element.style.display = 'none';
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

// Clipboard copying utility
function copyToClipboard(text, buttonId, successText) {
  navigator.clipboard.writeText(text).then(() => {
    const button = document.getElementById(buttonId);
    const originalHTML = button.innerHTML;
    
    // Success feedback
    button.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
        <polyline points="20 6 9 17 4 12" />
      </svg>
      <span>Copied!</span>
    `;
    button.style.borderColor = 'var(--primary)';
    button.style.color = 'var(--primary)';
    
    setTimeout(() => {
      button.innerHTML = originalHTML;
      button.style.borderColor = '';
      button.style.color = '';
    }, 2000);
  }).catch(err => {
    console.error('Failed to copy: ', err);
  });
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  // Bind searches
  const searchL = document.getElementById('search_left');
  const searchR = document.getElementById('search_right');
  
  if (searchL) {
    searchL.addEventListener('input', (e) => {
      state.searchLeft = e.target.value;
      renderLists();
    });
  }
  
  if (searchR) {
    searchR.addEventListener('input', (e) => {
      state.searchRight = e.target.value;
      renderLists();
    });
  }
  
  // Bind Transfer Buttons
  document.getElementById('lstview_rightSelected')?.addEventListener('click', transferRight);
  document.getElementById('lstview_rightAll')?.addEventListener('click', transferAllRight);
  document.getElementById('lstview_leftSelected')?.addEventListener('click', transferLeft);
  document.getElementById('lstview_leftAll')?.addEventListener('click', transferAllLeft);
  
  // Undo / Redo
  document.getElementById('lstview_undo')?.addEventListener('click', undo);
  document.getElementById('lstview_redo')?.addEventListener('click', redo);
  
  // Iterations Selector Counter Buttons
  const btnDec = document.getElementById('btn_iter_dec');
  const btnInc = document.getElementById('btn_iter_inc');
  const displayVal = document.getElementById('iterations_val');
  
  if (btnDec && btnInc && displayVal) {
    btnDec.addEventListener('click', () => {
      if (state.iterations > 1) {
        state.iterations--;
        displayVal.innerText = state.iterations;
      }
    });
    
    btnInc.addEventListener('click', () => {
      if (state.iterations < 7) {
        state.iterations++;
        displayVal.innerText = state.iterations;
      }
    });
  }
  
  // Modal Interactions
  const modalOverlay = document.getElementById('modal_overlay');
  const btnGenerate = document.getElementById('btn_generate');
  const btnCloseModal = document.getElementById('btn_close_modal');
  const btnDownloadCode = document.getElementById('btn_download_code');
  const btnCopyCode = document.getElementById('btn_copy_code');
  const editorCode = document.getElementById('editor_code');
  
  if (btnGenerate && modalOverlay && editorCode) {
    btnGenerate.addEventListener('click', () => {
      const code = generateSimulationCode();
      
      // Populate lines with line numbers for styling inside editor
      const lines = code.split('\n');
      editorCode.innerHTML = '';
      lines.forEach((line, index) => {
        const lineSpan = document.createElement('span');
        lineSpan.style.display = 'block';
        
        const numSpan = document.createElement('span');
        numSpan.style.color = '#4b5563'; // gray-600 line number
        numSpan.style.marginRight = '1.25rem';
        numSpan.style.userSelect = 'none';
        numSpan.style.textAlign = 'right';
        numSpan.style.display = 'inline-block';
        numSpan.style.width = '2rem';
        numSpan.innerText = index + 1;
        
        const codeText = document.createTextNode(line || ' ');
        
        lineSpan.appendChild(numSpan);
        lineSpan.appendChild(codeText);
        editorCode.appendChild(lineSpan);
      });
      
      modalOverlay.classList.add('open');
    });
  }
  
  if (btnCloseModal && modalOverlay) {
    btnCloseModal.addEventListener('click', () => {
      modalOverlay.classList.remove('open');
    });
    // Close on overlay backdrop click
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) {
        modalOverlay.classList.remove('open');
      }
    });
  }
  
  if (btnDownloadCode) {
    btnDownloadCode.addEventListener('click', () => {
      const code = generateSimulationCode();
      downloadFile('simulation.py', code);
    });
  }
  
  if (btnCopyCode) {
    btnCopyCode.addEventListener('click', () => {
      const code = generateSimulationCode();
      copyToClipboard(code, 'btn_copy_code', 'Copied!');
    });
  }
  
  // Setup click copy for Terminal Commands
  const copyDockerBtn = document.getElementById('btn_copy_docker');
  const dockerCmdText = `docker run --rm --volume $(pwd):/home/shared/ --workdir /home/shared/ waldeyr/mod_v0.8.0:v1.0 /home/mod-v0.8.0/bin/mod -f /home/shared/molecules.py -f /home/shared/simulation.py -f /home/shared/printer.py`;
  
  if (copyDockerBtn) {
    copyDockerBtn.addEventListener('click', () => {
      copyToClipboard(dockerCmdText, 'btn_copy_docker', 'Copied!');
    });
  }
  
  const copyDockerNewBtn = document.getElementById('btn_copy_docker_new');
  const dockerNewCmdText = `docker build -t 2path-terpenes-mod:latest . && docker run --rm --volume $(pwd):/home/shared/ --workdir /home/shared/ 2path-terpenes-mod:latest -f /home/shared/molecules.py -f /home/shared/simulation.py -f /home/shared/printer.py`;
  
  if (copyDockerNewBtn) {
    copyDockerNewBtn.addEventListener('click', () => {
      copyToClipboard(dockerNewCmdText, 'btn_copy_docker_new', 'Copied!');
    });
  }
  
  const copyLocalBtn = document.getElementById('btn_copy_local');
  const localCmdText = `PATH_TO_MOD/mod -f molecules.py -f simulation.py -f printer.py`;
  
  if (copyLocalBtn) {
    copyLocalBtn.addEventListener('click', () => {
      copyToClipboard(localCmdText, 'btn_copy_local', 'Copied!');
    });
  }
  
  // Set up mouseleave listener on lists to reset preview
  document.getElementById('available_list')?.addEventListener('mouseleave', resetPreview);
  
  // Save Initial History State and Render
  saveHistory();
  renderLists();
  resetPreview();
});
