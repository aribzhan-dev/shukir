function toggleOtherCategory(select) {
    const selectedOption = select.options[select.selectedIndex];
    const isOther = selectedOption.getAttribute('data-is-other') === 'true';
    document.getElementById('otherCategoryRow').style.display = isOther ? 'block' : 'none';
}

function showFileName() {
    const input = document.getElementById('file');
    const text = document.getElementById('uploadText');

    if (input.files.length > 0) {
        const fileNames = Array.from(input.files).map(f => f.name);
        let displayText = fileNames.join(', ');
        if (displayText.length > 50) displayText = displayText.slice(0, 47) + '...';
        text.textContent = displayText;
        text.style.color = "#222";
    } else {
        text.textContent = "{{ 'file_upload_btn'|translate:lang_code }}";
        text.style.color = "#666";
    }
}

function increaseCount() {
    const input = document.getElementById('childCount');
    input.value = parseInt(input.value || 0) + 1;
}

function decreaseCount() {
    const input = document.getElementById('childCount');
    const current = parseInt(input.value || 0);
    if (current > 0) input.value = current - 1;
}

function validateLetters(input) {
    input.value = input.value.replace(/[^A-Za-zА-Яа-яЁё\s]/g, "");
}

function validateAge(input, is_age = false) {
    let value = input.value;
    value = value.replace(/[eEpP\+\-\.]/g, "");
    value = value.replace(/[^0-9]/g, "");

    if (is_age && value.startsWith("0")) {
        value = value.replace(/^0+/, "");
    }

    if (value.length > 3) {
        value = value.slice(0, 3);
    }
    input.value = value;
}

const phoneInput = document.getElementById("phoneInput");

phoneInput.addEventListener("focus", addPrefix);
phoneInput.addEventListener("blur", removeEmptyPrefix);
phoneInput.addEventListener("input", formatPhone);
phoneInput.addEventListener("keydown", handleBackspace);

function addPrefix() {
    if (!phoneInput.value.startsWith("+7")) {
        phoneInput.value = "+7 ";
    }
}

function removeEmptyPrefix() {
    if (phoneInput.value === "+7 " || phoneInput.value === "+7") {
        phoneInput.value = "";
    }
}

function handleBackspace(e) {

    if (e.key === "Backspace") {
        const pos = phoneInput.selectionStart;
        const val = phoneInput.value;

        if (pos > 0 && /[\s\-\)\(]/.test(val[pos - 1])) {
            e.preventDefault();
            const before = val.slice(0, pos - 1);
            const after = val.slice(pos);
            phoneInput.value = before + after;
            formatPhone(true);
            phoneInput.setSelectionRange(pos - 1, pos - 1);
        }
    }
}

function formatPhone(fromBackspace = false) {
    const cursorPos = phoneInput.selectionStart;
    let value = phoneInput.value.replace(/\D/g, "");
    if (!value.startsWith("7")) value = "7" + value;

    let formatted = "+7";
    if (value.length > 1) formatted += " (" + value.substring(1, 4);
    if (value.length >= 4) formatted += ")";
    if (value.length >= 5) formatted += " " + value.substring(4, 7);
    if (value.length >= 7) formatted += "-" + value.substring(7, 9);
    if (value.length >= 9) formatted += "-" + value.substring(9, 11);

    phoneInput.value = formatted;


    if (fromBackspace) return;
    phoneInput.setSelectionRange(phoneInput.value.length, phoneInput.value.length);
}

