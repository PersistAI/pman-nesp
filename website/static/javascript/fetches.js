let respContainer = document.getElementById("response-container");

function display(s, className = "") {
  let span = document.createElement("span");
  span.textContent = s;
  respContainer.appendChild(span);
  if (className) {
    span.classList.add(className);
  }

  respContainer.appendChild(span);
}

async function fetchPOST(endpoint, data) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.text();
}

async function push(args) {
  const data = { args: args };
  return fetchPOST("/pman/push", data);
}

async function pull(args) {
  const data = { args: args };
  return fetchPOST("/pman/pull", data);
}

function disableButtons(){
  let btns = document.querySelectorAll('button');
  btns.forEach(button => {
    button.disabled = true;
  });
}

function enableButtons(){
  let btns = document.querySelectorAll('button');
  btns.forEach(button => {
    button.disabled = false;
  });
}
