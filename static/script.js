// Predefined examples
const examples = {
    basic: {
        chemicals: [
            { name: "HCl", hazard: "3" },
            { name: "NaOH", hazard: "2" },
            { name: "Ethanol", hazard: "2" },
            { name: "Acetone", hazard: "2" },
            { name: "H2O2", hazard: "3" }
        ],
        incompatibilities: [
            { chem1: "HCl", chem2: "NaOH", severity: "3" },
            { chem1: "HCl", chem2: "Ethanol", severity: "1" },
            { chem1: "NaOH", chem2: "Ethanol", severity: "1" },
            { chem1: "Ethanol", chem2: "H2O2", severity: "3" },
            { chem1: "Acetone", chem2: "H2O2", severity: "3" }
        ]
    },
    industrial: {
        chemicals: [
            { name: "HCl", hazard: "3" },
            { name: "NaOH", hazard: "2" },
            { name: "Ethanol", hazard: "2" },
            { name: "Acetone", hazard: "2" },
            { name: "H2O2", hazard: "3" },
            { name: "NaCN", hazard: "3" },
            { name: "KMnO4", hazard: "2" },
            { name: "CH3COOH", hazard: "2" },
            { name: "NH3", hazard: "2" },
            { name: "C6H6", hazard: "3" }
        ],
        incompatibilities: [
            { chem1: "HCl", chem2: "NaOH", severity: "3" },
            { chem1: "HCl", chem2: "Ethanol", severity: "1" },
            { chem1: "NaOH", chem2: "Ethanol", severity: "1" },
            { chem1: "Ethanol", chem2: "H2O2", severity: "3" },
            { chem1: "Acetone", chem2: "H2O2", severity: "3" },
            { chem1: "NaCN", chem2: "HCl", severity: "3" },
            { chem1: "KMnO4", chem2: "Ethanol", severity: "2" },
            { chem1: "KMnO4", chem2: "Acetone", severity: "2" },
            { chem1: "CH3COOH", chem2: "NaOH", severity: "2" },
            { chem1: "NH3", chem2: "HCl", severity: "2" },
            { chem1: "C6H6", chem2: "H2O2", severity: "3" },
            { chem1: "C6H6", chem2: "KMnO4", severity: "2" }
        ]
    },
    academic: {
        chemicals: [
            { name: "H2SO4", hazard: "3" },
            { name: "NaOH", hazard: "2" },
            { name: "Methanol", hazard: "2" },
            { name: "Chloroform", hazard: "2" },
            { name: "Nitric Acid", hazard: "3" },
            { name: "Silver Nitrate", hazard: "2" }
        ],
        incompatibilities: [
            { chem1: "H2SO4", chem2: "NaOH", severity: "3" },
            { chem1: "H2SO4", chem2: "Methanol", severity: "2" },
            { chem1: "NaOH", chem2: "Chloroform", severity: "2" },
            { chem1: "Methanol", chem2: "Nitric Acid", severity: "3" },
            { chem1: "Chloroform", chem2: "Silver Nitrate", severity: "1" }
        ]
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeChemicalList();
    initializeIncompatibilityList();
    setupEventListeners();
});

function initializeChemicalList() {
    // Initial chemical is already in HTML, just update selects
    updateChemicalSelects();
}

function initializeIncompatibilityList() {
    updateChemicalSelects();
}

function setupEventListeners() {
    // Add chemical button
    document.getElementById('add-chemical').addEventListener('click', addChemical);
    
    // Add incompatibility button
    document.getElementById('add-incompatibility').addEventListener('click', addIncompatibility);
    
    // Optimize button
    document.getElementById('optimize-btn').addEventListener('click', optimizeStorage);
    
    // Example buttons
    document.querySelectorAll('.load-example').forEach(btn => {
        btn.addEventListener('click', function() {
            loadExample(this.dataset.example);
        });
    });
}

function addChemical() {
    const chemicalsList = document.getElementById('chemicals-list');
    const newChemical = document.createElement('div');
    newChemical.className = 'chemical-item mb-2';
    newChemical.innerHTML = `
        <div class="row">
            <div class="col-6">
                <input type="text" class="form-control chemical-name" placeholder="Chemical Name">
            </div>
            <div class="col-4">
                <select class="form-select hazard-level">
                    <option value="1">Low Hazard</option>
                    <option value="2" selected>Medium Hazard</option>
                    <option value="3">High Hazard</option>
                </select>
            </div>
            <div class="col-2">
                <button class="btn btn-danger btn-sm remove-chemical"><i class="fas fa-times"></i></button>
            </div>
        </div>
    `;
    chemicalsList.appendChild(newChemical);
    
    // Add event listener to remove button
    newChemical.querySelector('.remove-chemical').addEventListener('click', function() {
        chemicalsList.removeChild(newChemical);
        updateChemicalSelects();
    });
    
    updateChemicalSelects();
}

function addIncompatibility() {
    const incompatibilitiesList = document.getElementById('incompatibilities-list');
    const newIncompatibility = document.createElement('div');
    newIncompatibility.className = 'incompatibility-item mb-2';
    newIncompatibility.innerHTML = `
        <div class="row">
            <div class="col-5">
                <select class="form-select chem1"></select>
            </div>
            <div class="col-5">
                <select class="form-select chem2"></select>
            </div>
            <div class="col-2">
                <button class="btn btn-danger btn-sm remove-incompatibility"><i class="fas fa-times"></i></button>
            </div>
        </div>
        <div class="row mt-1">
            <div class="col-12">
                <select class="form-select severity">
                    <option value="1">Low Severity</option>
                    <option value="2" selected>Medium Severity</option>
                    <option value="3">High Severity</option>
                </select>
            </div>
        </div>
    `;
    incompatibilitiesList.appendChild(newIncompatibility);
    
    // Update selects for the new incompatibility
    updateChemicalSelects();
    
    // Add event listener to remove button
    newIncompatibility.querySelector('.remove-incompatibility').addEventListener('click', function() {
        incompatibilitiesList.removeChild(newIncompatibility);
    });
}

function updateChemicalSelects() {
    const chemicalNames = Array.from(document.querySelectorAll('.chemical-name'))
        .map(input => input.value)
        .filter(name => name.trim() !== '');
    
    document.querySelectorAll('.chem1, .chem2').forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '';
        
        chemicalNames.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
           