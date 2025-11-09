function toggleOtherCategory(select) {
    const selectedOption = select.options[select.selectedIndex];
    const isOther = selectedOption.getAttribute('data-is-other') === 'true';
    document.getElementById('otherCategoryRow').style.display = isOther ? 'block' : 'none';
}

function validateFileUpload(event) {
  const fileInput = document.getElementById("file");
  const uploadBox = document.querySelector(".upload-box");
  const uploadText = document.getElementById("uploadText");
  const uploadError = document.getElementById("uploadError");

  if (!fileInput.files.length) {
    event.preventDefault();
    uploadBox.style.borderColor = "#e53e3e";
    uploadBox.style.backgroundColor = "#fff5f5";
    uploadText.style.color = "#e53e3e";
    uploadError.style.display = "block";
    return false;
  } else {
    uploadBox.style.borderColor = "#6ad48c";
    uploadBox.style.backgroundColor = "#f7fff9";
    uploadText.style.color = "#2f855a";
    uploadError.style.display = "none";
    return true;
  }
}

function showFileName() {
  const fileInput = document.getElementById("file");
  const uploadText = document.getElementById("uploadText");
  const uploadBox = document.querySelector(".upload-box");
  const uploadError = document.getElementById("uploadError");

  if (fileInput.files.length > 0) {
    uploadText.textContent = fileInput.files.length === 1
      ? fileInput.files[0].name
      : `${fileInput.files.length} файл танланди`;
    uploadText.style.color = "#2f855a";
    uploadBox.style.borderColor = "#6ad48c";
    uploadBox.style.backgroundColor = "#f7fff9";
    uploadError.style.display = "none";
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

